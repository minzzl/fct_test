#!/usr/bin/env python3

import subprocess
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import yaml
import shutil
import hashlib
import threading
import sys
import shlex
import time
import select
import multiprocessing

subprocess.run("dmesg -n 1", shell=True)
subprocess.run("mount -o rw,remount /", shell=True)

def get_log_datetime():
    # 현재 시스템 시간을 읽어와서 포맷팅합니다.
    log_datetime = datetime.now().strftime('%Y-%m-%d %H:%M')
    return log_datetime

log_datetime = get_log_datetime()
print(f"Log date and time: {log_datetime}")

# YAML 파일 읽기
with open('/lg_rw/fct_interface/cfg.yml', 'r') as file:
    config = yaml.safe_load(file)

# global 설정 읽기
global_config = config['global']

# CPU 스트레스 설정 확인
cpu_stress = config.get('global', {}).get('cpu_stress', 0)

# CPU 스트레스 프로세스 초기화
cpu_stress_process = None

# CPU 스트레스 설정
if cpu_stress > 0:
    cpu_cores = 4  # 사용할 CPU 코어 수 (필요에 따라 조정)
    stress_cmd = f"/lg_rw/fct_interface/stress --cpu {cpu_cores} --cpu-load {cpu_stress}"
    cpu_stress_process = subprocess.Popen(stress_cmd, shell=True)
    print(f"Started CPU stress with {cpu_stress}% load on {cpu_cores} cores")

# WiFi 설정을 wpa_supplicant.conf 파일에 작성
wifi_config = config['wifi']
if wifi_config['enable']:
    if wifi_config['password'] != None :
        wpa_supplicant_conf = f"""
ctrl_interface=/var/run/wpa_supplicant
ctrl_interface_group=0
update_config=1
network={{
    ssid="{wifi_config['ssid']}"
    psk="{wifi_config['password']}"
    key_mgmt=WPA-PSK
}}
"""
    else:
        wpa_supplicant_conf = f"""
ctrl_interface=/var/run/wpa_supplicant
ctrl_interface_group=0
update_config=1
network={{
    ssid="{wifi_config['ssid']}"
    key_mgmt=NONE
}}
"""
    with open('/lg_rw/fct_interface/wpa_supplicant.conf', 'w') as wpa_file:
        wpa_file.write(wpa_supplicant_conf)

    # 네트워크 인터페이스 설정
    subprocess.run("dmesg -n 1", shell=True)
    subprocess.run("mount -o rw,remount /", shell=True)
    subprocess.run(f"ifconfig {wifi_config['name']} up", shell=True)
    # wpa_supplicant.conf 파일 복사 및 권한 설정
    subprocess.run("cp -f /lg_rw/fct_interface/wpa_supplicant.conf /etc/wpa_supplicant.conf", shell=True)
    subprocess.run("chmod +x /etc/wpa_supplicant.conf", shell=True)

# WiFi 및 BLE MAC 주소 읽기
def get_mac_address(interface,target):
    try:
        mac = subprocess.run(f"cat /sys/class/{target}/{interface}/address", shell=True, capture_output=True, text=True).stdout.strip()
        mac = mac.replace(":", "")  # 콜론 제거
    except Exception as e:
        mac = "unknown"
    return mac

def get_current_ble_mac_address():
    try:
        result = subprocess.run("hcitool dev", shell=True, capture_output=True, text=True).stdout.strip()
        
        for line in result.splitlines():
            if "hci" in line:
                mac_address = line.split()[1]
                return mac_address.replace(":", "") 
    except Exception as e:
        print(f"Failed to get current BLE MAC address: {e}")
    return "unknown"


eth_mac = get_mac_address("eth0",'net')
# ble_mac = get_current_ble_mac_address()
# print(ble_mac)

# 로그 파일 설정
log_file_path = '/lg_rw/fct_interface/fct_test.log'
usb_log_file_path = f"interface_{eth_mac}.log"

