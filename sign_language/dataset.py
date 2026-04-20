import json
from pathlib import Path

from sign_language.models import BodyFrameFeatures, PredictionResult, SequenceFeatures


class SequenceDatasetLogger:
    def __init__(self, output_path: str | None = None) -> None:
        self.output_path = Path(output_path) if output_path else None

    def log(
        self,
        frame_features: BodyFrameFeatures,
        sequence_features: SequenceFeatures,
        prediction: PredictionResult | None,
    ) -> None:
        if not self.output_path:
            return

        record = {
            "frame": frame_features.to_dict(),
            "sequence": sequence_features.to_dict(),
            "prediction": {
                "label": prediction.label,
                "confidence": prediction.confidence,
                "gesture_key": prediction.gesture_key,
            }
            if prediction
            else None,
        }
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
