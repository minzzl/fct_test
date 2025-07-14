import subprocess
import json
import time
import sys
import argparse

# 전역 변수 초기화
return_data = ""

def log(message):
    if args.debug:
        print(f"[log] {message}")

def get_wifi_profiles():
    # WiFi 프로파일 목록을 가져오는 명령어 실행
    result = subprocess.run(['luna-send', '-n', '1', '-f', 'luna://com.webos.service.wifi/getprofilelist', '{}'], capture_output=True, text=True)
    data = json.loads(result.stdout)
    if data.get("returnValue"):
        return data
    else:
        log("Failed to retrieve WiFi profiles")
        return None

def delete_wifi_profile(profile_id):
    # 특정 프로파일을 삭제하는 명령어 실행
    result = subprocess.run(['luna-send', '-n', '1', '-f', 'luna://com.webos.service.wifi/deleteprofile', json.dumps({"profileId": profile_id})], capture_output=True, text=True)
    data = json.loads(result.stdout)
    if data.get("returnValue"):
        log(f"Successfully deleted profile with ID {profile_id}")
        return True
    else:
        log(f"Failed to delete profile with ID {profile_id}")
        return False

def connect_to_network(ssid, passKey):
    connect_command = [
        "luna-send", "-n", "1", "-f", "luna://com.webos.service.wifi/connect",
        json.dumps({
            "ssid": ssid,
            "security": {
                "securityType": "psk",
                "simpleSecurity": {
                    "passKey": passKey
                }
            }
        })
    ]
    result = subprocess.run(connect_command, capture_output=True, text=True)
    data = json.loads(result.stdout)
    
    if data.get("returnValue"):
        log(f"Successfully connected to SSID '{ssid}'")
        return True
    else:
        print(f"[WIFI] FAIL (Failed to connect to SSID '{ssid}')")
        return False

def ping_test(targetIp):
    ping_command = ["ping", "-I", "wlan0", "-c", "4", targetIp]
    result = subprocess.run(ping_command, capture_output=True, text=True)
    if result.returncode == 0:
        log("ping OK")
        print("[WIFI] OK")
    else:
        print("[WIFI] FAIL (Ping test failed)")

def find_network(ssid_to_find, min_signal, max_signal, passKey, targetIp):
    global return_data  # 전역 변수 사용을 명시적으로 선언
    return_data = ""  # 초기화
    start_time = time.time()
    while True:
        if time.time() - start_time > 60:
            with open("/lg_rw/fct_test/wlan0_test.log", "a") as log_file:
                log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {return_data}\n")

            # journalctl 로그를 파일로 저장
            current_time = time.strftime('%Y%m%d_%H%M%S')
            journalctl_log_file = f"/lg_rw/fct_test/fail_log_{current_time}.txt"
            subprocess.run(f'journalctl > {journalctl_log_file}', shell=True)

            # demesg 를 파일로 저장
            dmesg_log_file = f"/lg_rw/fct_test/dmesg_log_{current_time}.txt"
            subprocess.run(f'dmesg > {dmesg_log_file}', shell=True)

            # flag 파일 생성
            flag_file = "/lg_rw/fct_test/wlan0_test_fail.flag"
            with open(flag_file, "w") as f:
                f.write("1")

            # /sbin/ifconfig -a wlan0 2>&1 | /usr/bin/awk '/HWaddr/ {print $5}' 출력 값을 파일에 저장
            subprocess.run(f"/sbin/ifconfig -a wlan0 2>&1 | /usr/bin/awk '/HWaddr/ {{print $5}}' > /lg_rw/fct_test/wlan0_test_fail_{current_time}.txt", shell=True)
            

            print("[WIFI] FAIL (Timeout)")
            return
        
        # Execute the luna-send command
        result = subprocess.run(
            ["luna-send", "-n", "1", "-f", "luna://com.webos.service.wifi/findnetworks", "{}"],
            capture_output=True,
            text=True
        )
        
        # Parse the JSON output
        data = json.loads(result.stdout)
        return_data += json.dumps(data, indent=2) + "\n"  # 누적
        
        if data.get("returnValue"):
            networks = data.get("foundNetworks", [])
            for network in networks:
                network_info = network.get("networkInfo", {})
                ssid = network_info.get("ssid")
                if ssid == ssid_to_find:
                    bss_info = network_info.get("bssInfo", [])
                    if bss_info:
                        signal = bss_info[0].get("signal")
                        log(f"Found SSID '{ssid_to_find}' with signal: {signal}")
                        if min_signal <= signal <= max_signal:
                            log(f"Signal {signal} is within the desired range ({min_signal} to {max_signal}).")
                            if connect_to_network(ssid_to_find, passKey):
                                ping_test(targetIp)
                            return
                        else:
                            print(f"[WIFI] FAIL (Signal {signal} is outside the desired range ({min_signal} to {max_signal})).")
                            return
        else:
            print("[WIFI] FAIL (Failed to find networks)")
        
        time.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WiFi network management script.")
    parser.add_argument('ssid', type=str, help='SSID of the WiFi network to connect to')
    parser.add_argument('min_signal', type=int, help='Minimum acceptable signal strength')
    parser.add_argument('max_signal', type=int, help='Maximum acceptable signal strength')
    parser.add_argument('passKey', type=str, help='Password for the WiFi network')
    parser.add_argument('targetIp', type=str, help='Target IP address for ping test')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    profiles = get_wifi_profiles()
    
    if profiles:
        for profile in profiles.get("profileList", []):
            wifi_profile = profile.get("wifiProfile", {})
            ssid = wifi_profile.get("ssid")
            profile_id = wifi_profile.get("profileId")
            
            if ssid == args.ssid:
                log(f"Deleting profile with SSID: {ssid} and Profile ID: {profile_id}")
                if delete_wifi_profile(profile_id):
                    log("Deleted OK")
                break
    
    log("Start to find network")
    find_network(args.ssid, args.min_signal, args.max_signal, args.passKey, args.targetIp)
    
    # 마지막에 프로필 삭제 로직 추가
    if profiles:
        for profile in profiles.get("profileList", []):
            wifi_profile = profile.get("wifiProfile", {})
            ssid = wifi_profile.get("ssid")
            profile_id = wifi_profile.get("profileId")
            
            if ssid == args.ssid:
                log(f"Deleting profile with SSID: {ssid} and Profile ID: {profile_id} after connection")
                delete_wifi_profile(profile_id)
                break
