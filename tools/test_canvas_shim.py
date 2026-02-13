from PIL import Image
import io
import sys

try:
    import streamlit.elements.image as st_image
except Exception as e:
    print('Failed to import streamlit.elements.image:', e)
    sys.exit(1)

if not hasattr(st_image, 'image_to_url'):
    print('streamlit.elements.image has no attribute image_to_url')
    sys.exit(2)

# Create a small test image
img = Image.new('RGB', (8, 8), (123, 222, 100))
try:
    url = st_image.image_to_url(img, width=8, use_container_width=False, fmt='RGB', ftype='PNG', key='test')
    print('image_to_url produced data URL length:', len(url))
    print(url[:60] + '...')
except Exception as e:
    print('image_to_url call raised exception:')
    import traceback
    traceback.print_exc()
