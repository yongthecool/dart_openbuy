# 📢 DART 공개매수 실시간 텔레그램 알리미 (dart_openbuy)

금융감독원 전자공시시스템(DART)에 **'공개매수'** 관련 공시가 등록되면, 실시간으로 감지하여 **스마트폰 텔레그램으로 푸시 알림**을 보내주는 자동화 프로그램입니다.

---

## 🌟 주요 기능

- ⚡ **실시간 감시**: 1분(설정 가능) 주기로 DART 공시 목록을 모니터링하여 공개매수 공시 포착
- 📱 **텔레그램 알림**: 종목명, 시장구분(코스피/코스닥), 보고서명, 제출인, 공시 본문 바로가기 링크 제공
- 🛡️ **중복 알림 방지**: DART 고유 접수번호(`rcept_no`) 기반 캐싱으로 동일 공시 중복 전송 방지
- 🔒 **보안 유지**: API 키 및 텔레그램 토큰은 `.gitignore`에 등록된 `.env`로 안전하게 분리
- 🧪 **테스트 모드**: 텔레그램 발송 및 최근 공시 검색 테스트 CLI 지원

---

## 📁 프로젝트 구조

```text
dart_openbuy/
├── .env                  # 개인 API 키 및 토큰 (Git에 업로드되지 않음)
├── .env.example          # 환경변수 설정 예시 파일
├── .gitignore            # Git 추적 제외 설정
├── requirements.txt      # 파이썬 의존성 패키지
├── config.py             # 설정 로더 및 검증
├── dart_client.py        # OpenDART API 연동 및 키워드 필터링
├── telegram_bot.py       # 텔레그램 알림 발송 및 메시지 포맷팅
├── storage.py            # 발송 이력 캐시 저장소 (중복 방지)
├── main.py               # 메인 실행 및 스케줄러
└── data/
    └── sent_reports.json # 발송 완료된 접수번호 이력 (자동 생성)
```

---

## 🔑 사전 준비 사항

### 1. OpenDART API 인증키 발급 (무료, 즉시 발급)
1. [OpenDART 웹사이트](https://opendart.fss.or.kr/) 접속 후 회원가입
2. 상단 메뉴 [인증키 신청/관리] > [인증키 신청] 클릭
3. 인증키 신청 후 발급된 **32자리 API 키** 복사

### 2. 텔레그램 봇 토큰 및 Chat ID 확인
1. 텔레그램 앱에서 `@BotFather` 검색 후 채팅 시작
2. `/newbot` 입력 후 봇 이름 및 아이디(예: `my_dart_alarm_bot`) 생성
3. 발급된 **HTTP API 토큰** 복사
4. 방금 만든 내 봇을 찾아 채팅창을 열고 **`/start`** 메시지 전송
5. 내 Chat ID 확인: 텔레그램에서 `@userinfobot` 검색 후 시작하면 본인의 **`Id`**(숫자) 확인 가능

---

## 🚀 설치 및 사용 방법

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정
`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 발급받은 키를 입력합니다.
```bash
# Windows CMD
copy .env.example .env
```
`.env` 파일 내용 편집:
```env
DART_API_KEY=발급받은_OPENDART_API_키
TELEGRAM_BOT_TOKEN=발급받은_텔레그램_봇_토큰
TELEGRAM_CHAT_ID=확인한_본인_숫자_CHAT_ID
CHECK_INTERVAL_SECONDS=60
SEARCH_KEYWORDS=공개매수
SEND_STARTUP_MESSAGE=True
```

### 3. 기능 테스트
```bash
# 텔레그램 발송 테스트 (스마트폰으로 테스트 메시지가 도착하는지 확인)
python main.py --test-tg

# 최근 14일간 등록된 공개매수 공시 조회 테스트
python main.py --test-dart --days 14
```

### 4. 실시간 모니터링 시작
```bash
python main.py
```

---

## 🐙 GitHub 연동 방법

본 프로젝트의 소스코드를 본인의 GitHub 저장소에 연동하는 방법입니다. (`.env` 파일은 `.gitignore`에 등록되어 있어 민감 정보가 외부에 노출되지 않습니다.)

### 1. 로컬 Git 저장소 초기화 및 첫 커밋
```cmd
cmd /c git init
cmd /c git add .
cmd /c git commit -m "feat: DART 공개매수 실시간 텔레그램 알리미 초기 구성"
```

### 2. GitHub 새 저장소(Repository) 생성
1. [GitHub](https://github.com/) 로그인 후 우측 상단 **[+ New repository]** 클릭
2. Repository name 입력 (예: `dart-openbuy-notifier`)
3. 공개 범위(Public 또는 Private) 선택 후 **[Create repository]** 클릭 (README 등 체크하지 마세요)

### 3. 원격 저장소 연결 및 Push
```cmd
# 기본 브랜치를 main으로 설정
cmd /c git branch -M main

# GitHub 저장소 URL 연결 (본인 저장소 주소로 변경)
cmd /c git remote add origin https://github.com/<사용자아이디>/<저장소이름>.git

# GitHub에 푸시
cmd /c git push -u origin main
```
*(GitHub 로그인 창이나 Personal Access Token(PAT) 입력 창이 나타나면 인증을 완료합니다.)*

---

## 💡 상시 실행 팁

1. **로컬 백그라운드 실행 (Windows)**
   - `pythonw main.py` 명령어로 콘솔 창 없이 백그라운드에서 실행 가능합니다.
   - PC 부팅 시 자동 시작하려면 `시작프로그램(shell:startup)` 폴더에 배치 파일(`.bat`) 바로가기를 등록해두면 편리합니다.

2. **클라우드 서버 배포**
   - GitHub에 코드가 연동되어 있으므로 AWS EC2 프리티어, Oracle Cloud Always Free, 또는 Render/Fly.io 등의 가상서버에서 `git clone` 후 24시간 안정적으로 구동할 수 있습니다.
