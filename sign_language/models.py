from dataclasses import asdict, dataclass


@dataclass
class PredictionResult:
    label: str
    confidence: float
    gesture_key: str


@dataclass
class BodyFrameFeatures:
    fingers: list[int]
    hand_label: str
    wrist_above_elbow: bool = False
    wrist_above_shoulder: bool = False
    hand_near_head: bool = False
    elbow_angle: float = 0.0
    wrist_x: float = 0.0
    wrist_y: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SequenceFeatures:
    hand_label: str
    frame_count: int
    x_range: float
    y_range: float
    direction_changes: int
    open_palm_ratio: float
    near_head_ratio: float
    above_shoulder_ratio: float
    elbow_angle_mean: float
    wave_detected: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TranslationResult:
    label: str
    confidence: float
    translated_text: str
    subtitle_text: str = ""
    api_keyword: str = ""
    source_title: str = ""
    source_description: str = ""
