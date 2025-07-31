1. new_cfg.yml 
"DIO:
  enable: false
  order: 6
  repeat: 1
ETH:
  address: 192.168.1.100
  auto: true
  enable: false
  mac: 00:00:00:00:00:00
  order: 3
  repeat: 1
LCD:
  auto: false
  enable: false
  order: 8
  repeat: 1
PWM:
  auto: false
  enable: false
  order: 5
  repeat: 1
RTC:
  auto: false
  enable: false
  order: 1
  repeat: 1
TOUCH:
  enable: false
  order: 9
  repeat: 1
UART:
  boadrate: 9600
  data: 256
  enable: false
  order: 7
  repeat: 1
USB:
  enable: true
  auto: false
  order: 2
  repeat: 1
  uart-1: true
  uart-2: false
VERSION:
  app: com.acp.energy,com.acp.softap,com.acp.lgapcomm,com.acp.logics,com.acp.mailer,com.acp.mqttbroker,com.acp.mqttpublisher,com.acp.quickinstall,com.acp.restserver,com.acp.tmsclient,com.acp.trends,com.acp.flat,com.acp.lcd
  enable: false
  kernel: 5.15.174-b0-saturn
  model: PACPIA000.AKM
  order: 1
  ram: 1.0.0
  repeat: 1
  serial: DEFAULT_SN
BLUETOOTH:
  enable: false
  mac: 0
  max: 0
  min: 0
  order: 0
  repeat: 1
WIFI:
  address: 192.168.2.254
  enable: false
  max: -10
  min: -90
  name: wlan0
  order: 4
  password: 12347890
  repeat: 1
  ssid: next_test
global:
  log_file_path: /lg_rw/expansion_test.log
  parallel: false
"
2. test_start_dq1.py

"#!/usr/bin/env python3

import subprocess
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import yaml
import shutil
import sys
import select
import multiprocessing
import json



subprocess.run("dmesg -n 1", shell=True)
# subprocess.run("mount -o rw,remount /", shell=True)


def get_log_datetime():
    # 현재 시스템 시간을 읽어와서 포맷팅합니다.
    log_datetime = datetime.now().strftime('%Y-%m-%d %H:%M')
    return log_datetime

log_datetime = get_log_datetime()
# 테스트 진행 중 출력 예시
print("========================================")
print("              TEST IN PROGRESS         ")
print("========================================")
print(f"Log date and time: {log_datetime}")

# YAML 파일 읽기
with open('/lg_rw/fct_test/cfg.yml', 'r') as file:
    config = yaml.safe_load(file)


# 이더넷 맥 주소 읽기
def get_wired_addr():
    cmd = "luna-send -n 1 -f luna://com.webos.service.systemservice/deviceInfo/query '{}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    try:
        response = json.loads(result.stdout)
        wired_addr = response.get("wired_addr", None)
        if wired_addr:
            # ":" 문자를 제거하고 소문자로 변환
            wired_addr = wired_addr.replace(":", "").lower()
            return wired_addr
        else:
            print("[log] wired_addr not found")
            return "None"
    except json.JSONDecodeError:
        print("[log] Invalid JSON data")
        return "None"

eth_mac = get_wired_addr()


check1 = config['USB'].get('uart-1', False)
check2 = config['USB'].get('uart-2', False)

# 로그 파일 설정
log_file_path = config.get('global', {}).get('log_file_path', '/lg_rw/fct_test/expansion_fct_test.log')

if check1:

    print("[Q] 1번 확장 보드의 시리얼 번호 입력(스캐너로 큐알을 스캔하세요):")
    label_serial1 = input().strip()          ### CHANGED
    usb_log_file_path = f"expansion_fct_test_{label_serial1}.log"
if check2:
    print("[Q] 1번 확장 보드의 시리얼 번호 입력(스캐너로 큐알을 스캔하세요):")
    label_serial1 = input().strip()          ### CHANGED
    usb_log_file_path = f"expansion_fct_test_{label_serial1}.log"
    print("[Q] 2번 확장 보드의 시리얼 번호 입력(스캐너로 큐알을 스캔하세요):")
    label_serial2 = input().strip()   
    usb_log_file_path = f"expansion_fct_test_{label_serial1}_{label_serial2}.log"

