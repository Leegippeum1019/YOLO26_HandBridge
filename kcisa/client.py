import os

import requests

from config import KCISA_API_URL, load_env_file
from kcisa.models import KcisaItem, KcisaResponse
from kcisa.parser import parse_kcisa_response


class KcisaSignLanguageClient:
    def __init__(
        self,
        service_key: str | None = None,
        session: requests.Session | None = None,
    ) -> None:
        load_env_file()
        self.service_key = service_key or os.getenv("KCISA_SERVICE_KEY")
        if not self.service_key:
            raise ValueError(
                "KCISA_SERVICE_KEY가 설정되지 않았습니다. "
                ".env 파일에 KCISA_SERVICE_KEY=서비스키 형식으로 추가하세요."
            )
        self.session = session or requests.Session()

    def fetch_life_sign_words(
        self,
        num_of_rows: int,
        page_no: int = 1,
    ) -> KcisaResponse:
        params = {
            "serviceKey": self.service_key,
            "numOfRows": num_of_rows,
            "pageNo": page_no,
        }
        headers = {"accept": "application/json"}

        response = self.session.get(
            KCISA_API_URL,
            params=params,
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
        return parse_kcisa_response(response.json())

    def fetch_all_life_sign_words(
        self,
        num_of_rows: int = 100,
        max_pages: int = 5,
    ) -> list[KcisaItem]:
        all_items: list[KcisaItem] = []
        for page_no in range(1, max_pages + 1):
            response = self.fetch_life_sign_words(
                num_of_rows=num_of_rows,
                page_no=page_no,
            )
            page_items = response.body.items
            if not page_items:
                break

            all_items.extend(page_items)
            total_count = int(response.body.totalCount or "0")
            if total_count and len(all_items) >= total_count:
                break

        return all_items
