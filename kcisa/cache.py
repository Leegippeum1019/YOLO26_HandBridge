import json
from pathlib import Path

from kcisa.client import KcisaSignLanguageClient
from kcisa.models import KcisaItem


def _item_to_dict(item: KcisaItem) -> dict:
    return item.__dict__.copy()


def _dict_to_item(data: dict) -> KcisaItem:
    return KcisaItem(**data)


class KcisaCacheRepository:
    def __init__(self, cache_path: str) -> None:
        self.cache_path = Path(cache_path)

    def load_items(self) -> list[KcisaItem]:
        if not self.cache_path.exists():
            return []

        payload = json.loads(self.cache_path.read_text(encoding="utf-8"))
        return [_dict_to_item(item) for item in payload.get("items", [])]

    def save_items(self, items: list[KcisaItem], metadata: dict | None = None) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "metadata": metadata or {},
            "items": [_item_to_dict(item) for item in items],
        }
        self.cache_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def build_from_api(
        self,
        client: KcisaSignLanguageClient,
        num_of_rows: int,
        max_pages: int,
    ) -> list[KcisaItem]:
        items = client.fetch_all_life_sign_words(
            num_of_rows=num_of_rows,
            max_pages=max_pages,
        )
        self.save_items(
            items,
            metadata={
                "num_of_rows": num_of_rows,
                "max_pages": max_pages,
                "item_count": len(items),
            },
        )
        return items