# 로그 파일에 날짜 기록
with open(log_file_path, 'a') as log_file:
    log_file.write("###############################################################\n")
    log_file.write(f"Test started at: {log_datetime}\n")

# 테스트 항목, 스크립트, 순서
test_items = {
    'VERSION': ['sw_version_test.py',0],
    'WIFI': ['wlan0_test.py',0],
    'ETH': ['eth0_test.sh',0],
    # 'BLUETOOTH': ['ble_test.py',0],
    'DIO': ['dio_test.py',0],
    'RTC': ['rtc_test.py',0],
    'UART': ['485test.py',0],
    'PWM': ['pwm_test.py',0],
    'USB': ['usb_test.py',0],
    'TOUCH': ['touch_test.py',0],
    'LCD': ['lcd_test.py',0],
}

# 기본 설정값
default_config = {
    'VERSION': {'kernel': "", 'ram': "", "serial": "", "app" : "", "model": "" },
    'UART': {'boadrate': 115200, 'data': 256},
    'WIFI': {'ssid': 'next_test','name': 'wlan0', 'address': '192.168.0.1', 'password': '12345678', 'min': -60, 'max': -40},
    'ETH': {'address': '192.168.0.1', "mac":""},
    # 'BLUETOOTH': {'mac': '00:00:00:00:00:00','min': -60, 'max': -40},
    'USB': {'file_path': '/lg_rw/fct_test', 'data': 1}
}

# 값의 범위 설정
valid_ranges = {
    'UART': {'boadrate': [4800, 9600, 19200, 38400, 57600, 115200], 'data': range(1, 256+1)},
    'WIFI': {'name': str, 'address':str},
    'ETH': {'address':str },
    # 'BLUETOOTH': {'mac': str},
}

# 실시간 출력을 처리하는 함수
def run_test_script(script, args):
    # 실행파일이 파이썬인 경우
    if script.endswith('.py'):
        #print(f"Running Python script: {script} with args: {args}")
        command = f"python3 -u {script} {args}"  # -u 플래그 추가
    else:
        command = f"{script} {args}"


    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,  # 텍스트 모드로 스트림 처리
        bufsize=1,  # 라인 버퍼링
        env={**os.environ, 'PYTHONUNBUFFERED': '1'}  # PYTHONUNBUFFERED 환경 변수 설정
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
            print(f"<TEST on {test_name}>", flush=True)
        
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
            
            if item == 'UART':
                args_str = f"{args['boadrate']} {args['data']}"
            elif item == 'WIFI':
                args_str = f"{args['ssid']} {args['min']} {args['max']} {args['password']} {args['address']}"
            elif item == 'ETH':
                skip_mac_check_flag = "--skip-mac-check" if config[item]['auto'] else ""
                args_str = f"{args['address']} {args['mac']} {skip_mac_check_flag}".strip()
            # elif item == 'BLUETOOTH':
            #     args_str = f"{args['mac']} {args['min']} {args['max']}"
            elif item == 'VERSION':
                args_str = f"\"{args['app']}\" {args['kernel']} {args['ram']} {args['serial']} {args['model']}"
            elif item == 'LCD':
                # LCD 테스트를 위한 인자 설정
                auto_flag = config[item].get('auto', False)
                args_str = f"--auto" if auto_flag else ""
            elif item == 'PWM':
                auto_flag = config[item].get('auto', False)
                args_str = f"--auto" if auto_flag else ""
            elif item == 'RTC':
                auto_flag = config[item].get('auto', False)
                args_str = f"--default-time" if auto_flag else ""
            elif item == 'USB':
                auto_flag = config[item].get('auto', False)
                #print(f"USB auto flag: {auto_flag}")
                args_str = f"--usb-test" if auto_flag else ""

                com_flag = config[item].get('uart-1', False)
                #print(f"USB 485 check flag: {com_flag}")
                if com_flag:
                    args_str += " --check-485-1"
                com_flag2 = config[item].get('uart-2', False)
                #print(f"USB 485 check flag: {com_flag}")
                if com_flag2:
                    args_str += " --check-485-2"    
                
            else:
                args_str = ''
            
            script_path = os.path.abspath(f"/lg_rw/fct_test/{script}")
            
            # 디버깅을 위한 추가 코드
            if not os.path.exists(script_path):
                print(f"Error: The script {script_path} does not exist!")
                return
            if not os.access(script_path, os.R_OK):
                print(f"Error: The script {script_path} is not readable!")
                return
            
            result_code, log_lines = run_test_script(script_path, args_str)
            last_line = log_lines[-1] if log_lines else "No output"
            
            with lock:
                if repeat > 1:
                    test_results[test_name][f'test_{i+1}'] = last_line
                else:   
                    test_results[test_name] = last_line
            
             # 진행률 출력
            # progress = (i + 1) / repeat * 100
            # print(f"Progress: {i + 1}/{repeat} tests completed ({progress:.2f}%)", flush=True)

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

    if item in ['WIFI']:
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


