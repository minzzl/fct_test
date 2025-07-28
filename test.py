
import subprocess
import json
import time
import sys
import argparse
import os

# 전역 변수 초기화
return_data = ""
current_time = ""

def log(message):
    if args.debug:
        print(f"[log] {message}")

def get_wifi_profiles():
    result = subprocess.run(['luna-send', '-n', '1', '-f', 'luna://com.webos.service.wifi/getprofilelist', '{}'],
                            capture_output=True, text=True)
    data = json.loads(result.stdout)
    return data if data.get("returnValue") else None

def delete_wifi_profile(profile_id):
    result = subprocess.run(['luna-send', '-n', '1', '-f',
                             'luna://com.webos.service.wifi/deleteprofile', json.dumps({"profileId": profile_id})],
                            capture_output=True, text=True)
    return json.loads(result.stdout).get("returnValue", False)

def connect_to_network(ssid, passKey, max_retries=3):
    global return_data
    return_data = ""
    for attempt in range(1, max_retries + 1):
        print(f"[WIFI] Attempt {attempt} to connect to SSID '{ssid}'...")
        connect_command = [
            "luna-send", "-n", "1", "-f", "luna://com.webos.service.wifi/connect",
            json.dumps({"ssid": ssid, "security": {"securityType": "psk", "simpleSecurity": {"passKey": passKey}}})
        ]
        result = subprocess.run(connect_command, capture_output=True, text=True)
        data = json.loads(result.stdout)
        return_data += json.dumps(data, indent=2) + "\n"
        if data.get("returnValue"):
            print(f"[WIFI] SUCCESS: Connected to SSID '{ssid}'")
            return True
        else:
            print(f"[WIFI]: Attempt {attempt} failed")
            time.sleep(2)

    save_failure_logs("connect", ssid)
    return False

def ping_test(targetIp):
    result = subprocess.run(["ping", "-I", "wlan0", "-c", "4", targetIp],
                            capture_output=True, text=True)
    print("[WIFI] OK" if result.returncode == 0 else "[WIFI] FAIL (Ping test failed)")

def save_failure_logs(context, ssid):
    global current_time
    flag_file = "/lg_rw/fct_test/wlan0_test_fail.flag"
    with open(flag_file, "w") as f:
        f.write("1")
    log_dir = f"/lg_rw/fct_test/wifi_test_{current_time}_ssid-{ssid.replace(' ', '_')}"
    os.makedirs(log_dir, exist_ok=True)
    with open(f"{log_dir}/{context}.json", "w") as f:
        f.write(return_data)
    subprocess.run(f'journalctl > {log_dir}/journalctl.log', shell=True)
    subprocess.run(f'dmesg > {log_dir}/dmesg.log', shell=True)

def run_normalmode_and_capture_logs(log_dir):
    subprocess.run("dmesg > {}/before_normalmode_dmesg.log".format(log_dir), shell=True)
    subprocess.run("journalctl > {}/before_normalmode_journalctl.log".format(log_dir), shell=True)
    result = subprocess.run(['/usr/etc/normalmode.sh'], capture_output=True, text=True)
    with open(f"{log_dir}/normalmode_output.log", "w") as f:
        f.write(result.stdout + "\n" + result.stderr)
    subprocess.run("dmesg > {}/after_normalmode_dmesg.log".format(log_dir), shell=True)
    subprocess.run("journalctl > {}/after_normalmode_journalctl.log".format(log_dir), shell=True)
    scan_log = []
    start_time = time.time()
    while time.time() - start_time < 60:
        result = subprocess.run(
            ["luna-send", "-n", "1", "-f", "luna://com.webos.service.wifi/findnetworks", "{}"],
            capture_output=True, text=True)
        try:
            scan_log.append(json.loads(result.stdout))
        except:
            scan_log.append({"raw": result.stdout})
        time.sleep(5)
    with open(f"{log_dir}/reproduce_findnetwork.json", "w") as f:
        json.dump(scan_log, f, indent=2)

def find_network(ssid_to_find, min_signal, max_signal, passKey, targetIp):
    global return_data
    global current_time
    return_data = ""
    start_time = time.time()
    while True:
        if time.time() - start_time > 60:
            save_failure_logs("findnetworks", ssid_to_find)
            return

        result = subprocess.run(
            ["luna-send", "-n", "1", "-f", "luna://com.webos.service.wifi/findnetworks", "{}"],
            capture_output=True, text=True)
        try:
            data = json.loads(result.stdout)
        except:
            data = {"error": result.stdout}
        return_data += json.dumps(data, indent=2) + "\n"
        if data.get("errorCode") == 5 and data.get("errorText") == "WiFi technology unavailable":
            log_dir = f"/lg_rw/fct_test/wifi_test_{current_time}_ssid-{ssid_to_find.replace(' ', '_')}"
            os.makedirs(log_dir, exist_ok=True)
            run_normalmode_and_capture_logs(log_dir)
            return
        if data.get("returnValue"):
            networks = data.get("foundNetworks", [])
            for network in networks:
                info = network.get("networkInfo", {})
                ssid = info.get("ssid")
                bss_info = info.get("bssInfo", [])
                if ssid == ssid_to_find and bss_info:
                    signal = bss_info[0].get("signal", 0)
                    if min_signal <= signal <= max_signal:
                        if connect_to_network(ssid_to_find, passKey):
                            ping_test(targetIp)
                            return
        time.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WiFi network diagnostic tool")
    parser.add_argument('ssid', type=str)
    parser.add_argument('min_signal', type=int)
    parser.add_argument('max_signal', type=int)
    parser.add_argument('passKey', type=str)
    parser.add_argument('targetIp', type=str)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    current_time = time.strftime('%Y%m%d_%H%M%S')

    profiles = get_wifi_profiles()
    if profiles:
        for profile in profiles.get("profileList", []):
            ssid = profile.get("wifiProfile", {}).get("ssid")
            pid = profile.get("wifiProfile", {}).get("profileId")
            if ssid == args.ssid:
                delete_wifi_profile(pid)
                break
    find_network(args.ssid, args.min_signal, args.max_signal, args.passKey, args.targetIp)
    profiles = get_wifi_profiles()
    if profiles:
        for profile in profiles.get("profileList", []):
            ssid = profile.get("wifiProfile", {}).get("ssid")
            pid = profile.get("wifiProfile", {}).get("profileId")
            if ssid == args.ssid:
                delete_wifi_profile(pid)
                break


save_failure_logs 를 실행할때, subprocess.run 을 여러곳에서 동시에 사용해서 그런지 다른 파일에 동일 내용이 작성되는 문제가 있어. 이를 방지하려면 어떤 코드를 추가해야할까
