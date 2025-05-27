[...] SSH connect 192.168.1.101
[v] SSH OK
================ Connection OK ================
[...] Write SN/MAC
[v] SN/MAC OK
[v] Excel Check OK
[...] Write launcher files
[v] launcher OK
[...] Write cfg.yml
[v] cfg OK
[...] Send time 2025-05-27 22:42:14
[v] Time OK
[...] Start FCT
========================================
              TEST IN PROGRESS         
========================================
Log date and time: 2025-05-27 22:40
<TEST on VERSION>
[Q] Input serial :
 
[SW version] : FAIL (Failed to read RAM Disk version: [Errno 2] No such file or directory: '/lg_ro/issue', File serial (bbbbbbbb) ≠ Label ())
----------------------------------------
<TEST on ETH>
[ETH]:OK
----------------------------------------
<TEST on DIO>
[DIO]:FAIL (diff value dio)
----------------------------------------
<TEST on UART>
[485] OK
----------------------------------------
<TEST on USB>
[USB] OK
----------------------------------------
<TEST on TOUCH>
[Q] Are you ready to check the touch key? (y/n):
y
[Q] Please touch key12
[log] key12 touched!
[Q] Please touch key11
[log] key11 touched!
[Q] Please touch key10
[log] key10 touched!
[Touch] OK
----------------------------------------
<TEST on PWM>
[log] The buzzer will sound for 1 seconds.
[PWM]:OK
----------------------------------------
<TEST on LCD>
[log] RGB colors sequentially for 1 seconds each...
[log] Duty cycle will change sequentially for 1 seconds each...
[log] Duty cycle changed successfully in auto mode.
[LCD]: OK
----------------------------------------
<TEST on RTC>
[log] Using default time.
[RTC]: OK
----------------------------------------
<TEST on WIFI>
[WIFI] OK
----------------------------------------
----------------------------------------
Test Results:
========================================
Test       | Result    | Details
========================================
VERSION    |   FAIL   | Failed to read RAM Disk version: [Errno 2] No such file or directory: '/lg_ro/issue', File serial (bbbbbbbb) ≠ Label 
ETH        |    OK    |
DIO        |   FAIL   | diff value dio
UART       |    OK    |
USB        |    OK    |
TOUCH      |    OK    |
PWM        |    OK    |
LCD        |    OK    |
RTC        |    OK    |
WIFI       |    OK    |
----------------------------------------
Total tests: 10, Failed tests: 2
----------------------------------------
**********
[ALL TESTS]: 2 out of 10 tests failed
Log file copied to USB: /lg_rw/fct_test/result/interface_d84fb8066676.log
[v] FCT done
[v] ALL OK – replace board