def run_all_tests(scripts):
    total_tests = sum(config[item]['repeat'] for item in scripts if config[item]['enable'])  # 수정된 부분
    completed_tests = 0

    for item, script in scripts.items():
        if config[item]['enable']:
            execute_test(item, script[0])

            # 진행률 업데이트
            completed_tests += config[item]['repeat']
            overall_progress = (completed_tests / total_tests) * 100
            # 진행률 바 완료
            print("----------------------------------------")

    


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

    run_all_tests(test_items)
# 테스트 결과 확인 및 출력
all_tests_passed = True
failed_count = 0
total_count = 0
print("-" * 40)
print("Test Results:")
print("=" * 40)
print("Test       | Result    | Details")
print("=" * 40)

with open(log_file_path, 'a') as log_file:
    for test_name, iterations in test_results.items():
        if isinstance(iterations, dict):
            for iteration, result in iterations.items():
                total_count += 1

                iteration_number = iteration.split('_')[1]  # 'test_1'에서 '1'만 추출
                
                if "OK" not in result:
                    all_tests_passed = False
                    failed_count += 1
                    details = result.split("FAIL", 1)[-1].strip()  # "FAIL" 이후의 내용 추출
                    details = details.strip("()")  # 양 옆의 괄호 제거
                    print(f"{test_name:<6} {iteration_number:<4} | {'':<1} FAIL {'':<1} | {details}")
                    log_file.write(f"{test_name:<6} {iteration_number:<4}| {'':<1} FAIL {'':<1} | {details}\n")
                else:
                    print(f"{test_name:<6} {iteration_number:<4} | {'':<2} OK {'':<2} |")
                    log_file.write(f"{test_name:<6} {iteration_number:<4} | {'':<2} OK {'':<2} |\n")
        else:
            total_count += 1
            if "OK" not in iterations:
                all_tests_passed = False
                failed_count += 1
                details = iterations.split("FAIL", 1)[-1].strip()  # "FAIL" 이후의 내용 추출
                details = details.strip("()")  # 양 옆의 괄호 제거
                print(f"{test_name:<10} | {'':<1} FAIL {'':<1} | {details}")
                log_file.write(f"{test_name:<10} | {'':<1} FAIL {'':<1} | {details}\n")
            else:
                print(f"{test_name:<10} | {'':<2} OK {'':<2} |")
                log_file.write(f"{test_name:<10} | {'':<2} OK {'':<2} |\n")

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
            # /dev 디렉토리에서 FAT32, exFAT, vfat 파일 시스템을 가진 파티션을 찾음
            lsblk_output = subprocess.run("lsblk -o NAME,FSTYPE", shell=True, capture_output=True, text=True).stdout.strip()
            if lsblk_output:
                lines = lsblk_output.splitlines()
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2 and any(fs in parts[1] for fs in ['vfat', 'fat32', 'exfat']):
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
                mount_point = "/lg_rw/fct_test/result"
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
                return True
            else:
                print(f"Verification failed for {dst}. Retrying...")
        except Exception as e:
            print(f"Attempt {attempt + 1}: Failed to copy log file to USB: {e}")
    return False

# USB 장치 찾기
device_name = find_usb_device()

if device_name:
    # USB 장치 마운트
    mount_point = mount_usb(device_name, "/lg_rw/fct_test/result")
    if mount_point:
        # 로그 파일 경로 생성
        usb_full_log_path = os.path.join(mount_point, usb_log_file_path)

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
    print("USB device not found.")"

3.usb_test.py
"import os
import argparse
import time
import serial
import threading
import shutil
import subprocess

