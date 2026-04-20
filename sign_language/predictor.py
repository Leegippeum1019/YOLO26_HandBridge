from sign_language.models import BodyFrameFeatures, PredictionResult, SequenceFeatures


GESTURE_RULES = {
    (0, 1, 0, 0, 0): ("one", "\ud558\ub098", 0.72),
    (0, 1, 1, 0, 0): ("two", "\ub458", 0.78),
    (0, 1, 1, 1, 0): ("three", "\uc14b", 0.8),
    (0, 1, 1, 1, 1): ("four", "\ub137", 0.82),
    (1, 1, 1, 1, 1): ("five", "\ub2e4\uc12f", 0.84),
    (1, 0, 0, 0, 0): ("thumbs_up", "\uc88b\uc544\uc694", 0.68),
    (0, 0, 0, 0, 0): ("fist", "\uc8fc\uba39", 0.75),
}


def _predict_hello(
    features: BodyFrameFeatures,
    sequence_features: SequenceFeatures | None = None,
) -> PredictionResult | None:
    if (
        sequence_features
        and sequence_features.wave_detected
        and tuple(features.fingers) == (1, 1, 1, 1, 1)
        and (features.hand_near_head or features.wrist_above_shoulder)
    ):
        return PredictionResult(
            label="\uc548\ub155\ud558\uc138\uc694",
            confidence=0.96,
            gesture_key="hello",
        )

    if (
        tuple(features.fingers) == (1, 1, 1, 1, 1)
        and (features.wrist_above_elbow or features.wrist_above_shoulder)
        and (features.hand_near_head or features.wrist_above_shoulder)
        and features.elbow_angle > 20
    ):
        return PredictionResult(
            label="\uc548\ub155\ud558\uc138\uc694",
            confidence=0.88,
            gesture_key="hello",
        )
    return None


def predict_sign(
    features: BodyFrameFeatures,
    sequence_features: SequenceFeatures | None = None,
) -> PredictionResult | None:
    hello_prediction = _predict_hello(features, sequence_features)
    if hello_prediction:
        return hello_prediction

    gesture = tuple(features.fingers)
    matched = GESTURE_RULES.get(gesture)
    if not matched:
        return None

    gesture_key, label, confidence = matched
    return PredictionResult(
        label=label,
        confidence=confidence,
        gesture_key=gesture_key,
    )
