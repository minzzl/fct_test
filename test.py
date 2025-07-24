import subprocess
import json
import time
import sys
import argparse
import os

# 전역 변수 초기화
return_data = ""
reload_return_data = ""  # [ADDED] 드라이버 리로드 후 결과 저장
current_time =""

def log(message):
    if args.debug:
        print(f"[log] {message}")

def reload_driver(log_dir):
   log("[driver] Reloading WiFi driver...")
   env = os.environ.copy()
   env["PATH"] += os.pathsep + "/sbin"
   commands = [
       '/usr/etc/normalmode.sh'
   ]
   output_log = []
   for cmd in commands:
       result = subprocess.run(cmd, shell=True, env=env, capture_output=True, text=True)
       output_log.append(f"$ {cmd}\n{result.stdout}{result.stderr}\n")
       # sleep between certain commands
      
   # 저장

   with open(os.path.join(log_dir, "reload_driver_output.log"), "w") as f:
        f.write("\n".join(output_log))

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

def connect_to_network(ssid, passKey, max_retries=3):
    global return_data  # 전역 변수 사용을 명시적으로 선언
    return_data = ""  # 초기화
    start_time = time.time()
    for attempt in range(1, max_retries + 1):
        print(f"[WIFI] Attempt {attempt} to connect to SSID '{ssid}'...")

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
        return_data += json.dumps(data, indent=2) + "\n"  # 누적
        
        if data.get("returnValue"):
            print(f"[WIFI] SUCCESS: Connected to SSID '{ssid} after {attempt} to try'")
            return True
        else:
            print(f"[WIFI]: Could not connect on attempt {attempt}")
            time.sleep(2) 

    print(f"[WIFI] FAIL: Failed to connect to SSID '{ssid}' after {max_retries} attempts.")
    flag_file = "/lg_rw/fct_test/wlan0_test_fail.flag"
    with open(flag_file, "w") as f:
        f.write("1")
 
        current_time = time.strftime('%Y%m%d_%H%M%S')  # [MODIFIED]
        log_dir = f"/lg_rw/fct_test/wifi_test_{current_time}_ssid-{ssid.replace(' ', '_')}"  # [ADDED]
        os.makedirs(log_dir, exist_ok=True)  # [ADDED]
        # connect 결과 저장
        with open(f"{log_dir}/connect.json", "w") as f:  # [ADDED]
            f.write(return_data)
        # journalctl 로그 저장
        subprocess.run(f'journalctl > {log_dir}/journalctl.log', shell=True)  # [MODIFIED]
        # dmesg 로그 저장
        subprocess.run(f'dmesg > {log_dir}/dmesg.log', shell=True)  # [MODIFIED]
        time.sleep(2)
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
    global current_time
    global return_data  # 전역 변수 사용을 명시적으로 선언
    global reload_return_data
    driver_reload_needed = False  # [ADDED] 드라이버 리로드 필요 여부 플래그
    return_data = ""  # 초기화
    start_time = time.time()
    while True:
        if time.time() - start_time > 60:
           # flag 파일 생성
           flag_file = "/lg_rw/fct_test/wlan0_test_fail.flag"
           with open(flag_file, "w") as f:
               f.write("1")

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
               f.write(f"Driver Reloaded: {'Yes' if driver_reload_needed else 'No'}\n")  # [ADDED]
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
        
        # [ADDED] 에러코드 5 처리 (WiFi 기술 사용 불가)
        if data.get("errorCode") == 5 and data.get("errorText") == "WiFi technology unavailable":
           log("[driver] WiFi technology unavailable - reloading driver...")
           log_dir = f"/lg_rw/fct_test/wifi_test_{current_time}_ssid-{ssid_to_find.replace(' ', '_')}"
           os.makedirs(log_dir, exist_ok=True)
           reload_driver(log_dir=log_dir)  # 로그 저장용 디렉토리 전달
           driver_reload_needed = True
           # 재시도
           retry_result = subprocess.run(
               ["luna-send", "-n", "1", "-f", "luna://com.webos.service.wifi/findnetworks", "{}"],
               capture_output=True, text=True
           )
           retry_data = json.loads(retry_result.stdout)
           reload_return_data += json.dumps(retry_data, indent=2) + "\n"
           with open(os.path.join(log_dir, "reload_driver.json"), "w") as f:
               f.write(reload_return_data)
           # [추가] 여전히 실패면 normalmode.sh 실행
           if retry_data.get("errorCode") == 5:
               log("[driver] reload_driver 실패 → normalmode.sh 실행")
               normalmode_result = subprocess.run(
                   ['/usr/etc/normalmode.sh'],
                   capture_output=True, text=True
               )
               with open(os.path.join(log_dir, "normalmode_output.log"), "w") as f:
                   f.write(normalmode_result.stdout + "\n" + normalmode_result.stderr)
               # normalmode 후 findnetwork 재시도
               normal_retry = subprocess.run(
                   ["luna-send", "-n", "1", "-f", "luna://com.webos.service.wifi/findnetworks", "{}"],
                   capture_output=True, text=True
               )
               try:
                   normal_data = json.loads(normal_retry.stdout)
               except:
                   normal_data = {"parseError": normal_retry.stdout}
               with open(os.path.join(log_dir, "normalmode_result.json"), "w") as f:
                   f.write(json.dumps(normal_data, indent=2))
               # 이후에도 실패면 로그 출력만 하고 종료
               if not normal_data.get("returnValue"):
                   print("[WIFI] FAIL (After normalmode)")
                   return
               else:
                   data = normal_data

        
        if data.get("returnValue"):
            networks = data.get("foundNetworks", [])

            # {
            # "subscribed": false,
            # "returnValue": true,
            # "foundNetworks": []
            # }

            # have to check foundNetworks '[]'
            if not networks:
                print("[WIFI] FAIL (No networks found)")
                with open(os.path.join(log_dir, "findNetwork_result.json"), "w") as f:
                    f.write(json.dumps(normal_data, indent=2))
                # journalctl 로그 저장
                subprocess.run(f'journalctl > {log_dir}/empty_findNetwork_journalctl.log', shell=True)  # [MODIFIED]
                # dmesg 로그 저장
                subprocess.run(f'dmesg > {log_dir}/empty_findNetwork_dmesg.log', shell=True)  # [MODIFIED]

            # this is code for bssi print
            for network in networks:
                network_info = network.get("networkInfo", {})

                bss_info = network_info.get("bssInfo", [])
                
                if bss_info:
                    ssid = network_info.get("ssid")
                    print(f"{ssid} -> {bss_info}")
                    
                else:
                    print("[WIFI] FAIL (No BSS info available for the network)")
                    return
            # this is connection code
            for network in networks:
                network_info = network.get("networkInfo", {})

                bss_info = network_info.get("bssInfo", [])

                if bss_info:
                    ssid = network_info.get("ssid")
                    # print(f"{ssid} -> {bss_info}")
                    
                    if ssid == ssid_to_find:
                        if connect_to_network(ssid_to_find, passKey):
                            ping_test(targetIp)
                            return
                else:
                    print("[WIFI] FAIL (No BSS info available for the network)")
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
    current_time = time.strftime('%Y%m%d_%H%M%S')  # [MODIFIED]
    
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



1.remove code driver load, keep code run normalmode
2. normalmode.sh 실행 전의 dmesg and journal log 
3. normalmode.sh 실행 후의 dmesg and journal log 
3. Run API findnetwork in 60 second and print value output of run API to a json file (for make sure issue scan fail can reporduce)


