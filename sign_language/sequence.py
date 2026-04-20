from collections import deque

from sign_language.models import BodyFrameFeatures, SequenceFeatures


class SequenceBuffer:
    def __init__(self, window_size: int = 16) -> None:
        self.window_size = window_size
        self._history_by_hand: dict[str, deque[BodyFrameFeatures]] = {}

    def _get_history(self, hand_label: str) -> deque[BodyFrameFeatures]:
        if hand_label not in self._history_by_hand:
            self._history_by_hand[hand_label] = deque(maxlen=self.window_size)
        return self._history_by_hand[hand_label]

    def update(self, features: BodyFrameFeatures) -> SequenceFeatures:
        history = self._get_history(features.hand_label)
        history.append(features)
        return self._build_sequence_features(features.hand_label, list(history))

    def _build_sequence_features(
        self,
        hand_label: str,
        samples: list[BodyFrameFeatures],
    ) -> SequenceFeatures:
        if not samples:
            return SequenceFeatures(
                hand_label=hand_label,
                frame_count=0,
                x_range=0.0,
                y_range=0.0,
                direction_changes=0,
                open_palm_ratio=0.0,
                near_head_ratio=0.0,
                above_shoulder_ratio=0.0,
                elbow_angle_mean=0.0,
                wave_detected=False,
            )

        x_positions = [sample.wrist_x for sample in samples]
        y_positions = [sample.wrist_y for sample in samples]
        x_range = max(x_positions) - min(x_positions)
        y_range = max(y_positions) - min(y_positions)

        dx_values = [
            x_positions[index] - x_positions[index - 1]
            for index in range(1, len(x_positions))
        ]
        filtered_dx = [delta for delta in dx_values if abs(delta) > 0.01]
        direction_changes = 0
        for index in range(1, len(filtered_dx)):
            if filtered_dx[index - 1] * filtered_dx[index] < 0:
                direction_changes += 1

        open_palm_count = sum(
            1 for sample in samples if tuple(sample.fingers) == (1, 1, 1, 1, 1)
        )
        near_head_count = sum(1 for sample in samples if sample.hand_near_head)
        above_shoulder_count = sum(
            1 for sample in samples if sample.wrist_above_shoulder
        )
        elbow_angle_mean = sum(sample.elbow_angle for sample in samples) / len(samples)

        open_palm_ratio = open_palm_count / len(samples)
        near_head_ratio = near_head_count / len(samples)
        above_shoulder_ratio = above_shoulder_count / len(samples)
        wave_detected = (
            len(samples) >= 6
            and open_palm_ratio >= 0.45
            and (near_head_ratio >= 0.3 or above_shoulder_ratio >= 0.3)
            and x_range > 0.12
            and y_range < 0.25
            and direction_changes >= 1
        )

        return SequenceFeatures(
            hand_label=hand_label,
            frame_count=len(samples),
            x_range=x_range,
            y_range=y_range,
            direction_changes=direction_changes,
            open_palm_ratio=open_palm_ratio,
            near_head_ratio=near_head_ratio,
            above_shoulder_ratio=above_shoulder_ratio,
            elbow_angle_mean=elbow_angle_mean,
            wave_detected=wave_detected,
        )
