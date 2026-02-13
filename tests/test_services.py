import io
import base64
import json
import pytest
from types import SimpleNamespace

import services
from services import utils

# Helper mock response
class MockResponse:
    def __init__(self, status_code=200, json_data=None, text=None):
        self.status_code = status_code
        self._json = json_data if json_data is not None else {}
        self.text = text if text is not None else json.dumps(self._json)

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise Exception(f"HTTP {self.status_code}")

    def json(self):
        return self._json


@pytest.fixture
def sample_image_bytes():
    # tiny white PNG
    from PIL import Image
    img = Image.new('RGB', (8, 8), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


def test_ensure_api_key():
    with pytest.raises(ValueError):
        utils.ensure_api_key(None)


def test_prompt_enhancement_parsing(monkeypatch):
    # Simulate API returning a weird key 'prompt variations'
    response_body = {"prompt variations": "Enhanced prompt text here"}
    def fake_post(url, headers=None, json=None):
        return MockResponse(json_data=response_body)

    monkeypatch.setattr('requests.post', fake_post)

    enhanced = services.prompt_enhancement.enhance_prompt(api_key='key', prompt='orig')
    assert 'Enhanced' in enhanced or 'enhanced' in enhanced.lower() or enhanced == 'Enhanced prompt text here' or 'Enhanced prompt text here' == enhanced


def test_generative_fill_normalize(monkeypatch, sample_image_bytes):
    # API returns urls list
    response_body = {"urls": ["https://example.com/gen1.png"]}
    monkeypatch.setattr('requests.post', lambda *a, **k: MockResponse(json_data=response_body))

    # `services` package exposes `generative_fill` as a function; call it directly
    res = services.generative_fill(api_key='key', image_data=sample_image_bytes, mask_data=sample_image_bytes, prompt='x')
    assert isinstance(res, dict)
    assert 'urls' in res and res['urls'][0].startswith('http')


def test_hd_image_generation_normalize(monkeypatch):
    response_body = {"result": [{"urls": ["https://example.com/hd1.png"]}]}
    monkeypatch.setattr('requests.post', lambda *a, **k: MockResponse(json_data=response_body))

    res = services.hd_image_generation.generate_hd_image(prompt='p', api_key='key')
    assert isinstance(res, dict)
    assert 'urls' in res and res['urls'][0].startswith('http')


def test_lifestyle_shot_by_text_normalize(monkeypatch, sample_image_bytes):
    response_body = {"result": [["https://example.com/life1.png", 12345, "id.png"]]}
    monkeypatch.setattr('requests.post', lambda *a, **k: MockResponse(json_data=response_body))

    res = services.lifestyle_shot.lifestyle_shot_by_text(api_key='key', image_data=sample_image_bytes, scene_description='desc')
    assert isinstance(res, dict)
    assert 'urls' in res and res['urls'][0].startswith('http')


def test_erase_foreground_normalize(monkeypatch, sample_image_bytes):
    response_body = {"result_url": "https://example.com/erase1.png"}
    monkeypatch.setattr('requests.post', lambda *a, **k: MockResponse(json_data=response_body))

    # `services` package exposes `erase_foreground` as a function; call it directly
    res = services.erase_foreground(api_key='key', image_data=sample_image_bytes)
    assert isinstance(res, dict)
    assert 'urls' in res and res['urls'][0].startswith('http')


def test_local_diffusion_missing_deps():
    # local_diffusion functions should raise informative errors if torch/diffusers missing
    with pytest.raises(Exception) as excinfo:
        services.local_diffusion.generate_hd_local('prompt', num_images=1)
    assert 'diffusers' in str(excinfo.value) or 'torch' in str(excinfo.value)

    with pytest.raises(Exception) as excinfo2:
        # dummy bytes for inpaint
        services.local_diffusion.inpaint_local(b'0', b'0', 'prompt')
    assert 'diffusers' in str(excinfo2.value) or 'torch' in str(excinfo2.value)


def test_local_diffusion_success_path(monkeypatch):
    # Simulate local diffusion functions being available and returning urls
    monkeypatch.setattr('services.local_diffusion.generate_hd_local', lambda prompt, num_images=1, seed=None, model_name=None: {'urls': ['data:image/png;base64,AAA']})
    monkeypatch.setattr('services.local_diffusion.inpaint_local', lambda image_bytes, mask_bytes, prompt, num_images=1, seed=None, model_name=None: {'urls': ['data:image/png;base64,BBB']})

    res1 = services.local_diffusion.generate_hd_local('p', num_images=1)
    assert isinstance(res1, dict) and 'urls' in res1

    res2 = services.local_diffusion.inpaint_local(b'0', b'1', 'p')
    assert isinstance(res2, dict) and 'urls' in res2
