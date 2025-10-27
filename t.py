minzzl@minzzl-HP-Z6-G5-Workstation-Desktop-PC:~/Code/tool.fata_test$ python3 run_sota_memory_test.py \
 --app-path test_data/com.acp.lcd_1.0.0_all_signed.ipk \
 --app-id com.acp.lcd \
 --app-version 1.0.0 \
 --iteration 3 \
 --ip 10.175.195.66 \
 --expected-rss-mib 120 \
 --target-avail-mib 1600
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

[MEM] Avail=12737MiB / Total=31730MiB (Warn=4759, Crit=1586, Need≈220) | SwapFree=2625MiB
[MEM] round#1 Avail=12731MiB, target=1600MiB, diff=11131MiB
[MEM] hog additional ~7791MiB
[MEM] round#2 Avail=12704MiB, target=1600MiB, diff=11104MiB
[MEM] hog additional ~7772MiB
[MEM] round#3 Avail=12697MiB, target=1600MiB, diff=11097MiB
[MEM] hog additional ~7767MiB
[MEM] round#4 Avail=12719MiB, target=1600MiB, diff=11119MiB
[MEM] hog additional ~7783MiB
[MEM] round#5 Avail=12702MiB, target=1600MiB, diff=11102MiB
[MEM] hog additional ~7771MiB
[MEM] round#6 Avail=12746MiB, target=1600MiB, diff=11146MiB
[MEM] hog additional ~7802MiB
[MEM] round#7 Avail=12764MiB, target=1600MiB, diff=11164MiB
[MEM] hog additional ~7814MiB
[MEM] round#8 Avail=12785MiB, target=1600MiB, diff=11185MiB
[MEM] hog additional ~7829MiB
[MEM] Now Avail ≈ 12778MiB (target 1600MiB, tol ±120)
[MEM] Start test at Avail≈12750MiB (target 1600MiB)
[INFO] Initiating application installation for 'com.acp.lcd' (Version: 1.0.0)
[SUCCESS] Application installation request sent successfully. Status: 200
