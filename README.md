좋은 로그 공유해주셨어요. 결론부터 말씀드리면:

⸻

❌ 현재 도커 컨테이너에서는 snap을 쓸 수 없습니다.

이유는?

컨테이너 환경은 일반적으로 Systemd init 시스템 없이 동작합니다. 그런데 snapd는 systemd 기반 서비스로 동작하기 때문에 다음과 같은 오류가 발생하는 겁니다:

System has not been booted with systemd as init system (PID 1). Can't operate.

dial unix /run/snapd.socket: connect: no such file or directory


⸻

🚫 snap install flutter --classic은 컨테이너에서 불가능ㅗ

flutter를 snap으로 설치하는 건 일반적인 Ubuntu 데스크탑에서 가능한 방법이고, Docker 컨테이너에서는 snap 기반 설치는 작동하지 않습니다.

⸻

✅ 대안 1: APT 혹은 Git으로 직접 설치

Flutter를 설치하려면 snap 대신 git clone 방식으로 설치하세요:

git clone https://github.com/flutter/flutter.git -b stable
export PATH="$PATH:`pwd`/flutter/bin"
flutter --version

필요하다면 .bashrc에 PATH 추가도 가능합니다.

⸻

✅ 대안 2: Docker 공식 flutter 이미지 사용

Flutter 개발 환경이 필요하다면, 오히려 Flutter가 사전 설치된 Docker 이미지를 쓰는 것이 훨씬 깔끔합니다.

docker run -it --name flutter-dev -v $HOME/flutter-dev:/home/flutter -p 8080:8080 cirrusci/flutter:latest bash

이렇게 하면 flutter, dart 등이 이미 세팅된 컨테이너가 실행됩니다.

⸻

✅ 요약

시도한 것	결과
snap install flutter	❌ systemd 없어서 snap 작동 불가
해결 방법 1	✅ git clone으로 flutter 수동 설치
해결 방법 2	✅ Flutter 사전 설치된 Docker 이미지 사용


⸻

필요하다면 flutter 직접 설치하는 bash 스크립트도 만들어드릴게요. 어떤 방식이 더 나을까요?
	•	A. 지금 컨테이너에 직접 설치 (git 방식)
	•	B. Flutter 전용 이미지 사용해서 새 컨테이너 만들기
