import logging
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

# 시장 구분 코드 한글화
CORP_CLS_MAP = {
    "Y": "유가증권(코스피)",
    "K": "코스닥",
    "N": "코넥스",
    "E": "기타"
}


def send_telegram_message(text: str) -> bool:
    """텔레그램 봇 API를 통해 메시지를 전송합니다."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("텔레그램 토큰 또는 채팅 ID가 설정되지 않았습니다.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        res_data = response.json()
        if response.status_code == 200 and res_data.get("ok"):
            logger.info("텔레그램 알림 발송 성공")
            return True
        else:
            logger.error(f"텔레그램 전송 실패: {res_data}")
            return False
    except Exception as e:
        logger.error(f"텔레그램 API 요청 오류: {e}")
        return False


def format_openbuy_message(report: dict) -> str:
    """공시 정보를 바탕으로 사용자에게 보낼 텔레그램 알림 메시지를 생성합니다."""
    corp_name = report.get("corp_name", "미상")
    corp_cls = CORP_CLS_MAP.get(report.get("corp_cls"), "기타")
    stock_code = report.get("stock_code", "").strip()
    stock_text = f" ({stock_code})" if stock_code else ""
    report_nm = report.get("report_nm", "공시명 없음")
    flr_nm = report.get("flr_nm", "제출인 미상")
    rcept_dt = report.get("rcept_dt", "")
    rcept_no = report.get("rcept_no", "")

    # 날짜 포맷 (YYYYMMDD -> YYYY.MM.DD)
    if len(rcept_dt) == 8:
        formatted_dt = f"{rcept_dt[:4]}.{rcept_dt[4:6]}.{rcept_dt[6:]}"
    else:
        formatted_dt = rcept_dt

    # DART 상세 페이지 바로가기 링크
    dart_url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}"

    msg = (
        f"📢 <b>[DART 공개매수 공시 알림]</b>\n\n"
        f"🏢 <b>대상종목:</b> {corp_name}{stock_text} [{corp_cls}]\n"
        f"📑 <b>보고서명:</b> {report_nm}\n"
        f"👤 <b>제출인:</b> {flr_nm}\n"
        f"📅 <b>접수일자:</b> {formatted_dt}\n\n"
        f"🔗 <b>공시 바로보기:</b>\n"
        f"<a href='{dart_url}'>{dart_url}</a>"
    )
    return msg


def test_telegram_connection() -> bool:
    """텔레그램 연결 상태를 확인하고 테스트 메시지를 전송합니다."""
    msg = (
        "✅ <b>[DART 공개매수 알리미]</b>\n\n"
        "텔레그램 봇 연동 테스트가 성공적으로 완료되었습니다.\n"
        "이제 DART에 공개매수 공시가 등록되면 즉시 알림이 발송됩니다."
    )
    return send_telegram_message(msg)