# 로그 파일에 날짜 기록
with open(log_file_path, 'a') as log_file:
    log_file.write("###############################################################\n")
    log_file.write(f"Test started at: {log_datetime}\n")

# 테스트 항목, 스크립트, 순서
test_items = {
    'wifi': ['wlan0_test.sh',0],
    'eth': ['eth0_test.sh',0],
    'ble': ['ble_test.sh',0],
    'dio': ['dio_test.sh',0],
    'uart': ['485_test.sh',0],
    'expansion': ['expansion.sh',0],
    'pwm': ['pwm_test.sh',0],
    'usb': ['usb_test.sh',0],
    'emmc': ['emmc_test.sh',0],
    'memory': ['mem_test.sh',0],
    'cpu': ['cpu_test.sh',0],
    'touch': ['touch_test.sh',0],
    'LCD': ['lcd_test.sh',0],
    'LED': ['led_test.sh',0],
    'RTC': ['rtc_test.sh',0],
    'expansion_full': ['expansion_full.sh',0],
}

# 기본 설정값
default_config = {
    'uart': {'boadrate': 115200, 'data': 256},
    'wifi': {'name': 'wlan0', 'address': '192.168.0.1'},
    'eth': {'address': '192.168.0.1'},
    'ble': {'mac': '00:00:00:00:00:00'},
    'usb': {'file_path': '/lg_rw/fct_interface', 'data': 1}
}

# 값의 범위 설정
valid_ranges = {
    'uart': {'boadrate': [4800, 9600, 19200, 38400, 57600, 115200], 'data': range(1, 256+1)},
    'wifi': {'name': str, 'address':str},
    'eth': {'address':str},
    'ble': {'mac': str},
    'usb': {'file_path': str, 'data': [1,50,100]}
}

# 실시간 출력을 처리하는 함수
def run_test_script(script, args):
    #print(f"Running {script} {args}...", flush=True)
    process = subprocess.Popen(
        f"{script} {args}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,  # 텍스트 모드로 스트림 처리
        bufsize=1,  # 라인 버퍼링
        env=os.environ 
    )
    log_lines = []
    last_line = ""

    while True:
        try:
            output = process.stdout.readline()
            if output:
                print(output.strip(), flush=True)  # flush=True로 강제 플러시
                log_lines.append(output.strip())
                last_line = output.strip()
            if process.poll() is not None:
                break
        except UnicodeDecodeError:
            print("result message include UnicodeDecodeError. Ignoring the line.")
    # Ensure all remaining output is read
    remaining_output = process.stdout.read()
    if remaining_output:
        for line in remaining_output.splitlines():
            print(line.strip(), flush=True)
            log_lines.append(line.strip())
    process.wait()  # Add this line
    return process.returncode, log_lines

#실시간 출력을 처리하는 함수
def run_test_script_spi(script, args):
    process = subprocess.run(f"{script} {args.strip()}", shell=True, capture_output=True, text=True,env=os.environ )  # strip args to remove trailing spaces
    log_lines = []

    try:
        output = process.stdout.split('\n')  # split the output into lines
        for line in output:
            line = line.strip()  # strip line to remove trailing spaces
            print(line, flush=True)  # flush=True로 강제 플러시
            log_lines.append(line)
    except UnicodeDecodeError:
        print("result message include UnicodeDecodeError. Ignoring the line.")
    return process.returncode, log_lines

# 전역 변수 사용 최소화
lock = multiprocessing.Lock()
manager = multiprocessing.Manager()
test_results = {}

