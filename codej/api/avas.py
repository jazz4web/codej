import io

from PIL import Image


def check_img(binary):
    b, t = None, io.BytesIO(binary)
    try:
        image = Image.open(t)
    except OSError:
        t.close()
        return None
    if image and (image.format not in ('JPEG', 'PNG', 'GIF') or
                  image.height != image.width or image.width > 200):
        image.close()
        t.close()
        return None
    b = io.BytesIO()
    image.save(b, format='PNG')
    image.close()
    b.seek(0)
    binary = b.read()
    b.close()
    if not t.closed:
        t.close()
    return binary
