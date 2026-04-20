from sign_language.dataset import SequenceDatasetLogger
from sign_language.models import BodyFrameFeatures, PredictionResult, SequenceFeatures
from sign_language.predictor import predict_sign
from sign_language.sequence import SequenceBuffer
from sign_language.stabilizer import PredictionStabilizer


class RealTimeSignRecognizer:
    def __init__(
        self,
        window_size: int = 16,
        stabilizer_window_size: int = 6,
        stabilizer_min_count: int = 2,
        sequence_log_path: str | None = None,
    ) -> None:
        self.sequence_buffer = SequenceBuffer(window_size=window_size)
        self.stabilizer = PredictionStabilizer(
            window_size=stabilizer_window_size,
            min_count=stabilizer_min_count,
        )
        self.dataset_logger = SequenceDatasetLogger(sequence_log_path)

    def recognize(
        self,
        frame_features: BodyFrameFeatures,
    ) -> tuple[PredictionResult | None, SequenceFeatures]:
        sequence_features = self.sequence_buffer.update(frame_features)
        raw_prediction = predict_sign(frame_features, sequence_features)
        prediction = self.stabilizer.update(
            frame_features.hand_label,
            raw_prediction,
        )
        self.dataset_logger.log(frame_features, sequence_features, prediction)
        return prediction, sequence_features
