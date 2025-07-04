좋아요, 이건 딱 봐도 flutter SDK가 비정상적인 상태로 설치된 cirrusci 이미지에서 흔히 생기는 문제예요.

요약: cirrusci/flutter:latest 이미지 내부 Flutter는 정상적인 Git 저장소가 아님 → flutter upgrade, flutter channel 불가 ❌

⸻

🎯 해결책: 최신 Flutter SDK를 직접 설치해서 덮어쓰기

이 방법이 가장 확실하고 깨끗해요.

⸻

✅ 1. 기존 Flutter SDK 무시하고 새로 설치

도커 안에서 아래 순서로 실행하세요:

① /opt 등 안전한 경로로 이동

cd /opt

② 최신 flutter clone 받기

git clone https://github.com/flutter/flutter.git -b stable

③ flutter 최신 경로를 PATH에 추가

export PATH="/opt/flutter/bin:$PATH"

(※ 임시 적용이므로, 필요하면 .bashrc에 추가)

⸻

✅ 2. 설치 확인 및 프로젝트 실행

① 확인

flutter --version
flutter doctor

→ Dart 3.3.x 이상, Flutter 최신 stable인지 확인

② 프로젝트 실행

cd ~/lgsi-homelauncher
flutter pub get
flutter run -d linux


⸻

📦 선택사항: 아예 Dockerfile로 만들고 싶다면?

아래는 간단한 예시입니다:

FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    git curl unzip xz-utils zip libglu1-mesa libgtk-3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/flutter/flutter.git -b stable /opt/flutter
ENV PATH="/opt/flutter/bin:/opt/flutter/bin/cache/dart-sdk/bin:${PATH}"

RUN flutter doctor

WORKDIR /app

이걸로 docker build 하시면 항상 최신 Flutter가 깔린 컨테이너 생성 가능!

⸻

✅ 요약

문제	해결
flutter upgrade, channel 실패	cirrusci 이미지의 Flutter가 불완전해서 생긴 문제
해결 방법	최신 Flutter Git clone 받아서 직접 설치 (/opt/flutter)
부가 방법	Dockerfile로 직접 최신 환경 구성 가능


⸻

이제 /opt에 새 Flutter 설치하고 PATH 잡아서 돌려보시면 거의 100% 해결돼요.
필요하면 .bashrc, Dockerfile, 자동 설정도 도와드릴게요!
원하시면 한 줄씩 함께 해드릴게요 :)
