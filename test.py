[root@webOSNano-unofficial /lg_rw/fct_test]# cat  wlan0_test_fail.flag
1[root@webOSNano-unofficial /lg_rw/fct_test]# exit

import argparse
import time
import os
import pandas as pd
import threading
import subprocess
import yaml
from datetime import datetime
import subprocess
import paramiko
import sys
import warnings

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
    print(f"[...] Checking SSH connection to {host} as {username}")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password, timeout=10)
        client.close()
        print("[v] SSH Connection OK")
        return True
    except Exception as e:
        print(f"[x] SSH Connection FAIL")
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
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password, timeout=10)
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode().strip()
        client.close()
        return output
    except Exception as e:
        print(f"[x] SSH execute command error: {e}")
        return None

def write_sn_mac_to_board(sn, mac, host, username, password="allnewb2b^^"):
    print(f"[...] Writing SN ({sn}) and MAC ({mac}) to board {host}")
    write_command = f"echo {sn} > /persist/serial_number && /usr/bin/misc-util ETH_MAC {mac} && echo PACPIA000.AKM > /persist/model_number"
    check_command = "cat /persist/serial_number && /usr/bin/misc-util ETH_MAC && cat /persist/model_number"
    execute_ssh_command(host, username, write_command, password)
    stdout = execute_ssh_command(host, username, check_command, password)
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


def board_reboot(hostIp, username, password="allnewb2b^^"):
    print(f"[...] Rebooting board {hostIp}")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=hostIp, username=username, password=password, timeout=10)
        
        # Reboot command with sudo
        print(f"[...] Executing reboot command ...")

        #client 의 /lg_rw/fct_test/wlan0_test_fail.flag 위치에서 값을 읽어온다.
        stdin, stdout, stderr = client.exec_command("cat /lg_rw/fct_test/wlan0_test_fail.flag")
        print("result: ", stderr.read().decode().strip())
        flag_content = stderr.read().decode().strip()
        if flag_content == "1":
            # 해당 파일 삭제하고 끝내기
            client.exec_command("rm -f /lg_rw/fct_test/wlan0_test_fail.flag")
            print("[x] Reboot aborted due to failure flag")
            client.close()
            exit(1)  # 종료 코드 1로 종료
            return False
        else:
            stdin, stdout, stderr = client.exec_command("/sbin/reboot")
        
        # Read stderr for any error messages
        error_output = stderr.read().decode().strip()
        if error_output:
            print(f"[x] Error during reboot: {error_output}")
        
        # Wait for the command to complete
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("[v] Board rebooted successfully")
            return True
        else:
            print(f"[x] Board reboot failed with exit status {exit_status}")
            return False
    except paramiko.AuthenticationException:
        print(f"[x] Authentication failed for user {username}")
    except paramiko.SSHException as ssh_ex:
        print(f"[x] SSH connection error: {ssh_ex}")
    except Exception as e:
        print(f"[x] Board reboot error: {e}")
    finally:
        client.close()  # Ensure the SSH connection is closed
        
    return False


def start_fct_test(hostIp, username, password="allnewb2b^^"):
    print("[...] Starting FCT Test")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=hostIp, username=username,
                       password=password, timeout=10)

        transport = client.get_transport()
        channel = transport.open_session()
        channel.get_pty()
        channel.exec_command("python3 /lg_rw/fct_test/test_start_dq1.py")

        while True:
            if channel.recv_ready():
                output = channel.recv(1024).decode("utf-8")
                sys.stdout.write(output)
                sys.stdout.flush()

                low = output.lower()              # 소문자 비교용

                if 'y/n' in low:                  # (1) y/n 응답
                    user_input = input('Enter y or n: ')
                    channel.send(user_input + '\n')

                elif 'input serial' in low:       # (2) “Input serial :” 응답  ### <--- ADDED
                    user_input = input()  # 원격 프롬프트 그대로 보여줌  ### <--- ADDED
                    channel.send(user_input + '\n')           ### <--- ADDED

            if channel.exit_status_ready():
                break

        exit_status = channel.recv_exit_status()
        channel.close()
        client.close()

        if exit_status == 0:
            print("[v] FCT Test Completed")
            return True
        else:
            print(f"[x] FCT Test failed with exit status {exit_status}")
            return False

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
        return True



def send_time_now(username, hostIp, password="allnewb2b^^"):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[...] Sending current time ({current_time}) to {hostIp}")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=hostIp, username=username, password=password)
        cmd_write = f"echo '{current_time}' > /home/root/current_time"
        cmd_read = "cat /home/root/current_time"
        client.exec_command(cmd_write)
        time.sleep(0.5)
        stdin, stdout, stderr = client.exec_command(cmd_read)
        read_time = stdout.read().decode().strip()
        client.close()
        if read_time == current_time:
            print("[v] Time write OK")
            return True
        else:
            print("[x] Time write FAIL")
            return False
    except Exception as e:
        print(f"[x] Time write error: {e}")
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

    # SSH 연결 및 파일 전송
    try:
        print("[*] Establishing SSH connection")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=hostIp, username=username, password=password)
        print("[*] SSH connection established")

        # 파일 내용을 읽어와서 원격 서버에 cat 명령어로 기록
        with open('new_cfg.yml', 'rb') as file:
            file_content = file.read()
            command = f"cat > /lg_rw/fct_test/cfg.yml"
            stdin, stdout, stderr = client.exec_command(command)
            stdin.write(file_content)
            stdin.close()

        print("[v] cfg write OK")  # 성공 메시지 출력
        client.close()
        return True

    except paramiko.SSHException as ssh_error:
        print(f"[x] SSH error: {ssh_error}")
    except Exception as e:
        print(f"[x] cfg write FAIL ({e})")
    
    return False

