from typing import Dict, Any
import base64
import io
from PIL import Image


def remove_background(api_key: str, image_bytes: bytes, content_moderation: bool = False) -> Dict[str, Any]:
    """Simple fallback background removal stub.

    This function doesn't perform real background removal. It returns a data URI
    containing the original image so calling code can continue to work during
    development. Replace with a real background removal implementation (e.g.
    remove.bg API, Adobe, or a local segmentation model) when ready.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        # For the stub, just return the original image as PNG data URI
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        data = buf.getvalue()
        data_uri = "data:image/png;base64," + base64.b64encode(data).decode("utf-8")
        return {"result_url": data_uri}
    except Exception as e:
        raise Exception(f"remove_background stub failed: {e}")
