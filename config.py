import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# DART API 키
DART_API_KEY = os.getenv("DART_API_KEY", "").strip()

# 텔레그램 설정
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# 체크 주기 (초 단위, 기본 60초)
try:
    CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))
except ValueError:
    CHECK_INTERVAL_SECONDS = 60

# 검색 키워드 목록
raw_keywords = os.getenv("SEARCH_KEYWORDS", "공개매수")
SEARCH_KEYWORDS = [k.strip() for k in raw_keywords.split(",") if k.strip()]

# 봇 시작 안내 메시지 전송 여부
SEND_STARTUP_MESSAGE = os.getenv("SEND_STARTUP_MESSAGE", "True").lower() in ("true", "1", "yes")

# 발송 이력 저장 경로
DATA_DIR = BASE_DIR / "data"
SENT_CACHE_FILE = DATA_DIR / "sent_reports.json"


def validate_config() -> list[str]:
    """필수 환경변수가 설정되어 있는지 검증합니다."""
    errors = []
    if not DART_API_KEY or DART_API_KEY == "your_opendart_api_key_here":
        errors.append("DART_API_KEY 가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
        errors.append("TELEGRAM_BOT_TOKEN 이 설정되지 않았습니다. .env 파일을 확인해주세요.")
    if not TELEGRAM_CHAT_ID or TELEGRAM_CHAT_ID == "your_chat_id_here":
        errors.append("TELEGRAM_CHAT_ID 가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    return errors
