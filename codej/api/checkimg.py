import io

from PIL import Image


def read_data(binary):
    b = io.BytesIO(binary)
    try:
        image = Image.open(b)
    except OSError:
        image = None
    if image and image.format not in ('JPEG', 'PNG', 'GIF'):
        image.close()
        image = None
    if image:
        res = {'width': image.width,
               'height': image.height,
               'format': image.format}
        image.close()
        b.close()
        return res
    return image
