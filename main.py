import cv2
import mediapipe as mp

# MediaPipe 설정
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)


def get_finger_states(hand_landmarks, hand_label):
    lm = hand_landmarks.landmark
    fingers = []

    # 엄지
    # 원본 프레임 기준으로 판단
    # Right: tip(4)이 ip(3)보다 왼쪽이면 펼침
    # Left : tip(4)이 ip(3)보다 오른쪽이면 펼침
    if hand_label == "Right":
        thumb_open = lm[4].x < lm[3].x
    else:
        thumb_open = lm[4].x > lm[3].x
    fingers.append(1 if thumb_open else 0)

    # 검지, 중지, 약지, 새끼
    tip_ids = [8, 12, 16, 20]
    pip_ids = [6, 10, 14, 18]

    for tip_id, pip_id in zip(tip_ids, pip_ids):
        is_open = lm[tip_id].y < lm[pip_id].y
        fingers.append(1 if is_open else 0)

    return fingers  # [엄지, 검지, 중지, 약지, 새끼]


cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 인식은 원본 프레임 기준으로
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks and results.multi_handedness:
        for i, (hand_landmarks, handedness) in enumerate(
            zip(results.multi_hand_landmarks, results.multi_handedness)
        ):
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            # MediaPipe 기준 손 라벨
            hand_label = handedness.classification[0].label

            # 화면은 마지막에 좌우반전해서 보여줄 거라
            # 표시용 라벨은 반대로 바꿔줌
            if hand_label == "Right":
                display_label = "Left"
            else:
                display_label = "Right"

            fingers = get_finger_states(hand_landmarks, hand_label)
            finger_count = sum(fingers)

            debug_text = f"T:{fingers[0]} I:{fingers[1]} M:{fingers[2]} R:{fingers[3]} P:{fingers[4]}"

            y_base = 40 + (i * 120)

            cv2.putText(
                frame,
                f"Hand: {display_label}",
                (10, y_base),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 0, 0),
                2
            )

            cv2.putText(
                frame,
                f"Count: {finger_count}",
                (10, y_base + 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                debug_text,
                (10, y_base + 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2
            )

    # 보여줄 때만 좌우반전
    display = cv2.flip(frame, 1)
    cv2.imshow("Hand Finger Counter", display)

    # ESC 종료
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()