def write_pc_launcher_to_board(launcher, hostIp, username, password="allnewb2b^^"):
    """보드에 새로운 index.html, launcher.exe 파일을 전송"""
    print(f"[...] Writing index.html, launcher.exe to {hostIp}")

    # SSH 연결 및 파일 전송
    try:
        print("[*] Establishing SSH connection")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=hostIp, username=username, password=password)
        print("[*] SSH connection established")

        # /lg_rw/b2b-platform/http 디렉토리 생성
        client.exec_command("mkdir -p /lg_rw/b2b-platform/http")

        # index.html 파일 전송
        with open("index.html", 'rb') as file:
            file_content = file.read()
            command = f"cat > /lg_rw/b2b-platform/http/index.html"
            stdin, stdout, stderr = client.exec_command(command)
            stdin.write(file_content)
            stdin.close()

        # launcher.exe 파일 전송
        with open(launcher, 'rb') as file:
            file_content = file.read()
            command = f"cat > /lg_rw/b2b-platform/http/launcher.exe"
            stdin, stdout, stderr = client.exec_command(command)
            stdin.write(file_content)
            stdin.close()

        print("[v] index.html, launcher.exe write OK")  # 성공 메시지 출력
        client.close()
        return True
    except paramiko.SSHException as ssh_error:
        print(f"[x] SSH error: {ssh_error}")
    except Exception as e:
        print(f"[x] index.html, launcher.exe write FAIL ({e})")
    return False

def main(hostIp, username):
    
    while True:
        # print("*********** Do you want to start FCT ? ***********")
        # user_input = input(" Please answer (y/n): ").strip().lower()
        # if user_input == 'y':
        # known host 삭제
        known_hosts_path = os.path.expanduser("~/.ssh/known_hosts")
        if not remove_known_host(known_hosts_path, hostIp):
            break
        # Find the next row index to start processing
        if not args.spec and not find_next_row_index():
            break
        
        while True:
            if not check_ssh_connection(hostIp, username):
                print("[*] Wait 10 Seconds and Retry..")
                time.sleep(10)
                continue

            print("==================Connection OK========================")
            # --spec 플래그가 활성화된 경우 아래 코드 블록을 건너뜁니다.
            if not args.spec:
                read_result, sn, mac = read_sn_mac_from_file()
                if not read_result:
                    print("[x] Excel read FAIL")
                    break

                print(f"[Serial Number] {sn}\n[ MAC Address ] {mac}")
                # 맥주소 00:1A:2B:3C:4D:5F 되어있을 경우 : 지우기
                mac = mac.replace(":", "")

                if not write_sn_mac_to_board(sn, mac, hostIp, username, "allnewb2b^^"):
                    print("[x] Write SN or MAC FAIL")
                    break

                # column date
                if not update_check_column():
                    print("[x] Excel Check FAIL")
                    break
                # index.html, launcher.exe 파일 전송
                if not write_pc_launcher_to_board("launcher.exe", hostIp, username):
                    print("[x] index.html, launcher.exe write FAIL")
                    break
            else:
                # --spec 플래그가 활성화된 경우 기본 MAC 주소 설정
                mac = "00:00:00:00:00:00"  # 기본 MAC 주소를 설정합니다.
                sn = "DEFAULT_SN"  # 기본 Serial Number를 설정합니다.
            # cfg 파일 전송
            if not write_cfg_to_board(mac, sn, hostIp, username):
                print("[x] cfg write FAIL")
                break


            if not send_time_now(username, hostIp):
                print("[x] Time write FAIL")
                break

            # fct 시작
            if start_fct_test(hostIp, username):
                print("[v] FCT OK")

            if board_reboot(hostIp, username):
                print("[v] Board reboot OK")

            if not args.spec:
                print("================== Please replace the board for the next test ==================")
                time.sleep(20)            
                break
            time.sleep(30)    
    # elif user_input == 'n':
    #     print("[v] Exit program")
    #     break
    # else:
    #     print("Please Input y or n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SSH to a remote server and write/read the current time.')
    parser.add_argument('hostIp', nargs='?', default='192.168.1.101', type=str, help='The IP address of the remote host (default: 192.168.1.100)')
    parser.add_argument('--spec', action='store_true', help='Enable spec test')
    warnings.filterwarnings("ignore", category=UserWarning)
    global args
    args = parser.parse_args()
    hostIp = args.hostIp
    username = 'root'
    main(hostIp, username)

아래의 코드가 제대로 의도대로 동작하지 않는 것같아cat 하면 1이 나오는데, result 찍어보니까 아무것도 안뜨네
[...] Executing reboot command ...
result:
이렇게 

   #client 의 /lg_rw/fct_test/wlan0_test_fail.flag 위치에서 값을 읽어온다.
        stdin, stdout, stderr = client.exec_command("cat /lg_rw/fct_test/wlan0_test_fail.flag")
        print("result: ", stderr.read().decode().strip())
        flag_content = stderr.read().decode().strip()
        if flag_content == "1":
            # 해당 파일 삭제하고 끝내기
            client.exec_command("rm -f /lg_rw/fct_test/wlan0_test_fail.flag")
            print("[x] Reboot aborted due to failure flag")
            client.close()
            exit(1)  # 종료 코드 1로 종료
            return False
        else:
            stdin, stdout, stderr = client.exec_command("/sbin/reboot")