def get_test_args(item, config, default_config, valid_ranges):
    if item not in config:
        raise ValueError(f"Invalid test item: {item}")
    
    item_config = config.get(item, {})
    default_item_config = default_config.get(item, {})
    valid_item_ranges = valid_ranges.get(item, {})
    
    args = {}
    
    for key, default_value in default_item_config.items():

        if key not in item_config or item_config[key] == None or item_config[key] == '':
            value = default_value
        else:
            value = item_config[key]
        
        # valid_range 체크
        valid_range = valid_item_ranges.get(key)
        if valid_range is not None:
            if isinstance(valid_range, range) and value not in valid_range:
                raise ValueError(f"Invalid value for {item} {key}: {value}")
            elif isinstance(valid_range, list) and value not in valid_range:
                raise ValueError(f"Invalid value for {item} {key}: {value}")
            elif isinstance(valid_range, type) and not isinstance(value, valid_range):
                raise ValueError(f"Invalid type for {item} {key}: {value}")
        
        args[key] = value
    return args

def execute_test(item, script, verbose=True):
    if config[item]['enable']:
        test_name = item
        repeat = config[item]['repeat']
        
        if verbose:
            print("########################################")
            print(f"Running {test_name}...", flush=True)
        
        test_results[test_name] = {}
        
        for i in range(repeat):
            try:
                args = get_test_args(item, config, default_config, valid_ranges)

            except ValueError as e:
                print(f"Error: {e}")
                with lock:
                    if repeat > 1:
                        test_results[test_name][f'test_{i+1}'] = f"[{test_name}] FAIL (Invalid value)"
                    else:   
                        test_results[test_name] = f"[{test_name}] FAIL (Invalid value)"
                return
            
            if item == 'uart':
                args_str = f"{args['boadrate']} {args['data']}"
            elif item == 'wifi':
                args_str = f"-p {args['address']} {args['name']}"
            elif item == 'eth':
                args_str = f"{args['address']}"
            elif item == 'ble':
                args_str = f"-m \"{args['mac']}\""
            elif item == 'usb':
                args_str = f"{args['file_path']} {args['data']}"
            else:
                args_str = ''
            script_path = os.path.abspath(f"/lg_rw/fct_interface/{script}")
            
            # 디버깅을 위한 추가 코드
            if not os.path.exists(script_path):
                print(f"Error: The script {script_path} does not exist!")
                return
            if not os.access(script_path, os.R_OK):
                print(f"Error: The script {script_path} is not readable!")
                return
            if item == "spi":
                result_code, log_lines = run_test_script_spi(script_path, args_str)
                last_line = log_lines[-1] if log_lines else "No output"
            else:
                result_code, log_lines = run_test_script(script_path, args_str)
                last_line = log_lines[-1] if log_lines else "No output"
            
            with lock:
                if repeat > 1:
                    test_results[test_name][f'test_{i+1}'] = last_line
                else:   
                    test_results[test_name] = last_line

        else:
            # If the loop completes without a break, record the last result
            with lock:
                if repeat > 1:
                    test_results[test_name][f'test_{i+1}'] = last_line
                else:   
                    test_results[test_name] = last_line


# 병렬 실행 여부 확인
parallel = config.get('global', {}).get('parallel', False)


# wifi와 ble 테스트가 최초로 실행되었는지 여부를 추적하는 플래그
first_run_done = multiprocessing.Event()
stop_event = multiprocessing.Event()

def worker(item, script, first_run_done, stop_event):

    if item in ['wifi', 'ble']:
        if not first_run_done.is_set():
            execute_test(item, script, False)
            first_run_done.set()
    else:
        while not stop_event.is_set():
            execute_test(item, script, False)
            if stop_event.is_set():
                break
    #print(item, "worker done....")

def input_listener(stop_event):
    print("Press Enter to stop the tests...\n")
    while True:
        # select.select()을 사용하여 입력을 모니터링
        if select.select([sys.stdin], [], [], 1)[0]:
            print("...")
            # Enter 키 입력을 감지
            if sys.stdin.read(1) == '\n':
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                print("@@@@@@@@@@ You want to exit... @@@@@@@@@@@@")
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                stop_event.set()
                
                break


def run_tests_in_parallel():

    processes = []
    for item, script in test_items.items():
        if config[item]['enable']:
            p = multiprocessing.Process(target=worker, args=(item, script[0], first_run_done, stop_event))
            p.start()
            processes.append(p)

    input_listener(stop_event)

    for p in processes:
        p.join()



    


