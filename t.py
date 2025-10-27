minzzl@minzzl-HP-Z6-G5-Workstation-Desktop-PC:~/Code/tool.fata_test$ python3 run_sota_memory_test.py --app-path test_data/com.acp.lcd_1.0.0_all_signed.ipk --app-id com.acp.lcd --app-version 1.0.0 --iteration 3 --ip 10.175.195.66  --expected-rss-mib 120
==================================================
      App Install/Uninstall Test Initialized
==================================================
  - App ID: com.acp.lcd
  - App Version: 1.0.0
  - App Path: test_data/com.acp.lcd_1.0.0_all_signed.ipk
  - Total Iterations: 3
==================================================

---------- [ Iteration 1/3 ] ----------

[MEM] SAFE | Avail=11007MiB / Total=31730MiB (Warn=4759, Crit=1586, Need=220) | SwapFree=4806MiB
[INFO] Initiating application installation for 'com.acp.lcd' (Version: 1.0.0)
[SUCCESS] Application installation request sent successfully. Status: 200
[INFO] Verifying application 'com.acp.lcd' status. Expected: 'ok'
[PASS] Verification successful. Received status: 'ok'
[INFO] App RSS after install: [29] MiB
--------------------
[INFO] Initiating application uninstallation for 'com.acp.lcd'
[SUCCESS] Application uninstallation request sent successfully. Status: 200
[INFO] Verifying application 'com.acp.lcd' status. Expected: 'err'
[PASS] Verification successful. Received status: 'err'


---------- [ Iteration 2/3 ] ----------

[MEM] SAFE | Avail=11209MiB / Total=31730MiB (Warn=4759, Crit=1586, Need=220) | SwapFree=4806MiB
[INFO] Initiating application installation for 'com.acp.lcd' (Version: 1.0.0)
[SUCCESS] Application installation request sent successfully. Status: 200
[INFO] Verifying application 'com.acp.lcd' status. Expected: 'ok'
[PASS] Verification successful. Received status: 'ok'
[INFO] App RSS after install: [29] MiB
--------------------
[INFO] Initiating application uninstallation for 'com.acp.lcd'
[SUCCESS] Application uninstallation request sent successfully. Status: 200
[INFO] Verifying application 'com.acp.lcd' status. Expected: 'err'
[PASS] Verification successful. Received status: 'err'


---------- [ Iteration 3/3 ] ----------

[MEM] SAFE | Avail=11195MiB / Total=31730MiB (Warn=4759, Crit=1586, Need=220) | SwapFree=4806MiB
[INFO] Initiating application installation for 'com.acp.lcd' (Version: 1.0.0)
[SUCCESS] Application installation request sent successfully. Status: 200
[INFO] Verifying application 'com.acp.lcd' status. Expected: 'ok'
[PASS] Verification successful. Received status: 'ok'
[INFO] App RSS after install: [29] MiB
--------------------
[INFO] Initiating application uninstallation for 'com.acp.lcd'
[SUCCESS] Application uninstallation request sent successfully. Status: 200
[INFO] Verifying application 'com.acp.lcd' status. Expected: 'err'
[PASS] Verification successful. Received status: 'err'

메모리가 다음과 같이 관측이 될때, 우리가 진짜 가용 메모리 한계치에서 테스트하려면 어떻게 해야할까

