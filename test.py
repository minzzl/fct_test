import os
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
        if tx_buf != rx:
            success_flag = False
            failed_tests.append(f"tty{rs485_port.port[-1]}")
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
            success_flag = False
            failed_tests.append(f"tty{rs485_port.port[-1]}")
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
    print("[Q] 4쌍의 LED가 모두 반짝거렸습니까? (y/n 또는 r로 재시도): ")
    led_status = input().strip().lower()

    if led_status == 'y':
        return False
    elif led_status == 'n':
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
    parser.add_argument('--check-485', action='store_true', help='Perform RS-485 communication check', default=False)
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
    if args.check_485:
        # USB 통신 체크
        usb_expansion_success = check_usb_expansion_all()

        while True:
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
    main()


이거는 --check-485 옵션을 주고 실행 시켰을 때, 왜 led 가 깜빡 거렸냐는걸 묻지 않는걸까 

# LED 상태 확인
            if check_led_status():
                continue
            else:
                break

이 부분이 실행안된늑 것 같아 ?
