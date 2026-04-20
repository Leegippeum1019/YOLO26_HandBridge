from collections import Counter, deque

from sign_language.models import PredictionResult


class PredictionStabilizer:
    def __init__(self, window_size: int = 6, min_count: int = 2) -> None:
        self.window_size = window_size
        self.min_count = min_count
        self._history_by_stream: dict[str, deque[str]] = {}
        self._latest_by_stream: dict[str, dict[str, PredictionResult]] = {}

    def _get_history(self, stream_key: str) -> deque[str]:
        if stream_key not in self._history_by_stream:
            self._history_by_stream[stream_key] = deque(maxlen=self.window_size)
        return self._history_by_stream[stream_key]

    def _get_latest_map(self, stream_key: str) -> dict[str, PredictionResult]:
        if stream_key not in self._latest_by_stream:
            self._latest_by_stream[stream_key] = {}
        return self._latest_by_stream[stream_key]

    def update(
        self,
        stream_key: str,
        prediction: PredictionResult | None,
    ) -> PredictionResult | None:
        history = self._get_history(stream_key)
        latest_by_key = self._get_latest_map(stream_key)

        if prediction is None:
            history.append("")
            return None

        history.append(prediction.gesture_key)
        latest_by_key[prediction.gesture_key] = prediction

        counter = Counter(key for key in history if key)
        if not counter:
            return None

        best_key, count = counter.most_common(1)[0]
        if count < self.min_count:
            return None

        return latest_by_key.get(best_key)
