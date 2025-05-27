#!/bin/bash


# LCD 색상 순차적으로 display
display_485() {
    /lg_rw/fct_interface/485_test.sh 9600 256
}

# Duty 사이클 변경 (밝기 조정)
display_dio() {
    /lg_rw/fct_interface/dio_test.sh
}

echo "RS-485 LED will blinke..."

# RGB 색상 순차적으로 display 테스트
while true; do

    display_485
    
    while true; do
        echo "Did you see RS-485 LED blinking? If you want to retry, please input 'r'. (y/n/r): "
        read user_input
        user_input=$(echo "$user_input" | tr '[:upper:]' '[:lower:]')  # 소문자로 변환
        
        if [[ "$user_input" == "y" ]]; then
            break 2
        elif [[ "$user_input" == "n" ]]; then
            echo "[LED]: FAIL"
            exit 1
        elif [[ "$user_input" == "r" ]]; then
            break
        else
            echo -e "\nInvalid input. Please enter 'y', 'n', or 'r'."
        fi
    done
done

echo "DIO LED will blinke..."

# Duty 사이클 변경 테스트
while true; do
    display_dio
    
    while true; do
        echo "Did you see DIO LED blinking? If you want to retry, please input 'r'. (y/n/r):  "
        read user_input
        user_input=$(echo "$user_input" | tr '[:upper:]' '[:lower:]')  # 소문자로 변환
        
        if [[ "$user_input" == "y" ]]; then
            echo "[LED]: OK"
            break 2
        elif [[ "$user_input" == "n" ]]; then
            echo "[LED]: FAIL"
            exit 1
        elif [[ "$user_input" == "r" ]]; then
            break
        else
            echo -e "\nInvalid input. Please enter 'y', 'n', or 'r'."
        fi
    done
done


=> LED 테스트 코드... 485든 dio든 할 때 led가 깜빡이는데 그게 잘 테스트 되었는지 체크해야하는거야



이거를 그냥, 각각 DIO 테스트, 485 테스트에서 분리해서 진행하려고해...

일단 지금껏 DIO 테스트는 이거였는데 여기에 추가해줬으면해..

import subprocess
import time
import sys

# GPIO 핀 번호 설정
DO_PIN = 3  # GPIO3
DI_PIN = 2  # GPIO2

