import logging
from datetime import datetime, timedelta
import requests
from config import DART_API_KEY, SEARCH_KEYWORDS

logger = logging.getLogger(__name__)

OPENDART_LIST_URL = "https://opendart.fss.or.kr/api/list.json"


class DartClient:
    def __init__(self, api_key: str = DART_API_KEY):
        self.api_key = api_key

    def fetch_disclosures_page(
        self, bgn_de: str, end_de: str, page_no: int = 1, page_count: int = 100, pblntf_ty: str = "D"
    ) -> tuple[list[dict], int]:
        """
        OpenDART 공시검색 API 단일 페이지 호출
        :param pblntf_ty: 'D' (지분공시 - 공개매수는 지분공시에 등록됨)
        :return: (공시목록, 총페이지수)
        """
        if not self.api_key:
            logger.error("DART API 키가 설정되지 않았습니다.")
            return [], 0

        params = {
            "crtfc_key": self.api_key,
            "bgn_de": bgn_de,
            "end_de": end_de,
            "page_no": page_no,
            "page_count": page_count,
        }
        if pblntf_ty:
            params["pblntf_ty"] = pblntf_ty

        try:
            response = requests.get(OPENDART_LIST_URL, params=params, timeout=15)
            data = response.json()

            status = data.get("status")
            if status == "000":
                total_page = int(data.get("total_page", 1))
                return data.get("list", []), total_page
            elif status == "013":
                # 조회 데이터 없음
                return [], 0
            else:
                msg = data.get("message", "알 수 없는 오류")
                logger.warning(f"OpenDART 응답 상태코드: {status}, 메시지: {msg}")
                return [], 0
        except Exception as e:
            logger.error(f"OpenDART API 요청 실패: {e}")
            return [], 0

    def fetch_all_disclosures(self, bgn_de: str, end_de: str, pblntf_ty: str = "D") -> list[dict]:
        """
        해당 기간의 공시를 모든 페이지를 순회하여 가져옵니다 (누락 방지).
        """
        first_page_list, total_page = self.fetch_disclosures_page(
            bgn_de=bgn_de, end_de=end_de, page_no=1, page_count=100, pblntf_ty=pblntf_ty
        )
        all_list = list(first_page_list)

        # 2페이지 이상 존재할 경우 추가 수집 (최대 10페이지 안전 제한)
        for page in range(2, min(total_page + 1, 11)):
            page_list, _ = self.fetch_disclosures_page(
                bgn_de=bgn_de, end_de=end_de, page_no=page, page_count=100, pblntf_ty=pblntf_ty
            )
            all_list.extend(page_list)

        return all_list

    def filter_openbuy_reports(self, reports: list[dict], keywords: list[str] = None) -> list[dict]:
        """
        공시 목록 중 보고서명(report_nm)에 공개매수 관련 키워드가 포함된 공시만 필터링합니다.
        """
        if keywords is None:
            keywords = SEARCH_KEYWORDS

        matched = []
        for r in reports:
            report_nm = r.get("report_nm", "")
            if any(k in report_nm for k in keywords):
                matched.append(r)
        return matched

    def get_today_openbuy_reports(self) -> list[dict]:
        """오늘 등록된 공개매수 관련 공시 목록을 조회합니다."""
        today_str = datetime.now().strftime("%Y%m%d")
        all_reports = self.fetch_all_disclosures(bgn_de=today_str, end_de=today_str, pblntf_ty="D")
        return self.filter_openbuy_reports(all_reports)

    def get_recent_openbuy_reports(self, days: int = 7) -> list[dict]:
        """테스트용: 최근 N일간의 공개매수 공시를 조회합니다."""
        end_dt = datetime.now()
        bgn_dt = end_dt - timedelta(days=days)
        bgn_de = bgn_dt.strftime("%Y%m%d")
        end_de = end_dt.strftime("%Y%m%d")

        all_reports = self.fetch_all_disclosures(bgn_de=bgn_de, end_de=end_de, pblntf_ty="D")
        return self.filter_openbuy_reports(all_reports)
