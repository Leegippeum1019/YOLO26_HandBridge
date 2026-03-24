import cv2
import mediapipe as mp

# MediaPipe 설정
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils


def count_fingers(hand_landmarks, hand_label):
    fingers = []
    landmarks = hand_landmarks.landmark

    # 엄지 판별
    # 좌우반전(frame = cv2.flip(frame, 1)) 상태 기준
    if hand_label == "Right":
        if landmarks[4].x > landmarks[3].x:
            fingers.append(1)
        else:
            fingers.append(0)
    else:  # Left
        if landmarks[4].x < landmarks[3].x:
            fingers.append(1)
        else:
            fingers.append(0)

    # 검지
    if landmarks[8].y < landmarks[6].y:
        fingers.append(1)
    else:
        fingers.append(0)

    # 중지
    if landmarks[12].y < landmarks[10].y:
        fingers.append(1)
    else:
        fingers.append(0)

    # 약지
    if landmarks[16].y < landmarks[14].y:
        fingers.append(1)
    else:
        fingers.append(0)

    # 새끼
    if landmarks[20].y < landmarks[18].y:
        fingers.append(1)
    else:
        fingers.append(0)

    return fingers.count(1)


# 카메라 실행
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 좌우반전
    frame = cv2.flip(frame, 1)

    # BGR -> RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 손 인식
    results = hands.process(rgb)

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # 손 랜드마크 그리기
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            # 손 라벨 가져오기
            hand_label = handedness.classification[0].label

            # 손가락 개수 계산
            finger_count = count_fingers(hand_landmarks, hand_label)

            # 화면 출력
            cv2.putText(
                frame,
                f"Hand: {hand_label}",
                (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 0, 0),
                2
            )

            cv2.putText(
                frame,
                f"Finger Count: {finger_count}",
                (10, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

    cv2.imshow("Hand Finger Counter", frame)

    # ESC 누르면 종료
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()