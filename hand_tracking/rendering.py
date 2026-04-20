from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


DEFAULT_FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/malgun.ttf"),
    Path("C:/Windows/Fonts/gulim.ttc"),
    Path("C:/Windows/Fonts/arial.ttf"),
]


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for font_path in DEFAULT_FONT_CANDIDATES:
        if font_path.exists():
            return ImageFont.truetype(str(font_path), size)
    return ImageFont.load_default()


def draw_text(
    frame,
    text: str,
    position: tuple[int, int],
    font_size: int = 28,
    color: tuple[int, int, int] = (255, 255, 255),
) -> None:
    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_image)
    font = _load_font(font_size)
    draw.text(position, text, font=font, fill=color[::-1])
    updated = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    frame[:, :] = updated


def draw_panel(
    frame,
    top_left: tuple[int, int],
    size: tuple[int, int],
    color: tuple[int, int, int] = (24, 28, 36),
    alpha: float = 0.78,
) -> None:
    x, y = top_left
    width, height = size
    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (x, y),
        (x + width, y + height),
        color,
        thickness=-1,
    )
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    cv2.rectangle(
        frame,
        (x, y),
        (x + width, y + height),
        (90, 96, 110),
        thickness=1,
    )


def draw_subtitle_banner(frame, text: str) -> None:
    if not text:
        return

    height, width = frame.shape[:2]
    banner_height = 90
    top = max(0, height - banner_height)

    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (0, top),
        (width, height),
        (20, 20, 20),
        thickness=-1,
    )
    cv2.addWeighted(overlay, 0.72, frame, 0.28, 0, frame)
    draw_text(
        frame,
        text,
        (24, top + 22),
        font_size=30,
        color=(255, 255, 255),
    )
