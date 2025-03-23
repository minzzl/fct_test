import argparse
import time
import os
import platform
import pandas as pd
import pexpect
import threading
import subprocess
import yaml
from datetime import datetime
import platform
import subprocess

# 상수 정의
CHECK_INTERVAL = 1  # 1초마다 체크
SSH_TIMEOUT = 30
SSH_PROMPT = r'\[root@webOSNano-unofficial ~\]#'
EXCEL_FILE = 'local_file.xlsx'

# 현재 행 인덱스를 저장할 변수
current_row_index = 0
connection_status = False  # 연결 상태를 저장할 변수
lock = threading.Lock()  # 스레드 안전을 위한 락

def find_next_row_index():
    """Find the next row index where 'Check' is empty or 'X'."""
    global current_row_index
    try:
        df = pd.read_excel(EXCEL_FILE)
        for index, row in df.iterrows():
            if pd.isna(row['Check']) or row['Check'] == 'X':
                current_row_index = index
                return True
        print("[x] No available rows found.")
        return False
    except Exception as e:
        print(f"[x] Failed to find next row index: {e}")
        return False


def check_ssh_connection(host, username, password="allnewb2b^^"):
   """SSH 연결을 확인하며 비밀번호 입력을 추가 (Windows/Linux 구분)"""
   print(f"[...] Checking SSH connection to {host} as {username}")
   if platform.system() == "Windows":
       ssh_command = f"ssh -o StrictHostKeyChecking=no {username}@{host} echo connected"
       process = subprocess.Popen(ssh_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
       stdout, stderr = process.communicate(input=f"{password}\n")
       if "connected" in stdout:
           print("[v] SSH Connection OK")
           return True
       else:
           print("[x] SSH Connection FAIL")
           return False
   else:
       try:
           ssh_command = f"ssh -o StrictHostKeyChecking=no {username}@{host}"
           child = pexpect.spawn(ssh_command, timeout=SSH_TIMEOUT)
           index = child.expect(["password:", pexpect.EOF, pexpect.TIMEOUT])
           if index == 0:
               child.sendline(password)
               child.expect("#")
               child.sendline("exit")
               print("[v] SSH Connection OK")
               return True
           else:
               print("[x] SSH Connection FAIL")
               return False
       except Exception as e:
           print(f"[x] SSH Connection FAIL ({e})")
           return False


def read_sn_mac_from_file():
    """엑셀 파일에서 SN과 MAC 주소를 읽습니다."""
    try:
        df = pd.read_excel(EXCEL_FILE)
        if df.empty or current_row_index >= len(df):
            print("[x] Excel FAIL (No more rows to read)")
            return False, None, None
        
        serial_number = df.at[current_row_index, 'Serial Number']
        mac_address = df.at[current_row_index, 'Eth Address']
        serial_number = str(serial_number).strip()
        mac_address = str(mac_address).strip()
        return True, serial_number, mac_address
    except Exception as e:
        print(f"[x] Excel read FAIL ({e})")
        return False, None, None


def execute_ssh_command(host, username, command, password="allnewb2b^^"):
    """비밀번호 입력 후 SSH 명령 실행 (Windows/Linux 구분)"""
    # print(f"[DEBUG] Executing SSH command on {host} as {username}")
    # print(f"[DEBUG] Command: {command}")

    if platform.system() == "Windows":
        ssh_command = f"ssh -o StrictHostKeyChecking=no {username}@{host} {command}"
        process = subprocess.Popen(ssh_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(input=f"{password}\n")
        # print(f"[DEBUG] Process stdout: {stdout.strip()}")
        # print(f"[DEBUG] Process stderr: {stderr.strip()}")
        return stdout.strip() if stdout else None
    else:
        try:
            # SSH 명령어를 한 번에 실행
            ssh_command = f"ssh -o StrictHostKeyChecking=no {username}@{host} '{command}'"
            # print(f"[DEBUG] Linux SSH command: {ssh_command}")
            child = pexpect.spawn(ssh_command, timeout=SSH_TIMEOUT)
            index = child.expect(["password:", pexpect.EOF, pexpect.TIMEOUT])
            if index == 0:
                # print("[DEBUG] Password prompt received, sending password...")
                child.sendline(password)
                child.expect(pexpect.EOF)  # 명령어 실행 후 EOF를 기다림
                output = child.before.decode("utf-8").strip()
                # print(f"[DEBUG] Command output: {output}")
                return output
            return None
        except Exception as e:
            print(f"[x] SSH execute command error: {e}")
            return None

def write_sn_mac_to_board(sn, mac, host, username, password="allnewb2b^^"):
   
    """보드에 SN과 MAC 주소를 SSH를 통해 쓰고 확인 (Windows/Linux 구분)"""
    print(f"[...] Writing SN ({sn}) and MAC ({mac}) to board {host}")

    if platform.system() == "Windows":
        write_command = f"echo {sn} > /persist/serial_number && /usr/bin/misc-util ETH_MAC {mac} && echo PACPIA000.AKM > /persist/model_number"
        check_command = f"cat /persist/serial_number && /usr/bin/misc-util ETH_MAC"
        ssh_command = f"ssh -o StrictHostKeyChecking=no {username}@{host} \"{write_command}\""
        process = subprocess.Popen(ssh_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        process.communicate(input=f"{password}\n")
        ssh_command_check = f"ssh -o StrictHostKeyChecking=no {username}@{host} \"{check_command}\""
        process_check = subprocess.Popen(ssh_command_check, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, _ = process_check.communicate(input=f"{password}\n")

    else:
        write_command = f"echo {sn} > /persist/serial_number && /usr/bin/misc-util ETH_MAC {mac}"
        check_command = "cat /persist/serial_number && /usr/bin/misc-util ETH_MAC && cat /persist/model_number"
        execute_ssh_command(host, username, write_command)
        stdout = execute_ssh_command(host, username, check_command)

    if stdout:
        lines = stdout.split("\n")
        written_sn = lines[0].strip()
        written_mac = lines[1].strip() if len(lines) > 1 else None
        written_model = lines[2].strip() if len(lines) > 2 else None
        if written_sn == sn and written_mac == mac and written_model == "PACPIA000.AKM":
            print("[v] Serial Number write OK")
            print("[v] Eth MAC Addr write OK")
            print("[v] Model Number write OK")
            return True
        else:
            print("[x] Serial Number or MAC write FAIL")
            print("Intended ------------------------- actual")
            print(f"Serial number : {sn} ------------ {written_sn}")
            print(f"eth mac address : {mac} -------- {written_mac}")
            print(f"Model Number : PACPIA000.AKM ---- {written_model}")
            return False
    return False

def update_check_column():
    """엑셀 파일의 'Check' 열을 업데이트합니다."""
    global current_row_index
    try:
        df = pd.read_excel(EXCEL_FILE, dtype={'Check': str})
        if df.empty:
            print("[v] Execl Check FAIL (Empty)")
            return False
        
        df.at[current_row_index, 'Check'] = 'O'
        df.to_excel(EXCEL_FILE, index=False)
        print("[v] Execl Check OK")
        return True
    except Exception as e:

        print(f"[v] Execl Check FAIL ({e})")
        return False

"""
def start_fct_test(hostIp):
    ssh_command = f"ssh -o StrictHostKeyChecking=no root@{hostIp} python3 /lg_rw/fct_test/test_start_dq1.py "
    
    try:
        child = pexpect.spawn(ssh_command)
        child.interact()

    except Exception as e:
        print(f"Err: {e}")

"""

def start_fct_test(hostIp, username, password="allnewb2b^^"):
    """FCT 테스트 시작을 위해 SSH 접속 및 실행 (Windows/Linux 구분)"""
    print("[...] Starting FCT Test")
    ssh_command = f"ssh -o StrictHostKeyChecking=no {username}@{hostIp} python3 /lg_rw/fct_test/test_start_dq1.py"

    if platform.system() == "Windows":
        process = subprocess.Popen(ssh_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(input=f"{password}\n")
        print(stdout)
        return True
    else:
        try:
            child = pexpect.spawn(ssh_command, timeout=SSH_TIMEOUT)
            index = child.expect(["password:", pexpect.EOF, pexpect.TIMEOUT])
            if index == 0:
                print("[DEBUG] Password prompt received, sending password...")
                child.sendline(password)

            # 명령어 실행 후 실시간으로 출력 읽기
            while True:
                try:
                    # 다음 출력이 있을 때까지 대기
                    output = child.readline().decode("utf-8", errors="ignore").strip()
                    if output:
                        print(output)
                        if 'y/n' in output:
                            user_input = input('Enter y or n: ')
                            child.sendline(user_input)
                except pexpect.EOF:
                    break
                except pexpect.TIMEOUT:
                    continue

            print("[v] FCT Test Completed")
            return True
        except Exception as e:
            print(f"Err: {e}")
            return False

def remove_known_host(known_hosts_path, hostIp):
    if os.path.exists(known_hosts_path):
        with open(known_hosts_path, 'r') as file:
            known_hosts = file.readlines()
        
        # 호스트가 known_hosts에 존재하는지 확인
        host_found = any(hostIp in line for line in known_hosts)
        
        if host_found:
            print(f"[log] Removing {hostIp} from known_hosts...")
            subprocess.run(f"ssh-keygen -R {hostIp}", shell=True)
        return True
        
    else:
        print(f"[log] {known_hosts_path} does not exist.")
        return False



def send_time_now(username, hostIp, password="allnewb2b^^"):
    """현재 시간을 보드에 전송"""
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[...] Sending current time ({current_time}) to {hostIp}")
    if platform.system() == "Windows":
        write_command = f"echo {current_time} > /home/root/current_time"
        read_command = "cat /home/root/current_time"
        ssh_command = f"ssh -o StrictHostKeyChecking=no {username}@{hostIp} \"{write_command}\""
        subprocess.run(ssh_command, shell=True, input=f"{password}\n", text=True)
        ssh_command_check = f"ssh -o StrictHostKeyChecking=no {username}@{hostIp} \"{read_command}\""
        process_check = subprocess.Popen(ssh_command_check, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, _ = process_check.communicate(input=f"{password}\n")
    else:
       write_command = f"echo {current_time} > /home/root/current_time"
       read_command = "cat /home/root/current_time"
       execute_ssh_command(hostIp, username, write_command)
       stdout = execute_ssh_command(hostIp, username,read_command)
    read_time = stdout.strip() if stdout else None
    if read_time == current_time:
        print("[v] Time write OK")
        return True
    else:
       print("[x] Time write FAIL")
       return False


def write_cfg_to_board(new_mac, new_serial, hostIp, username, password="allnewb2b^^"):
    """보드에 새로운 cfg.yml 파일을 생성하고 전송"""
    print(f"[...] Writing cfg.yml with MAC: {new_mac}, Serial: {new_serial} to {hostIp}")

    # 현재 디렉토리에서 cfg.yml 파일 읽기
    with open('new_cfg.yml', 'r') as file:
        cfg_data = yaml.safe_load(file)  # YAML 파일을 파싱

    # MAC 주소와 Serial 번호 수정
    cfg_data['ETH']['mac'] = new_mac
    cfg_data['VERSION']['serial'] = new_serial

    # 수정된 내용을 다시 YAML 형식으로 저장
    with open('new_cfg.yml', 'w') as file:
        yaml.dump(cfg_data, file)

    # SSH 명령어를 통해 원격 서버에 파일 내용 쓰기
    if platform.system() == "Windows":
        check_command = f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no root@{hostIp} \"cat > /lg_rw/fct_test/cfg.yml\""
    else:
        check_command = f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no root@{hostIp} 'cat > /lg_rw/fct_test/cfg.yml'"

    try:
        # subprocess.Popen을 사용하여 파일 내용을 전송
        with open('new_cfg.yml', 'rb') as file:
            process = subprocess.Popen(check_command, shell=True, stdin=subprocess.PIPE)
            process.communicate(input=file.read())
            
        
        print("[v] cfg write OK")  # 성공 메시지 출력
        return True

    except subprocess.CalledProcessError as e:
        print(f"[x] cfg write FAIL {e.stderr.decode().strip()}")
        return False
    except Exception as e:
        print(f"[x] cfg write FAIL {e}")
        return False


def main(hostIp, username):

    # known host 삭제
    known_hosts_path = os.path.expanduser("~/.ssh/known_hosts")
    if not remove_known_host(known_hosts_path, hostIp):
        return

    # Find the next row index to start processing
    if not find_next_row_index():
        return

    

    while True:
        print("*********** Do you want to start FCT ? ***********")
        user_input = input(" Please answer (y/n): ").strip().lower()
        if user_input == 'y':
            while True:
                if check_ssh_connection(hostIp, username):
                    print("==================Connection OK========================")
                    read_result, sn, mac = read_sn_mac_from_file()
                    if read_result:
                        print(f"[Serial Number] {sn}\n[ MAC Address ] {mac}")
                        #맥주소 00:1A:2B:3C:4D:5F 되어있을 경우 : 지우기
                        mac = mac.replace(":", "")

                        if write_sn_mac_to_board(sn, mac, hostIp, username,"allnewb2b^^"):
                            #colum date
                            if update_check_column():
                                #cfg 파일 전송
                                if write_cfg_to_board(mac,sn,hostIp,username):
                                    if send_time_now(username, hostIp):
                                        #fct 시작
                                        if start_fct_test(hostIp,username):
                                            print("[v] FCT OK")
                                            print("================== Please replace the board for the next test ==================")
                                            time.sleep(20)            
                                            break
        elif user_input == 'n':
            print("[v] Exit program")
            break
        else:
            print("Please Input y or n")
            

        

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='SSH to a remote server and write/read the current time.')
    parser.add_argument('hostIp', nargs='?', default='192.168.1.101', type=str, help='The IP address of the remote host (default: 192.168.1.100)')
    
    args = parser.parse_args()
    hostIp = args.hostIp
    username = 'root'
    main(hostIp, username)
