from kcisa.cache import KcisaCacheRepository
from kcisa.client import KcisaSignLanguageClient
from kcisa.models import KcisaItem
from sign_language.models import PredictionResult, TranslationResult
from sign_language.phrasebook import DAILY_LIFE_PHRASES


class SignLanguageTranslator:
    def __init__(
        self,
        client: KcisaSignLanguageClient | None,
        num_of_rows: int = 50,
        cache_repository: KcisaCacheRepository | None = None,
    ) -> None:
        self.client = client
        self.num_of_rows = num_of_rows
        self.cache_repository = cache_repository
        self._items_cache: list[KcisaItem] | None = None

    def _load_items(self) -> list[KcisaItem]:
        if self._items_cache is None:
            if self.cache_repository:
                cached_items = self.cache_repository.load_items()
                if cached_items:
                    self._items_cache = cached_items
                    return self._items_cache

            if self.client is None:
                self._items_cache = []
                return self._items_cache

            response = self.client.fetch_life_sign_words(
                num_of_rows=self.num_of_rows,
                page_no=1,
            )
            self._items_cache = response.body.items
        return self._items_cache

    def _score_item(self, item: KcisaItem, keyword: str) -> int:
        fields = [
            item.title,
            item.alternativeTitle,
            item.subjectKeyword,
            item.description,
            item.subDescription,
            item.signDescription,
        ]
        score = 0
        keyword_lower = keyword.lower()

        for field in fields:
            value = (field or "").lower()
            if not value:
                continue
            if keyword_lower == value:
                score += 100
            elif keyword_lower in value:
                score += 30

        return score

    def _build_phrase_translation(self, prediction: PredictionResult) -> TranslationResult:
        phrase = DAILY_LIFE_PHRASES.get(prediction.gesture_key, {})
        subtitle_text = phrase.get("subtitle", prediction.label)
        translated_text = phrase.get("translation", prediction.label)
        api_keywords = phrase.get("api_keywords", [])
        api_keyword = api_keywords[0] if api_keywords else prediction.label

        return TranslationResult(
            label=prediction.label,
            confidence=prediction.confidence,
            translated_text=translated_text,
            subtitle_text=subtitle_text,
            api_keyword=api_keyword,
        )

    def translate_prediction(
        self,
        prediction: PredictionResult | None,
    ) -> TranslationResult | None:
        if prediction is None:
            return None

        translation = self._build_phrase_translation(prediction)
        items = self._load_items()
        scored_items = [
            (self._score_item(item, translation.api_keyword), item)
            for item in items
        ]
        scored_items.sort(key=lambda row: row[0], reverse=True)

        best_score, best_item = scored_items[0] if scored_items else (0, None)
        if best_item is None or best_score <= 0:
            return translation

        translated_text = (
            best_item.signDescription
            or best_item.description
            or best_item.subDescription
            or best_item.title
        )

        return TranslationResult(
            label=translation.label,
            confidence=translation.confidence,
            translated_text=translated_text,
            subtitle_text=translation.subtitle_text,
            api_keyword=translation.api_keyword,
            source_title=best_item.title,
            source_description=best_item.description,
        )