# 병렬 실행 시
if parallel:
    run_tests_in_parallel()
    #print("done")

# 순차 실행 시
else:
    # 순서를 설정
    for item in test_items.keys():
        if config[item]['enable']:
            # 순서를 체크한다
            if 'order' in config[item]:
                test_items[item][1] = config[item]['order']
    
    # 정렬한다
    test_items = dict(sorted(test_items.items(), key=lambda item: item[1][1]))

    for item, script in test_items.items():
        execute_test(item, script[0], True)

# 테스트 결과 확인 및 출력
all_tests_passed = True
failed_count = 0
total_count = 0
print("-" * 40, flush=True)
print("-" * 40, flush=True)

with open(log_file_path, 'a') as log_file:
    for test_name, iterations in test_results.items():
        if isinstance(iterations, dict):
            for iteration, result in iterations.items():
                total_count += 1
                print(f"{test_name}: {result}", flush=True)
                log_file.write(f"{test_name} {iteration}: {result}\n")
                if "OK" not in result:
                    all_tests_passed = False
                    failed_count += 1
        else:
            total_count += 1
            print(f"{test_name}: {iterations}", flush=True)
            log_file.write(f"{test_name}: {iterations}\n")
            if "OK" not in iterations:
                all_tests_passed = False
                failed_count += 1

    print("-" * 40, flush=True)
    if failed_count == total_count:
        print(f"Total tests: {total_count}, All tests failed", flush=True)
        log_file.write(f"Total tests: {total_count}, All tests failed\n")
    else:
        print(f"Total tests: {total_count}, Failed tests: {failed_count}", flush=True)
        log_file.write(f"Total tests: {total_count}, Failed tests: {failed_count}\n")
    print("-" * 40, flush=True)
    log_file.write("-" * 40 + "\n")

print("**********")

# 전체 테스트 결과 출력
with open(log_file_path, 'a') as log_file:
    if all_tests_passed:
        print("[ALL TESTS]: OK", flush=True)
        log_file.write("[ALL TESTS]: OK\n")
    else:
        if failed_count == total_count:
            print("[ALL TESTS]: FAIL (TOTAL)", flush=True)
            log_file.write("[ALL TESTS]: FAIL (TOTAL)\n")
        else:
            print(f"[ALL TESTS]: {failed_count} out of {total_count} tests failed", flush=True)
            log_file.write(f"[ALL TESTS]: {failed_count} out of {total_count} tests failed\n")


def find_usb_device():
    for attempt in range(3):
        try:
            # /dev 디렉토리에서 exfat 파일 시스템을 가진 파티션을 찾음
            lsblk_output = subprocess.run("lsblk -o NAME,FSTYPE", shell=True, capture_output=True, text=True).stdout.strip()
            if lsblk_output:
                lines = lsblk_output.splitlines()
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2 and 'exfat' in parts[1]:  # exFAT 파일 시스템이 포함된 라인을 찾음
                        device_name = parts[0].strip('`-')  # 디바이스 이름에서 `-` 문자를 제거
                        return f"/dev/{device_name}"
        except Exception as e:
            print(f"Attempt {attempt + 1}: Failed to find USB device: {e}")
    return None

def is_mounted(device_name, mount_point):
    try:
        # mount 명령어를 사용하여 현재 마운트된 디바이스 목록을 확인
        result = subprocess.run("mount", shell=True, capture_output=True, text=True).stdout.strip()
        for line in result.splitlines():
            if device_name in line and mount_point in line:
                return True
    except Exception as e:
        print(f"Failed to check if device is mounted: {e}")
    return False

