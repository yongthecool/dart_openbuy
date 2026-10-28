import json
import logging
from datetime import datetime
from config import DATA_DIR, SENT_CACHE_FILE

logger = logging.getLogger(__name__)


class ReportStorage:
    def __init__(self, cache_file=SENT_CACHE_FILE):
        self.cache_file = cache_file
        self._ensure_storage()

    def _ensure_storage(self):
        """데이터 저장 폴더 및 캐시 파일이 없으면 생성합니다."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not self.cache_file.exists():
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump({"sent_list": []}, f, ensure_ascii=False, indent=2)

    def _load_data(self) -> dict:
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"캐시 파일 로드 실패 ({e}), 새로 초기화합니다.")
            return {"sent_list": []}

    def _save_data(self, data: dict):
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"캐시 파일 저장 실패: {e}")

    def is_already_sent(self, rcept_no: str) -> bool:
        """해당 접수번호가 이미 발송되었는지 확인합니다."""
        data = self._load_data()
        for item in data.get("sent_list", []):
            if item.get("rcept_no") == rcept_no:
                return True
        return False

    def mark_as_sent(self, report: dict):
        """발송한 공시 정보를 캐시에 추가 저장합니다."""
        data = self._load_data()
        sent_item = {
            "rcept_no": report.get("rcept_no"),
            "corp_name": report.get("corp_name"),
            "report_nm": report.get("report_nm"),
            "sent_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        data.setdefault("sent_list", []).append(sent_item)

        # 최대 1,000건 유지 (오래된 데이터 자동 정리)
        if len(data["sent_list"]) > 1000:
            data["sent_list"] = data["sent_list"][-1000:]

        self._save_data(data)
