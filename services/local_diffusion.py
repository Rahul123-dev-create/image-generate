"""
Optional local diffusion helpers. These try to use Hugging Face diffusers if available.
They are intentionally optional: if the required packages are not installed, the functions
will raise a clear exception instructing how to install them.

Functions return a dict similar to remote API responses with 'urls' or 'result' keys.
Local images are returned as data URIs (data:image/png;base64,....)
"""
from typing import Dict, Any, List, Optional
import io
import base64
from PIL import Image


def _image_to_data_uri(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b = buf.getvalue()
    return "data:image/png;base64," + base64.b64encode(b).decode("utf-8")


def generate_hd_local(prompt: str, num_images: int = 1, seed: Optional[int] = None, model_name: str = "runwayml/stable-diffusion-v1-5") -> Dict[str, Any]:
    """Generate images locally using Stable Diffusion (if installed).

    Returns dict with 'urls' key containing data URIs.
    """
    try:
        import torch
        from diffusers import StableDiffusionPipeline
    except Exception:
        raise Exception("Local diffusion requires 'diffusers' and 'torch'. Install with: pip install 'diffusers[torch]' transformers accelerate torch")

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Load pipeline
    pipe = StableDiffusionPipeline.from_pretrained(model_name)
    pipe = pipe.to(device)

    generator = None
    if seed is not None:
        generator = torch.Generator(device=device).manual_seed(seed)

    images = []
    for i in range(num_images):
        out = pipe(prompt, num_inference_steps=25, guidance_scale=7.5, generator=generator)
        img = out.images[0]
        images.append(_image_to_data_uri(img))

    return {"urls": images}


def inpaint_local(image_bytes: bytes, mask_bytes: bytes, prompt: str, num_images: int = 1, seed: Optional[int] = None, model_name: str = "runwayml/stable-diffusion-inpainting") -> Dict[str, Any]:
    try:
        import torch
        from diffusers import StableDiffusionInpaintPipeline
    except Exception:
        raise Exception("Local inpainting requires 'diffusers' and 'torch'. Install with: pip install 'diffusers[torch]' transformers accelerate torch")

    device = "cuda" if torch.cuda.is_available() else "cpu"

    pipe = StableDiffusionInpaintPipeline.from_pretrained(model_name)
    pipe = pipe.to(device)

    generator = None
    if seed is not None:
        generator = torch.Generator(device=device).manual_seed(seed)

    init_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    mask_img = Image.open(io.BytesIO(mask_bytes)).convert("RGB")

    images = []
    for i in range(num_images):
        out = pipe(prompt=prompt, image=init_img, mask_image=mask_img, num_inference_steps=25, guidance_scale=7.5, generator=generator)
        img = out.images[0]
        images.append(_image_to_data_uri(img))

    return {"urls": images}
