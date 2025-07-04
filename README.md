오류의 핵심은 아래 두 가지입니다:

⸻

🔐 1. Keyring 관련 오류 (libsecret_error: Failed to unlock the keyring)
	•	PlatformException(Libsecret error, Failed to unlock the keyring) 에서 발생.
	•	libsecret은 Linux 환경에서 로그인 정보 등 민감 데이터를 저장하는 Gnome Keyring(또는 Secret Service)을 사용하는데, 현재 Keyring 잠금을 해제하지 못해 로그인 정보를 읽지 못하고 있습니다.

해결 방법:
	1.	Keyring 데몬이 실행 중인지 확인

ps aux | grep gnome-keyring


	2.	Keyring unlock 처리
수동 unlock:

secret-tool store --label='test' my test

혹은 앱에서 자동 로그인 시도 전에 unlock 로직 필요.

	3.	해결 우회
테스트 용도라면 환경 변수로 저장된 패스워드 사용도 가능 (보안상 권장X):

String? ip = Platform.environment['ACPI_IP'];



⸻

🧩 2. 503 에러 및 DioException
	•	https://10.175.195.66:9300/api/v1/admin 요청이 실패하면서 503 발생
	•	내부적으로는 keyring unlock 실패 → accessToken 획득 실패 → 인증 헤더 없이 API 요청 → 인증 필요 API 503 반환 흐름입니다.

해결 방법:
	1.	Keyring unlock 문제 해결 후 재시도
위 문제를 해결하면 이 문제도 같이 해결될 가능성 높음.
	2.	임시 accessToken 하드코딩 테스트 (비추천)
인증 절차 우회하여 서버 응답을 확인하려면:

headers: {
  'Authorization': 'Bearer <테스트용 토큰>',
}



⸻

✨ 보너스: GTK 오류
	•	Gtk-Message: Failed to load module "canberra-gtk-module"
이는 UI 사운드 관련 모듈이 없다는 경고로, 기능엔 지장 없음
필요 시 다음으로 설치 가능:

sudo apt-get install libcanberra-gtk-module libcanberra-gtk3-module



⸻

✅ 요약

문제	설명	조치
libsecret_error	Keyring 잠금 해제 실패로 로그인 정보 불러오기 실패	Gnome Keyring 데몬 실행 확인 및 unlock
503 /api/v1/admin	인증 토큰 누락 또는 유효하지 않음	Keyring 문제 해결 후 재시도
GTK 모듈 경고	UI 사운드 모듈 없음	무시 가능 or apt install로 설치


⸻

필요하면 keyring을 사용하지 않고 단순 로컬 저장이나 .env 파일을 활용하는 구조로 바꾸는 것도 가능해요. 필요하면 그렇게 수정하는 방향도 도와줄게요.