# 전역 변수로 결과 플래그 저장
success_flag = True
failed_tests = []
lock = threading.Lock()  # Lock 객체 생성

# 이벤트 객체 생성
master_ready = threading.Event()
slave_ready = threading.Event()

def log(message):
    if args.debug:
        print(f"[log] {message}")

def tx_485_test(port, buf_tx):
    with lock:  # Lock을 사용하여 스레드 동기화
        num_tx = port.write(buf_tx)  # 데이터 전송
        if args.debug:
            print(f"[{port.port}][send] send {num_tx} bytes.")
    return num_tx

def rx_485_test(port, rx_size):
    start_time = time.time()
    buf_rx = bytearray()  # 초기화
    while True:
        recved = port.read(rx_size - len(buf_rx))  # 남은 크기만큼 읽기
        buf_rx += recved
        if len(buf_rx) >= rx_size:
            if args.debug:
                print(f"[{port.port}][recv] Expected {rx_size}, Received {len(buf_rx)}")
            break
        if time.time() - start_time > 2:  # 타임아웃
            if args.debug:
                print("====== Timeout ======")
                print(f"[{port.port}][recv] Expected {rx_size}, Received {len(buf_rx)}")
            break
    return buf_rx

def slave_thread(rs485_port, tx_buf, rx_buf):
    global success_flag
    for j in range(1):  # 반복 횟수를 1로 줄임
        rs485_port.flushInput()
        master_ready.wait()  # 마스터가 준비될 때까지 대기
        rx = rx_485_test(rs485_port, len(rx_buf))
        
        port_name = f"tty{rs485_port.port[-1]}"
        if tx_buf != rx:
            if port_name not in failed_tests:  # 이미 실패 목록에 없는 경우에만 추가
                success_flag = False
                failed_tests.append(port_name)
                if args.debug:
                    print(f"[{j}][{rs485_port.port}][recv]: ", end="")
                    for i in rx:
                        print(f"{i:d}", end=" ")
                    print("\n\n")
        
        rs485_port.flushOutput()
        time.sleep(0.0015)
        tx_485_test(rs485_port, tx_buf)
        slave_ready.set()  # 슬레이브가 데이터를 보냈음을 알림
        master_ready.clear()  # 마스터가 다시 대기 상태로 설정

def master_thread(rs485_port, tx_buf, rx_buf):
    global success_flag
    for j in range(1):  # 반복 횟수를 1로 줄임
        tx_485_test(rs485_port, tx_buf)
        master_ready.set()  # 마스터가 데이터를 보냈음을 알림
        slave_ready.wait()  # 슬레이브가 준비될 때까지 대기
        rs485_port.flushInput()
        rx = rx_485_test(rs485_port, len(rx_buf))
        if tx_buf != rx:
            port_name = f"tty{rs485_port.port[-1]}"
            if port_name not in failed_tests:  # 이미 실패 목록에 없는 경우에만 추가
                success_flag = False
                failed_tests.append(port_name)
                if args.debug:
                    print(f"[{j}][{rs485_port.port}][recv]: ", end="")
                    for i in rx:
                        print(f"{i:d}", end=" ")
                    print("\n\n")
        rs485_port.flushOutput()
        time.sleep(0.0015)
        slave_ready.clear()  # 슬레이브가 다시 대기 상태로 설정

def try_communicate(port1, port2, baudrate, data_size):
    if args.debug:
        print(f"[log] Communicating from {port1} to {port2} and {port2} to {port1}")
    
    rs485_port1 = serial.Serial(port=port1, baudrate=baudrate, timeout=0)
    rs485_port2 = serial.Serial(port=port2, baudrate=baudrate, timeout=0)

    tx_buf = bytearray([0x11 for _ in range(data_size)])
    rx_buf = bytearray(data_size)
    rs485_port1.flushInput()
    rs485_port1.flushOutput()
    rs485_port2.flushInput()
    rs485_port2.flushOutput()

    # 첫 번째 통신: port1이 master, port2가 slave
    threads = [
        threading.Thread(target=master_thread, args=(rs485_port1, tx_buf, rx_buf)),  # port1이 master
        threading.Thread(target=slave_thread, args=(rs485_port2, tx_buf, rx_buf))    # port2가 slave
    ]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

