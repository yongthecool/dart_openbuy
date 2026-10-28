import logging
from datetime import datetime, timedelta
import requests
from config import DART_API_KEY, SEARCH_KEYWORDS

logger = logging.getLogger(__name__)

OPENDART_LIST_URL = "https://opendart.fss.or.kr/api/list.json"


class DartClient:
    def __init__(self, api_key: str = DART_API_KEY):
        self.api_key = api_key

    def fetch_disclosures(self, bgn_de: str, end_de: str, page_no: int = 1, page_count: int = 100) -> list[dict]:
        """
        OpenDART 공시검색 API를 호출하여 공시 목록을 가져옵니다.
        :param bgn_de: 검색시작일자 (YYYYMMDD)
        :param end_de: 검색종료일자 (YYYYMMDD)
        """
        if not self.api_key:
            logger.error("DART API 키가 설정되지 않았습니다.")
            return []

        params = {
            "crtfc_key": self.api_key,
            "bgn_de": bgn_de,
            "end_de": end_de,
            "page_no": page_no,
            "page_count": page_count,
            # pblntf_ty='B'로 한정하지 않고 전체 공시 중 보고서명으로 필터링하여 누락 방지
        }

        try:
            response = requests.get(OPENDART_LIST_URL, params=params, timeout=15)
            data = response.json()

            status = data.get("status")
            if status == "000":
                return data.get("list", [])
            elif status == "013":
                # 조회된 데이터가 없음
                return []
            else:
                message = data.get("message", "알 수 없는 오류")
                logger.warning(f"OpenDART 응답 상태코드: {status}, 메시지: {message}")
                return []
        except Exception as e:
            logger.error(f"OpenDART API 요청 실패: {e}")
            return []

    def filter_openbuy_reports(self, reports: list[dict], keywords: list[str] = None) -> list[dict]:
        """
        공시 목록 중 보고서명(report_nm)에 공개매수 관련 키워드가 포함된 공시만 필터링합니다.
        """
        if keywords is None:
            keywords = SEARCH_KEYWORDS

        matched = []
        for r in reports:
            report_nm = r.get("report_nm", "")
            # 키워드 중 하나라도 포함되어 있는지 확인
            if any(k in report_nm for k in keywords):
                matched.append(r)
        return matched

    def get_today_openbuy_reports(self) -> list[dict]:
        """오늘 등록된 공개매수 관련 공시 목록을 조회합니다."""
        today_str = datetime.now().strftime("%Y%m%d")
        all_reports = self.fetch_disclosures(bgn_de=today_str, end_de=today_str)
        return self.filter_openbuy_reports(all_reports)

    def get_recent_openbuy_reports(self, days: int = 7) -> list[dict]:
        """테스트 및 확인용: 최근 N일간의 공개매수 공시를 조회합니다."""
        end_dt = datetime.now()
        bgn_dt = end_dt - timedelta(days=days)
        bgn_de = bgn_dt.strftime("%Y%m%d")
        end_de = end_dt.strftime("%Y%m%d")

        all_reports = self.fetch_disclosures(bgn_de=bgn_de, end_de=end_de)
        return self.filter_openbuy_reports(all_reports)
