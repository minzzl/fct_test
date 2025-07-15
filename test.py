import subprocess
import json
import time
import sys
import argparse
import os
 
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
           # flag 파일 생성
           flag_file = "/lg_rw/fct_test/wlan0_test_fail.flag"
           with open(flag_file, "w") as f:
               f.write("1")
 
           current_time = time.strftime('%Y%m%d_%H%M%S')  # [MODIFIED]
           log_dir = f"/lg_rw/fct_test/wifi_test_{current_time}_ssid-{ssid_to_find.replace(' ', '_')}"  # [ADDED]
           os.makedirs(log_dir, exist_ok=True)  # [ADDED]
           # findnetworks 결과 저장
           with open(f"{log_dir}/findnetworks.json", "w") as f:  # [ADDED]
               f.write(return_data)
           # journalctl 로그 저장
           subprocess.run(f'journalctl > {log_dir}/journalctl.log', shell=True)  # [MODIFIED]
           # dmesg 로그 저장
           subprocess.run(f'dmesg > {log_dir}/dmesg.log', shell=True)  # [MODIFIED]
           # ifconfig 결과 저장
           subprocess.run(
               f"/sbin/ifconfig -a wlan0 2>&1 | /usr/bin/awk '/HWaddr/ {{print $5}}' > {log_dir}/ifconfig.txt",
               shell=True
           )  # [MODIFIED]
           # 요약 결과 저장
           with open(f"{log_dir}/summary.txt", "w") as f:  # [ADDED]
               f.write(f"SSID: {ssid_to_find}\n")
               f.write(f"Signal: {signal if 'signal' in locals() else 'N/A'}\n")
               f.write("Result: FAIL (Timeout or Signal out of range)\n")
           # 마스터 요약 로그에 한 줄 추가
           with open("/lg_rw/fct_test/test_summary_index.log", "a") as f:  # [ADDED]
               f.write(f"[{current_time}] SSID: {ssid_to_find} - FAIL\n")
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


이 코드에서, find_network 함수 내부에 추가하고 싶은 로직이 있어.
가끔 findnetworks 호출이후의 응답이 다음과 같이 나오는 경우가 있어.

{
  "errorCode": 5,
  "returnValue": false,
  "errorText": "WiFi technology unavailable"
}
이 때의 문제가 드라이버 문제라고 생각하고 있어. 
reload driver -> re-run API -> write log into "../reload_driver.json" 이렇게 추가를 하고 싶은데, 
드라이버를 리로드 하는 명령어는 6단계야.

  subprocess.run('systemctl stop connman', shell=True)
                subprocess.run('rmmod moal', shell=True)
                subprocess.run('rmmod mlan', shell=True)
                subprocess.run('systemctl restart connman', shell=True)
                subprocess.run('insmod /lib/modules/iw61x/extra/mlan.ko', shell=True)
                subprocess.run('insmod /lib/modules/iw61x/extra/moal.ko mod_para=nxp/wifi_mod_para.conf', shell=True)

6단계를 실행하고 나서, 이후의 findnetwork 의 응답으로는 return_data 말고 다른 변수에 누적시켜서, reload_driver.json  파일에 저장되도록 해서, 드라이버 리로드 전과 후의 응답을 구분할 수 있도록 코드를 수정해

