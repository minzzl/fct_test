wifi_test_20250715_075327_ssid-next_test
fail_log_20250713_091746.txt                           wifi_test_20250715_075731_ssid-next_test
fail_log_20250713_091943.txt                           wifi_test_20250715_075929_ssid-next_test
fail_log_20250713_092243.txt                           wifi_test_20250715_080436_ssid-next_test
fail_log_20250713_092440.txt                           wifi_test_20250715_080943_ssid-next_test
fail_log_20250713_092740.txt                           wifi_test_20250715_081244_ssid-next_test
fail_log_20250713_093040.txt                           wifi_test_20250715_081751_ssid-next_test
fail_log_20250713_093237.txt                           wifi_test_20250715_082051_ssid-next_test
fail_log_20250713_093537.txt                           wifi_test_20250715_082556_ssid-next_test
fail_log_20250713_093734.txt                           wifi_test_20250715_082753_ssid-next_test
fail_log_20250713_093931.txt                           wifi_test_20250715_083054_ssid-next_test
fail_log_20250713_094128.txt                           wifi_test_20250715_083354_ssid-next_test
fail_log_20250713_094324.txt                           wifi_test_20250715_083654_ssid-next_test
fail_log_20250713_094522.txt                           wifi_test_20250715_084200_ssid-next_test
fail_log_20250713_094822.txt                           wifi_test_20250715_084356_ssid-next_test
fail_log_20250713_095123.txt                           wifi_test_20250715_084553_ssid-next_test
fail_log_20250713_095320.txt                           wifi_test_20250715_084853_ssid-next_test
fail_log_20250713_095517.txt                           wifi_test_20250715_085813_ssid-next_test
fail_log_20250713_095817.txt                           wifi_test_20250715_090218_ssid-next_test
fail_log_20250713_100014.txt                           wifi_test_20250715_090415_ssid-next_test
fail_log_20250713_100211.txt                           wifi_test_20250715_090923_ssid-next_test
fail_log_20250713_100408.txt                           wifi_test_20250715_213923_ssid-next_test_connect_fail
fail_log_20250713_100604.txt                           wifi_test_20250715_214124_ssid-next_test
fail_log_20250713_100802.txt                           wifi_test_20250715_214338_ssid-next_test
fail_log_20250713_100959.txt                           wifi_test_20250715_214536_ssid-next_test
fail_log_20250713_101155.txt                           wifi_test_20250715_214734_ssid-next_test
fail_log_20250713_101353.txt                           wifi_test_20250715_214931_ssid-next_test
fail_log_20250713_101550.txt                           wifi_test_20250715_215128_ssid-next_test


[root@webOSNano-unofficial /lg_rw/fct_test]# cat zip.py
import os
import zipfile
# 기준 디렉토리
base_dir = os.getcwd()
# 압축 대상 패턴
prefix = "wifi_test_"
suffix = "_ssid-next_test"
# zip 파일 이름
output_zip = "wifi_all_tests.zip"
# 기존에 잘못 만들어진 zip 파일들 삭제
for file in os.listdir(base_dir):
   if file.endswith(".zip") and file != output_zip:
       if file.startswith(prefix) and file.endswith(suffix + ".zip"):
           os.remove(os.path.join(base_dir, file))
           print(f"[삭제됨] {file}")
# 압축 파일 만들기
with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
   for folder in os.listdir(base_dir):
       full_path = os.path.join(base_dir, folder)
       if os.path.isdir(full_path) and folder.startswith(prefix) and folder.endswith(suffix):
           for root, dirs, files in os.walk(full_path):
               for file in files:
                   file_path = os.path.join(root, file)
                   arcname = os.path.relpath(file_path, start=base_dir)
                   zipf.write(file_path, arcname)
                   print(f"[추가됨] {arcname}")
print(f"\n[완료] {output_zip} 생성 완료 ✅")
