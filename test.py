dmesg 및 FCT 테스트 시퀀스 공유드립니다. 
dmesg 는 기존 133mhz 적용 전(before), 적용 후(after)에 대해서 각각 첨부하였습니다. 

[FCT sequence]
2-3 번 무한 반복하도록 해놓았습니다.

보드와 PC 를 이더넷으로 연결
ssh 접속하여, 보드 내의 /lg_rw/fct_test/test_start_dq.py 실행 
/test_start_dq.py 에서 /lg_rw/fct_test/wlan0_test.py 실행
 /lg_rw/wlan0_test.py 시퀀스  
scan
[webos nano API] luna://com.webos.service.wifi/findnetworks
connect ( 3회 재시도 로직 포함)
