def find_network(ssid_to_find, min_signal, max_signal, passKey, targetIp):
   global current_time
   find_log = ""
   found = False
   start_time = time.time()
   while True:
       if time.time() - start_time > 60:
           print("[WIFI] FAIL: Timeout while scanning for networks.")
           save_failure_logs("findnetworks", ssid_to_find, find_log)
           return
       result = subprocess.run(
           ["luna-send", "-n", "1", "-f", "luna://com.webos.service.wifi/findnetworks", "{}"],
           capture_output=True, text=True)
       try:
           data = json.loads(result.stdout)
       except:
           data = {"error": result.stdout}
       find_log += json.dumps(data, indent=2) + "\n"
       if data.get("errorCode") == 5 and data.get("errorText") == "WiFi technology unavailable":
           print("[WIFI] FAIL: WiFi technology unavailable.")
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
                       found = True
                       success, connect_log = connect_to_network(ssid_to_find, passKey)
                       if success:
                           ping_test(targetIp)
                       else:
                           save_failure_logs("connect", ssid_to_find, connect_log)
                       return
       time.sleep(5)
   if not found:
       print("[WIFI] FAIL: SSID not found with acceptable signal strength.")


여기서 
   if not found:
       print("[WIFI] FAIL: SSID not found with acceptable signal strength.")

이 코드까지는 접근 불가능한데
