import argparse
import logging
import sys
import time
from datetime import datetime

from config import (
    CHECK_INTERVAL_SECONDS,
    SEND_STARTUP_MESSAGE,
    SEARCH_KEYWORDS,
    validate_config,
)
from dart_client import DartClient
from storage import ReportStorage
from telegram_bot import (
    format_openbuy_message,
    send_telegram_message,
    test_telegram_connection,
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("DartOpenBuy")


def run_test_telegram():
    """텔레그램 봇 연결 테스트를 수행합니다."""
    logger.info("텔레그램 연동 테스트 메시지를 발송합니다...")
    ok = test_telegram_connection()
    if ok:
        logger.info("✅ 텔레그램 테스트 메시지가 정상 발송되었습니다!")
    else:
        logger.error("❌ 텔레그램 발송 실패! .env 파일의 TOKEN과 CHAT_ID를 확인해주세요.")


def run_test_dart(days: int = 7):
    """최근 N일간의 공개매수 공시 조회 테스트를 수행합니다."""
    logger.info(f"최근 {days}일간 등록된 공개매수 공시를 조회합니다...")
    client = DartClient()
    reports = client.get_recent_openbuy_reports(days=days)

    if not reports:
        logger.info(f"최근 {days}일간 등록된 공개매수 공시가 없습니다.")
        return

    logger.info(f"총 {len(reports)}건의 공개매수 관련 공시를 발견했습니다:")
    for i, r in enumerate(reports, 1):
        print(f"[{i}] {r.get('rcept_dt')} | {r.get('corp_name')} | {r.get('report_nm')} | 제출인: {r.get('flr_nm')}")
        print(f"    링크: https://dart.fss.or.kr/dsaf001/main.do?rcpNo={r.get('rcept_no')}")


def monitor_once(client: DartClient, storage: ReportStorage) -> int:
    """당일 공시를 1회 확인하고, 신규 공개매수 공시 발견 시 텔레그램을 발송합니다."""
    reports = client.get_today_openbuy_reports()
    new_sent_count = 0

    for r in reports:
        rcept_no = r.get("rcept_no")
        if not rcept_no:
            continue

        # 이미 발송한 공시인지 확인
        if storage.is_already_sent(rcept_no):
            continue

        corp_name = r.get("corp_name")
        report_nm = r.get("report_nm")
        logger.info(f"🚨 [신규 공개매수 공시 포착] {corp_name} - {report_nm} (접수번호: {rcept_no})")

        # 텔레그램 메시지 생성 및 전송
        msg = format_openbuy_message(r)
        success = send_telegram_message(msg)

        if success:
            # 발송 성공 시 캐시에 기록
            storage.mark_as_sent(r)
            new_sent_count += 1
        else:
            logger.error(f"공시 알림 발송 실패 ({corp_name} - {report_nm})")

    return new_sent_count


def run_daemon():
    """실시간 모니터링 데몬 루프를 실행합니다."""
    # 1. 설정 검증
    errors = validate_config()
    if errors:
        for err in errors:
            logger.error(f"❌ 설정 오류: {err}")
        logger.error("프로그램을 종료합니다. .env 파일을 작성한 후 다시 실행해주세요.")
        sys.exit(1)

    client = DartClient()
    storage = ReportStorage()

    logger.info("=" * 60)
    logger.info("🚀 DART 공개매수 실시간 알리미를 시작합니다.")
    logger.info(f"• 감시 키워드: {', '.join(SEARCH_KEYWORDS)}")
    logger.info(f"• 모니터링 주기: {CHECK_INTERVAL_SECONDS}초")
    logger.info("=" * 60)

    # 봇 시작 알림 전송
    if SEND_STARTUP_MESSAGE:
        send_telegram_message(
            f"🚀 <b>[DART 공개매수 알리미 시작]</b>\n"
            f"• 감시 키워드: <code>{', '.join(SEARCH_KEYWORDS)}</code>\n"
            f"• 모니터링 주기: <code>{CHECK_INTERVAL_SECONDS}초</code>\n"
            f"지금부터 신규 공시가 등록되면 즉시 알림이 발송됩니다."
        )

    # 주기적 모니터링 루프
    while True:
        try:
            now_str = datetime.now().strftime("%H:%M:%S")
            logger.info(f"[{now_str}] DART 당일 공시 확인 중...")

            sent_count = monitor_once(client, storage)
            if sent_count > 0:
                logger.info(f"📢 신규 공개매수 공시 {sent_count}건 알림 발송 완료!")

        except KeyboardInterrupt:
            logger.info("사용자에 의해 모니터링이 중단되었습니다.")
            break
        except Exception as e:
            logger.error(f"모니터링 실행 중 오류 발생: {e}", exc_info=True)

        time.sleep(CHECK_INTERVAL_SECONDS)


def main():
    parser = argparse.ArgumentParser(description="DART 공개매수 실시간 텔레그램 알리미")
    parser.add_argument("--test-tg", action="store_true", help="텔레그램 발송 연동 테스트")
    parser.add_argument("--test-dart", action="store_true", help="최근 N일간 공개매수 공시 조회 테스트")
    parser.add_argument("--days", type=int, default=14, help="공시 조회 테스트 시 검색 기간(일수, 기본: 14일)")

    args = parser.parse_args()

    if args.test_tg:
        run_test_telegram()
    elif args.test_dart:
        run_test_dart(days=args.days)
    else:
        run_daemon()


if __name__ == "__main__":
    main()
