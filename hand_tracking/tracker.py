import cv2
import mediapipe as mp

from hand_tracking.logic import angle_2d, distance_2d, get_finger_states
from hand_tracking.rendering import draw_panel, draw_subtitle_banner, draw_text
from sign_language.models import (
    BodyFrameFeatures,
    PredictionResult,
    SequenceFeatures,
    TranslationResult,
)
from sign_language.recognizer import RealTimeSignRecognizer
from sign_language.translator import SignLanguageTranslator


mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
)
pose = mp_pose.Pose(
    static_image_mode=False,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
)


def _draw_translation(frame, translation: TranslationResult, y_base: int) -> None:
    confidence_text = f"{translation.confidence:.2f}"
    draw_text(
        frame,
        f"Predict: {translation.label} ({confidence_text})",
        (24, y_base - 22),
        font_size=24,
        color=(0, 165, 255),
    )

    preview_text = translation.translated_text[:40]
    draw_text(
        frame,
        f"Translate: {preview_text}",
        (24, y_base + 10),
        font_size=22,
        color=(255, 255, 255),
    )


def _draw_status_card(
    frame,
    index: int,
    display_label: str,
    finger_count: int,
    debug_text: str,
    sequence_features: SequenceFeatures,
    prediction: PredictionResult | None,
    translation: TranslationResult | None,
) -> None:
    column = index % 2
    row = index // 2
    card_x = 16 + (column * 446)
    card_y = 84 + (row * 180)
    card_width = 430
    card_height = 164
    draw_panel(frame, (card_x, card_y), (card_width, card_height))

    draw_text(
        frame,
        f"Hand {index + 1}: {display_label}",
        (card_x + 14, card_y + 10),
        font_size=26,
        color=(130, 200, 255),
    )
    draw_text(
        frame,
        f"Finger Count: {finger_count}",
        (card_x + 14, card_y + 44),
        font_size=24,
        color=(110, 255, 170),
    )
    draw_text(
        frame,
        debug_text,
        (card_x + 14, card_y + 76),
        font_size=20,
        color=(255, 225, 120),
    )
    draw_text(
        frame,
        (
            f"Wave {int(sequence_features.wave_detected)}  "
            f"Move {sequence_features.direction_changes}  "
            f"Stable {prediction.gesture_key if prediction else '-'}"
        ),
        (card_x + 14, card_y + 104),
        font_size=20,
        color=(220, 220, 220),
    )
    if translation:
        _draw_translation(frame, translation, card_y + 134)


def _build_fallback_translation(prediction: PredictionResult | None) -> TranslationResult | None:
    if prediction is None:
        return None

    return TranslationResult(
        label=prediction.label,
        confidence=prediction.confidence,
        translated_text=prediction.label,
        subtitle_text=prediction.label,
    )


def _build_body_features(hand_landmarks, hand_label: str, pose_landmarks) -> BodyFrameFeatures:
    fingers = get_finger_states(hand_landmarks, hand_label)
    features = BodyFrameFeatures(
        fingers=fingers,
        hand_label=hand_label,
    )

    if not pose_landmarks:
        return features

    body = pose_landmarks.landmark
    if hand_label == "Right":
        shoulder = body[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        elbow = body[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
        wrist = body[mp_pose.PoseLandmark.RIGHT_WRIST.value]
    else:
        shoulder = body[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        elbow = body[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        wrist = body[mp_pose.PoseLandmark.LEFT_WRIST.value]

    nose = body[mp_pose.PoseLandmark.NOSE.value]
    features.wrist_above_elbow = wrist.y < elbow.y
    features.wrist_above_shoulder = wrist.y < shoulder.y
    features.hand_near_head = distance_2d(wrist, nose) < 0.22
    features.elbow_angle = angle_2d(shoulder, elbow, wrist)
    features.wrist_x = wrist.x
    features.wrist_y = wrist.y
    return features


def run_hand_tracker(
    translator: SignLanguageTranslator | None = None,
    recognizer: RealTimeSignRecognizer | None = None,
) -> None:
    cap = cv2.VideoCapture(0)
    recognizer = recognizer or RealTimeSignRecognizer()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hand_results = hands.process(rgb)
        pose_results = pose.process(rgb)

        if pose_results.pose_landmarks:
            mp_draw.draw_landmarks(
                frame,
                pose_results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
            )

        overlay_items = []

        if hand_results.multi_hand_landmarks and hand_results.multi_handedness:
            for i, (hand_landmarks, handedness) in enumerate(
                zip(hand_results.multi_hand_landmarks, hand_results.multi_handedness)
            ):
                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                )

                hand_label = handedness.classification[0].label
                display_label = "Left" if hand_label == "Right" else "Right"

                features = _build_body_features(
                    hand_landmarks,
                    hand_label,
                    pose_results.pose_landmarks,
                )
                fingers = features.fingers
                finger_count = sum(fingers)
                debug_text = (
                    f"T:{fingers[0]} I:{fingers[1]} M:{fingers[2]} "
                    f"R:{fingers[3]} P:{fingers[4]}"
                )
                y_base = 40 + (i * 120)
                prediction, sequence_features = recognizer.recognize(features)
                translation = _build_fallback_translation(prediction)
                if translator and prediction:
                    translated = translator.translate_prediction(prediction)
                    if translated:
                        translation = translated
                if translation:
                    last_subtitle = translation.subtitle_text or translation.translated_text
                overlay_items.append(
                    {
                        "index": i,
                        "hand_label": hand_label,
                        "display_label": display_label,
                        "finger_count": finger_count,
                        "debug_text": debug_text,
                        "sequence_features": sequence_features,
                        "prediction": prediction,
                        "translation": translation,
                    }
                )

        display = cv2.flip(frame, 1)
        subtitle_parts = []
        for item in overlay_items:
            translation = item["translation"]
            if translation and translation.subtitle_text:
                subtitle_parts.append(
                    f'{item["display_label"]}: {translation.subtitle_text}'
                )

        draw_panel(display, (16, 16), (420, 54), color=(30, 42, 58), alpha=0.82)
        draw_text(
            display,
            "Sign Bridge Live View - Two Hand Tracking",
            (30, 25),
            font_size=24,
            color=(255, 255, 255),
        )
        for item in overlay_items:
            _draw_status_card(
                display,
                item["index"],
                item["display_label"],
                item["finger_count"],
                item["debug_text"],
                item["sequence_features"],
                item["prediction"],
                item["translation"],
            )
        draw_subtitle_banner(display, " | ".join(subtitle_parts))
        cv2.imshow("Hand Finger Counter", display)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
