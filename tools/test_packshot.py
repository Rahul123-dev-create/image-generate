import os
import io
import traceback
from PIL import Image

from services.packshot import create_packshot


def make_png_bytes(size=(32, 32), color=(255, 0, 0, 255)):
    img = Image.new("RGBA", size, color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


if __name__ == '__main__':
    api_key = os.getenv('BRIA_API_KEY')
    if not api_key:
        print('BRIA_API_KEY not set in environment. Test will still run to show error handling.')

    img_bytes = make_png_bytes()
    try:
        print('Calling create_packshot...')
        resp = create_packshot(api_key or '', img_bytes, background_color='#FFFFFF')
        print('create_packshot response:')
        print(resp)
    except Exception as e:
        print('create_packshot raised an exception:')
        traceback.print_exc()