def write_gpio(pin, value):
    try:
        # GPIO 값 쓰기
        subprocess.run(f"echo {value} > /sys/class/gpio/gpio{pin}/value", shell=True, check=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print(f"[log] Failed to write to gpio{pin}", file=sys.stderr)
        print(f"[DIO]:FAIL (Failed to write to gpio{pin})")
        sys.exit(1)

def read_gpio(pin):
    try:
        # GPIO 값 읽기
        result = subprocess.run(f"cat /sys/class/gpio/gpio{pin}/value", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return int(result.stdout.strip())
    except subprocess.CalledProcessError:
        print(f"[log] gpio{pin} does not exist", file=sys.stderr)
        print(f"[DIO]:FAIL (Failed to write to gpio{pin})")
        sys.exit(1)

try:
    # Write DO OFF (0으로 초기화)
    write_gpio(DO_PIN, 0)
    time.sleep(0.5)

    # Write DO ON (DO->DI 1 전송)
    write_gpio(DO_PIN, 1)
    time.sleep(0.5)  # 1초 동안 ON 상태 유지

    # DI 값 확인, 0일 경우 Fail
    if read_gpio(DI_PIN) != 1:
        print("[DIO]:FAIL (diff value dio)")
        sys.exit(1)

    # Write DO OFF (DO->DI 0 전송)
    write_gpio(DO_PIN, 0)
    time.sleep(0.5)

    # DI 값 확인, 0이 아닐 경우 Fail
    if read_gpio(DI_PIN) != 0:
        print("[DIO]:FAIL (diff value dio)")
        sys.exit(1)

    # 모든 작업이 성공적으로 완료되면 OK 출력
    print("[DIO] OK")

except Exception as e:
    print(f"[log] {str(e)}", file=sys.stderr)
    print(f"[DIO]:FAIL ({str(e)})")


그리고 이건 485 테스트 

import subprocess
import sys
import threading
import time
import argparse
import serial
import json

# 전역 변수로 결과 플래그 저장
success_flag = True
failed_tests = []
debug = False  # 디버그 플래그

def run_command(command):
    """주어진 명령어를 실행하고 결과를 반환합니다."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"Error executing command '{command}': {e}")
        return None

def check_command_success(output):
    """명령어 실행 결과가 성공적인지 확인합니다."""
    try:
        result = json.loads(output)
        return result.get("returnValue", False)
    except json.JSONDecodeError:
        return False

def tx_485_test(port, buf_tx):
    num_tx = port.write(buf_tx)  # 데이터 전송
    if debug:
        print(f"[{port.port}][send] send {num_tx}bytes.")
    return num_tx

def rx_485_test(port, rx_size):
    start_time = time.time()
    buf_rx = None
    while True:
        recved = port.read(rx_size)
        if buf_rx is None:
            buf_rx = recved
        else:
            buf_rx += recved
        if rx_size == len(buf_rx):
            if debug:
                print(f"[{port.port}][recv] Expected {rx_size}, Received {len(buf_rx)}")
            break
        if start_time + 2 < time.time():
            if debug:
                print("====== Timeout ======")
                print(f"[{port.port}][recv] Expected {rx_size}, Received {len(buf_rx)}")
            break
    return buf_rx

def slave_thread(rs485_port, tx_buf, rx_buf):
    global success_flag
    for j in range(1):  # 반복 횟수를 1로 줄임
        rs485_port.flushInput()
        rx = rx_485_test(rs485_port, len(rx_buf))
        if tx_buf != rx:
            success_flag = False
            if debug:
                print(f"[{j}][{rs485_port.port}][recv]: ", end="")
                for i in rx:
                    print(f"{i:d}", end=" ")
                print("\n\n")
        else:
            if debug:
                print(f"[{j}][{rs485_port.port}][recv] Data received successfully\n")
        rs485_port.flushOutput()
        time.sleep(0.0015)
        tx_485_test(rs485_port, tx_buf)

def master_thread(rs485_port, tx_buf, rx_buf):
    global success_flag
    for j in range(1):  # 반복 횟수를 1로 줄임
        tx_485_test(rs485_port, tx_buf)
        rs485_port.flushInput()
        rx = rx_485_test(rs485_port, len(rx_buf))
        if tx_buf != rx:
            success_flag = False
            if debug:
                print(f"[{j}][{rs485_port.port}][recv]: ", end="")
                for i in rx:
                    print(f"{i:d}", end=" ")
                print("\n\n")
        else:
            if debug:
                print(f"[{j}][{rs485_port.port}][recv] Data received successfully\n")
        rs485_port.flushOutput()
        time.sleep(0.0015)

def assert_rs485(baudrate, data_size):
    global success_flag
    rs485_port1 = serial.Serial(port="/dev/ttyAMA1", baudrate=baudrate, timeout=0)
    rs485_port2 = serial.Serial(port="/dev/ttyAMA2", baudrate=baudrate, timeout=0)

    tx_buf = bytearray([0x11 for _ in range(data_size)])
    rx_buf = bytearray(data_size)
    rs485_port1.flushInput()
    rs485_port1.flushOutput()
    rs485_port2.flushInput()
    rs485_port2.flushOutput()

    # RS485 통신 전에 lockInstall 명령어 실행
    stop_command = "systemctl stop com.acp.flat.service-appinstalld.service"
    run_command(stop_command)
    
    lock_command = "luna-send -n 1 -f luna://com.b2b.dataManager.service/lockInstall '{}'"
    lock_output = run_command(lock_command)
    if not check_command_success(lock_output):
        print("[log] Failed to lock installation.")
        failed_tests.append("Unlock installation failed.")
        return

    # 첫번째 통신 port1 -> port2
    threads = [
        threading.Thread(target=master_thread, args=(rs485_port1, tx_buf, rx_buf)),
        threading.Thread(target=slave_thread, args=(rs485_port2, tx_buf, rx_buf))
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


    # RS485 통신 후에 unlockInstall 명령어 실행
    unlock_command = "luna-send -n 1 -f luna://com.b2b.dataManager.service/unlockInstall '{}'"
    unlock_output = run_command(unlock_command)
    if not check_command_success(unlock_output):
        print("[log] Failed to unlock installation.")
        failed_tests.append("Unlock installation failed.")
        return
    start_command = "systemctl start com.acp.flat.service-appinstalld.service"
    run_command(start_command)

    if not success_flag:
        failed_tests.append("diff send and recv value")
        success_flag = True  # 다음 테스트를 위해 플래그 초기화
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RS485 communication test")
    parser.add_argument("baudrate", type=int, help="Baud rate for RS485 communication")
    parser.add_argument("data_size", type=int, help="Size of the data to be transmitted")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()
    debug = args.debug
    assert_rs485(args.baudrate, args.data_size)
    # 모든 스레드가 성공했는지 확인
    if not failed_tests:
        print("[485] OK")
        sys.exit(0)
    else:
        print(f"[485] FAIL ({failed_tests[0]})")
