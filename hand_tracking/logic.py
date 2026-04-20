import math


def distance_2d(point_a, point_b) -> float:
    dx = point_a.x - point_b.x
    dy = point_a.y - point_b.y
    return (dx * dx + dy * dy) ** 0.5


def angle_2d(point_a, point_b, point_c) -> float:
    ab_x = point_a.x - point_b.x
    ab_y = point_a.y - point_b.y
    cb_x = point_c.x - point_b.x
    cb_y = point_c.y - point_b.y

    ab_norm = math.hypot(ab_x, ab_y)
    cb_norm = math.hypot(cb_x, cb_y)
    if ab_norm == 0 or cb_norm == 0:
        return 0.0

    cosine = ((ab_x * cb_x) + (ab_y * cb_y)) / (ab_norm * cb_norm)
    cosine = max(-1.0, min(1.0, cosine))
    return math.degrees(math.acos(cosine))


def _is_thumb_open(landmarks) -> bool:
    palm_size = distance_2d(landmarks[0], landmarks[9])
    if palm_size == 0:
        return False

    thumb_extension = distance_2d(landmarks[4], landmarks[2]) / palm_size
    thumb_spread = distance_2d(landmarks[4], landmarks[5]) / palm_size
    thumb_angle = angle_2d(landmarks[2], landmarks[3], landmarks[4])

    return (
        thumb_extension > 0.72
        and thumb_spread > 0.35
        and thumb_angle > 140
    )


def _is_finger_open(landmarks, mcp_id: int, pip_id: int, dip_id: int, tip_id: int) -> bool:
    palm_size = distance_2d(landmarks[0], landmarks[9])
    if palm_size == 0:
        return False

    bend_angle = angle_2d(landmarks[pip_id], landmarks[dip_id], landmarks[tip_id])
    extension = distance_2d(landmarks[tip_id], landmarks[mcp_id]) / palm_size
    folded_depth = distance_2d(landmarks[tip_id], landmarks[0]) / palm_size

    return (
        bend_angle > 145
        and extension > 0.68
        and folded_depth > 0.78
    )


def get_finger_states(hand_landmarks, hand_label):
    del hand_label

    landmarks = hand_landmarks.landmark
    fingers = [1 if _is_thumb_open(landmarks) else 0]

    finger_joints = [
        (5, 6, 7, 8),
        (9, 10, 11, 12),
        (13, 14, 15, 16),
        (17, 18, 19, 20),
    ]

    for mcp_id, pip_id, dip_id, tip_id in finger_joints:
        is_open = _is_finger_open(landmarks, mcp_id, pip_id, dip_id, tip_id)
        fingers.append(1 if is_open else 0)

    return fingers