def get_usb_products():
    products = []
    for device in os.listdir('/sys/bus/usb/devices/'):
        try:
            with open(f'/sys/bus/usb/devices/{device}/product', 'r') as f:
                product = f.read().strip()
                products.append(product)
        except FileNotFoundError:
            continue
    return products

def check_usb_expansion():
    # USB 포트 체크
    required_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3']
    missing_ports = [port for port in required_ports if not os.path.exists(port)]

    if missing_ports:
        log(f"Missing USB ports: {', '.join(missing_ports)}")
        return False

    log("All required USB ports are present.")
    return True

def check_usb_expansion_all():
    # USB 포트 체크
    required_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3', '/dev/ttyUSB4', '/dev/ttyUSB5', '/dev/ttyUSB6', '/dev/ttyUSB7']
    missing_ports = [port for port in required_ports if not os.path.exists(port)]

    if missing_ports:
        log(f"Missing USB ports: {', '.join(missing_ports)}")
        return False

    log("All required USB ports are present.")
    return True
 
def check_usb_communication_all(baudrate, data_size):
    global success_flag
    try:
        for i in range(3):
            try_communicate('/dev/ttyUSB0', '/dev/ttyUSB1', baudrate, data_size)  # 0과 1 간의 통신
            try_communicate('/dev/ttyUSB2', '/dev/ttyUSB3', baudrate, data_size)  # 2와 3 간의 통신
            try_communicate('/dev/ttyUSB4', '/dev/ttyUSB5', baudrate, data_size)  # 2와 3 간의 통신
            try_communicate('/dev/ttyUSB6', '/dev/ttyUSB7', baudrate, data_size)  # 2와 3 간의 통신
    except Exception as e:
        success_flag = False
        failed_tests.append(f"Communication error: {str(e)}")


def check_usb_communication(baudrate, data_size):
    global success_flag
    try:
        for i in range(3):
            try_communicate('/dev/ttyUSB0', '/dev/ttyUSB1', baudrate, data_size)  # 0과 1 간의 통신
            try_communicate('/dev/ttyUSB2', '/dev/ttyUSB3', baudrate, data_size)  # 2와 3 간의 통신
    except Exception as e:
        success_flag = False
        failed_tests.append(f"Communication error: {str(e)}")

def create_test_file(file_path, size_in_mb):
    try:
        with open(file_path, 'wb') as f:
            f.write(os.urandom(size_in_mb * 1024 * 1024))  # 랜덤 데이터로 파일 생성
        log(f"Test file created: {file_path}")
    except Exception as e:
        log(f"Failed to create test file: {e}")

def compare_files(file1, file2):
    try:
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            return f1.read() == f2.read()
    except Exception as e:
        log(f"Failed to compare files: {e}")
        return False

def copy_test_file(src, dst):
    try:
        shutil.copy(src, dst)
        log(f"Test file copied to USB: {dst}")
        return True
    except Exception as e:
        log(f"Failed to copy test file to USB: {e}")
        return False

def usb_test(mount_point, file_size):
    global success_flag
    device_name = find_usb_device()
    if device_name:
        mount_usb(device_name, mount_point)
        test_file_path = os.path.join(mount_point, 'usb_test_file.bin')
        create_test_file(test_file_path, file_size)
        copied_file_path = os.path.join(mount_point, 'usb_test_file_copy.bin')
        if copy_test_file(test_file_path, copied_file_path):
            if compare_files(test_file_path, copied_file_path):
                log("USB test file copied and verified successfully.")
            else:
                success_flag = False
                failed_tests.append("Verification failed for the copied file.")
        unmount_usb(mount_point)
    else:
        success_flag = False
        failed_tests.append("USB device not found.")

def find_usb_device():
    for attempt in range(3):
        try:
            lsblk_output = subprocess.run("lsblk -o NAME,FSTYPE", shell=True, capture_output=True, text=True).stdout.strip()
            if lsblk_output:
                lines = lsblk_output.splitlines()
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2 and any(fs in parts[1] for fs in ['vfat', 'fat32', 'exfat']):
                        device_name = parts[0].strip('`-')
                        return f"/dev/{device_name}"
        except Exception as e:
            log(f"Attempt {attempt + 1}: Failed to find USB device: {e}")
    return None

