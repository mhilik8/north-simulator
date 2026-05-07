# graphics_utils.py

from pathlib import Path
from functools import cache
from PIL import Image
import io
import base64


@cache
def load_image(path: str) -> Image.Image:
    return Image.open(path).convert("RGBA")


def rotated_image_uri(path: str, angle_deg: float) -> str:
    """
    Load image, rotate it, and return base64 URI.
    """

    img = load_image(path)

    rotated = img.rotate(
        angle_deg,
        expand=True,
        resample=Image.Resampling.BICUBIC
    )

    buffer = io.BytesIO()

    rotated.save(buffer, format="PNG")

    encoded = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{encoded}"
