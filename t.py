minzzl@minzzl-HP-Z6-G5-Workstation-Desktop-PC:~/Code/tool.fata_test$ python3 run_sota_memory_test.py  --app-path test_data/com.acp.lcd_1.0.0_all_signed.ipk  --app-id com.acp.lcd  --app-version 1.0.0  --iteration 3  --ip 10.175.195.66  --expected-rss-mib 120  --target-avail-mib 1600
==================================================
      App Install/Uninstall Test Initialized
==================================================
  - App ID: com.acp.lcd
  - App Version: 1.0.0
  - App Path: test_data/com.acp.lcd_1.0.0_all_signed.ipk
  - Total Iterations: 3
  - Target MemAvailable: 1600 MiB
==================================================


---------- [ Iteration 1/3 ] ----------

[MEM] Avail=10609MiB / Total=31730MiB (Warn=4759, Crit=1586, Need≈220) | SwapFree=4852MiB
[MEM] Avail=10612MiB → target 1600MiB, hog 9012MiB
[MEM] Now Avail ≈ 6335MiB
[MEM] Start test at Avail≈4213MiB (target 1600MiB)
[INFO] Initiating application installation for 'com.acp.lcd' (Version: 1.0.0)
[SUCCESS] Application installation request sent successfully. Status: 200
[INFO] Verifying application 'com.acp.lcd' status. Expected: 'ok'
[PASS] Verification successful. Received status: 'ok'
[INFO] App RSS after install: [29] MiB
[INFO] Initiating application uninstallation for 'com.acp.lcd'
[SUCCESS] Application uninstallation request sent successfully. Status: 200
[INFO] Verifying application 'com.acp.lcd' status. Expected: 'err'
[PASS] Verification successful. Received status: 'err'
[RESULT] PASS

이런식으로 진행이 되고 있는데 잘되고 있는건가 ? 
             