def is_mounted(device_name, mount_point):
    try:
        result = subprocess.run("mount", shell=True, capture_output=True, text=True).stdout.strip()
        for line in result.splitlines():
            if device_name in line and mount_point in line:
                return True
    except Exception as e:
        log(f"Failed to check if device is mounted: {e}")
    return False

def mount_usb(device_name, mount_point):
    for attempt in range(3):
        try:
            if not os.path.exists(mount_point):
                os.makedirs(mount_point, exist_ok=True)
            if is_mounted(device_name, mount_point):
                log(f"{device_name} is already mounted on {mount_point}")
                return mount_point
            subprocess.run(f"mount {device_name} {mount_point}", shell=True, check=True)
            return mount_point
        except Exception as e:
            log(f"Attempt {attempt + 1}: Failed to mount USB device: {e}")
    return None

def unmount_usb(mount_point):
    for attempt in range(3):
        try:
            subprocess.run(f"umount {mount_point}", shell=True, check=True)
            return True
        except Exception as e:
            log(f"Attempt {attempt + 1}: Failed to unmount USB device: {e}")
    return False

def check_usb_flag():
    try:
        with open('/lg_rw/fct_test/usb_write', 'r') as flag_file:
            flag_content = flag_file.read().strip()
            return flag_content == "1"  # 1이면 성공, 0이면 실패
    except Exception as e:
        log(f"Failed to read USB flag file: {e}")
        return False

def check_led_status():

    global success_flag
    """사용자에게 LED 상태를 확인합니다."""
    if args.check_485_1:
        print("[Q] 2쌍의 LED가 모두 반짝거렸습니까? (y/n 또는 r로 재시도): ")
    if args.check_485_2:    
        print("[Q] 4쌍의 LED가 모두 반짝거렸습니까? (y/n 또는 r로 재시도): ")
    led_status = input().strip().lower()

    if led_status == 'y':
        return False
    elif led_status == 'n':
        failed_tests.append("LED")
        success_flag = False
    elif led_status == 'r':
        print("RS485 통신을 다시 수행합니다...")
        return True  # 재시도 필요
    else:
        print("잘못된 입력입니다. y, n 또는 r을 입력하세요.")
        return False  # 재시도 필요 없음
    return False  # 재시도 필요 없음

def main():
    parser = argparse.ArgumentParser(description='USB Expansion Checker and RS-485 Communication')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--usb-test', action='store_true', help='Perform USB test by writing and verifying a file')
    parser.add_argument('--check-485-1', action='store_true', help='Perform RS-485 communication check', default=False)
    parser.add_argument('--check-485-2', action='store_true', help='Perform RS-485 communication check', default=False)
    parser.add_argument('--mount-point', default='/lg_rw/fct_test/result', help='Mount point for the USB device')
    parser.add_argument('--file-size', type=int, default=1, help='Size of the test file in MB')

    global args
    args = parser.parse_args()

    #확장 모듈 체크 플래그
    usb_expansion_success = True

    # USB 플래그 체크 플래그
    usb_flag_success = True

    # 별도로 앱 다운로드 없이 USB 테스트가 필요한 경우에 수행
    # only 확장 모듈 USB 포트 체크

    if args.check_485_1:
        # USB 통신 체크
        usb_expansion_success = check_usb_expansion()

        while True:
            print("[*] 2쌍의 LED가 깜빡거립니다. LED 상태를 확인해주세요.")
            baudrate = 9600  # 예시로 설정한 baudrate
            data_size = 256   # 예시로 설정한 데이터 크기
            check_usb_communication(baudrate, data_size)
            # LED 상태 확인
            if check_led_status():
                continue
            else:
                break    
    elif args.check_485_2:
        # USB 통신 체크
        usb_expansion_success = check_usb_expansion_all()

        

        while True:
            print("[*] 4쌍의 LED가 깜빡거립니다. LED 상태를 확인해주세요.")
            baudrate = 9600  # 예시로 설정한 baudrate
            data_size = 256   # 예시로 설정한 데이터 크기
            check_usb_communication_all(baudrate, data_size)
            # LED 상태 확인
            if check_led_status():
                continue
            else:
                break
        
    elif args.usb_test:
        usb_test(args.mount_point, args.file_size)

        usb_expansion_success = check_usb_expansion()
        if not usb_expansion_success:
            log("[USB] USB expansion module check failed. Please check the USB ports.")
            failed_tests.append("Expansion Module")

    else: 
        # USB 플래그 체크
        usb_flag_success = check_usb_flag()
        if not usb_flag_success:
            log("[USB] USB flag check failed. Please check the USB connection.")
            failed_tests.append("USB Write")
        usb_expansion_success = check_usb_expansion()
        if not usb_expansion_success:
            log("[USB] USB expansion module check failed. Please check the USB ports.")
            failed_tests.append("Expansion Module")


    # 최종 결과 출력
    if usb_expansion_success and usb_flag_success and success_flag:
        print("[USB] OK")
    else:
        print(f"[USB] FAIL ({', '.join(failed_tests)})")

