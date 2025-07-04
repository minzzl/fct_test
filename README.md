확인 결과, Keyring 문제가 여전히 해결되지 않아 로그인용 secure storage에서 IP 또는 accessToken을 가져오지 못하고 있고, 이로 인해 API 요청도 인증 없이 날아가 503 오류가 계속 발생 중입니다.

⸻

🔥 핵심 원인 다시 정리

원인	내용
🔐 libsecret_error	Gnome Keyring 데몬이 실행되지 않음 또는 unlock되지 않음
🚫 API 요청 실패	토큰이 없어서 /api/v1/admin 요청 시 인증 실패 → 503 반환
🔧 결과	앱 실행 직후 SignInScreen에서 저장된 IP를 못 불러오며 PlatformException 발생


⸻

✅ 해결 방법 (두 가지 중 택 1)

✅ 1. Keyring 환경 구성 (근본 해결)
	1.	필요 패키지 설치

sudo apt update
sudo apt install gnome-keyring libsecret-1-0 libsecret-1-dev seahorse -y


	2.	Keyring 데몬 수동 실행

eval $(gnome-keyring-daemon --start)


	3.	환경 변수 등록 (옵션)

export GNOME_KEYRING_CONTROL
export SSH_AUTH_SOCK


	4.	다시 flutter run -d linux 실행

🧠 만약 root 계정에서 실행 중이라면 Keyring은 기본적으로 동작 안 할 수 있어, 일반 사용자 계정으로 실행하는 게 더 안정적입니다.

⸻

✅ 2. 우회: Keyring 없이 테스트용 기본 IP 설정 (임시)

sign_in_screen.dart 내 _loadSavedIp() 함수 또는 secureStorage.read() 호출 부분을 아래처럼 바꿔보세요:

try {
  ip = await secureStorage.read(key: 'ip');
  if (ip == null) {
    ip = '10.175.195.66'; // 기본값
  }
} catch (e) {
  print('Keyring failed: $e');
  ip = '10.175.195.66'; // fallback 기본 IP
}


⸻

🎯 추가 참고

🔊 GTK 관련 경고
	•	Gtk-Message: Failed to load module "canberra-gtk-module"
→ UI 사운드 모듈 누락으로 무시해도 무방. 원한다면:

sudo apt install libcanberra-gtk-module libcanberra-gtk3-module

🔧 libGL 오류
	•	libGL error: failed to load driver: nouveau
→ GPU 가속 드라이버 문제. 무시 가능하지만 성능 영향 있음. 필요 시 NVIDIA 드라이버 설치 권장.

⸻

✅ 정리

선택지	설명	추천 상황
Keyring 구성	libsecret 기반 저장소 정상 작동	실제 배포 환경 구성 시
Keyring 우회	개발/디버깅 용으로 기본값 사용	지금처럼 root 계정이거나 headless 환경 등


⸻

원하는 방향(근본 해결 vs 테스트 우회)을 알려주시면, 그에 맞게 코드나 설정 더 도와드릴게요.
