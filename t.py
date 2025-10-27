minzzl@minzzl-HP-Z6-G5-Workstation-Desktop-PC:~/Code/tool.fata_test$ python3 run_sota_memory_test.py \
 --app-path test_data/com.acp.lcd_1.0.0_all_signed.ipk \
 --app-id com.acp.lcd \
 --app-version 1.0.0 \
 --iteration 3 \
 --ip 10.175.195.66 \
 --expected-rss-mib 120 \
 --target-avail-mib 1600
Traceback (most recent call last):
  File "/home/minzzl/Code/tool.fata_test/run_sota_memory_test.py", line 28, in <module>
    def get_rss_by_name(app_id: str) -> List[int]:
                                        ^^^^
NameError: name 'List' is not defined. Did you mean: 'list'?