if __name__ == "__main__":
    main()"


이렇게 3개의 파일이 있는데 수정을 해야해. 근데 어디를 수정해야할지 모르겠어. 

일단 전체 구조를 말해주면, new_cfg.yml 에서 값을 읽어서 그 값을 기반으로 test_start_dq1.py 에서 테스트 파일을 실행시켜.new_cfg.yml 에 USB 부분만 enable true 니까 USB 테스트 스크립트만 실행될거야. 
USB에 해당하는 테스트 스크립트가 usb_test.py 니까, 이게 실행이 될텐데 이거는 "'/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3'" ,  '/dev/ttyUSB4', '/dev/ttyUSB5', '/dev/ttyUSB6', '/dev/ttyUSB7' 이 있는지 확인하고 각각이 485통신을 잘 하는지 , led 가 모두 깜빡거렸는지를 체크해.
내가 바꾸고 싶은건, "'/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3'" 한쌍,   '/dev/ttyUSB4', '/dev/ttyUSB5', '/dev/ttyUSB6', '/dev/ttyUSB7'  한쌍 .. 또 다음에 뭐가 연결된다면 8.9.10.11 뭐 이런식으로 될꺼고 총 3개가 붙은거잖아? 그럴 때에는 각각 파일 로그가 저장되면 좋겠어.

test_start_dq1.py 에 


if check1:

    print("[Q] 1번 확장 보드의 시리얼 번호 입력(스캐너로 큐알을 스캔하세요):")
    label_serial1 = input().strip()          ### CHANGED
    usb_log_file_path = f"expansion_fct_test_{label_serial1}.log"
if check2:
    print("[Q] 1번 확장 보드의 시리얼 번호 입력(스캐너로 큐알을 스캔하세요):")
    label_serial1 = input().strip()          ### CHANGED
    print("[Q] 2번 확장 보드의 시리얼 번호 입력(스캐너로 큐알을 스캔하세요):")
    label_serial2 = input().strip()   
    usb_log_file_path = f"expansion_fct_test_{label_serial1}_{label_serial2}.log"

이런식으로 해서 로그 파일이 생성되도록 했는데 알고보니까 이렇게 하는게 아니었고, 
만약 1개의 확장모듈이 연결된다면"'/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3'" 한쌍,  에 대해서 연결 여부, 485테스트, led 깜빡거림을 검사하고 해당 확장 모듈의 시리얼 넘버를 스캔해서 "expansion_fct_test_{label_serial1}.log" 이름의 파일로 결과를 저장해야해.
그리고 만약 2개의 확장 모듈이 연결된다면 각각의 확장 모듈에 대해서 테스트를 하고 파일이 생상되어야해.
예를 들어서 "'/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3'" 한쌍,  에 대해서 연결 여부, 485테스트, led 깜빡거림을 검사하고 해당 확장 모듈의 시리얼 넘버를 스캔해서 "expansion_fct_test_{label_serial1}.log" 이름의 파일로 결과를 저장해야해.
그리고 그 다음은  '/dev/ttyUSB4', '/dev/ttyUSB5', '/dev/ttyUSB6', '/dev/ttyUSB7'  485테스트, led 깜빡거림을 검사하고 해당 확장 모듈의 시리얼 넘버를 스캔해서 "expansion_fct_test_{label_serial2}.log" 이름의 파일로 결과를 저장해야해.
지금은 2개일 때는 개를 한꺼번에 테스트하고 파일 결과도 같이 저장하는데 분리를해야해. 
어떻게 수정해야할까