def mount_usb(device_name, mount_point):
    for attempt in range(3):
        try:
            if not mount_point:
                mount_point = "/lg_rw/fct_interface/result"
                os.makedirs(mount_point, exist_ok=True)
            
            # 디바이스가 이미 마운트되어 있는지 확인
            if is_mounted(device_name, mount_point):
                print(f"{device_name} is already mounted on {mount_point}")
                return mount_point
            
            # 마운트 포인트가 존재하지 않으면 생성
            if not os.path.exists(mount_point):
                subprocess.run(f"mkdir -p {mount_point}", shell=True, check=True)
            
            # 디바이스 마운트
            subprocess.run(f"mount {device_name} {mount_point}", shell=True, check=True)
            return mount_point
        except Exception as e:
            print(f"Attempt {attempt + 1}: Failed to mount USB device: {e}")
    return None

def unmount_usb(mount_point):
    for attempt in range(3):
        try:
            subprocess.run(f"umount {mount_point}", shell=True, check=True)
            print(f"Successfully unmounted {mount_point}")
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1}: Failed to unmount USB device: {e}")
    return False

def compare_files(file1, file2):
    try:
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            for line1, line2 in zip(f1, f2):
                if line1 != line2:
                    return False
        return True
    except Exception as e:
        print(f"Failed to compare files: {e}")
        return False

def copy_log_file(src, dst):
    for attempt in range(3):
        try:
            shutil.copy(src, dst)
            print(f"Log file copied to USB: {dst}")
            if compare_files(src, dst):
                print(f"Log file successfully verified: {dst}")
                return True
            else:
                print(f"Verification failed for {dst}. Retrying...")
        except Exception as e:
            print(f"Attempt {attempt + 1}: Failed to copy log file to USB: {e}")
    return False

# USB 장치 찾기
device_name = find_usb_device()
print(f"USB Device Name: {device_name}")  # 디버깅을 위해 추가

if device_name:
    # USB 장치 마운트
    mount_point = mount_usb(device_name, "/lg_rw/fct_interface/result")
    if mount_point:
        # 로그 파일 경로 생성
        usb_full_log_path = os.path.join(mount_point, usb_log_file_path)
        print(f"USB Full Log Path: {usb_full_log_path}")  # 디버깅을 위해 추가

        # 로그 파일을 USB로 복사 및 검증
        if copy_log_file(log_file_path, usb_full_log_path):
            # USB 장치 언마운트
            if not unmount_usb(mount_point):
                print("Failed to unmount USB device.")
        else:
            print("Failed to copy and verify log file to USB.")
    else:
        print("Failed to mount USB device")
else:
    print("USB device not found.")



    ----------------------

global:
  parallel: false
  cpu_stress: 0
wifi:
  name: wlan0
  address: 192.168.1.100
  ssid: "next_test"
  password: "12347890"
  enable: false
  repeat: 1
  order: 1
eth:
  address: 192.168.1.100
  enable: false
  repeat: 1
  order: 2
ble:
  mac: "8A:88:4B:60:1F:FF"
  enable: false
  repeat: 1
  order: 3
dio:
  enable: false
  repeat: 1
  order: 4
uart:
  boadrate: 9600
  data: 256
  enable: false
  repeat: 1
  order: 5
usb:
  file_path: "/home/root"
  data: 1
  enable: false
  repeat: 1
  order: 6
expansion:
  enable: false
  repeat: 1
  order: 7
expansion_full:
  enable: true
  repeat: 1
  order: 8
emmc:
  data: 1
  enable: false
  repeat: 1
  order: 8
memory:
  data: 1
  enable: false
  repeat: 1
  order: 9
cpu:
  data: 1
  enable: false
  repeat: 1
  order: 10
touch:
  enable: false
  repeat: 1
  order: 11
LCD:
  enable: false
  repeat: 1
  order: 12
pwm:
  enable: false
  repeat: 1
  order: 13
LED:
  enable: false
  repeat: 1
  order: 14
RTC:
  enable: false
  repeat: 1
  order: 15
-----------------


Traceback (most recent call last):
  File "/lg_rw/fct_expansion/test_start_dq1.py", line 373, in <module>
    if config[item]['enable']:
KeyError: 'RTC'
root@dq1:~#



왜 이런 오류가 날까 
    
