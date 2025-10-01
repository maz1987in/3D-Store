import sys
from PIL import Image
import io, os

from flask import current_app

class ImageProcess:
    def add_watermark(self, image):
        #print('add_watermark', file=sys.stderr)
        try:
            # base image
            base_image = Image.open(image)
            base_image_width, base_image_height = base_image.size

            # watermark
            base_path = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    'logo.png'
                )
            )
            watermark_image_path = base_path

            watermark = Image.open(watermark_image_path).convert('RGBA')
            base_size = min(base_image_width, base_image_height)
            size = (base_size/4, base_size/4)

            watermark.thumbnail(size)
            watermark_width, watermark_height = watermark.size
            #print(watermark_width, file=sys.stderr)

            # calculate the x,y coordinates of the image
            margin = 20
            x = base_image_width - watermark_width - margin
            y = base_image_height - watermark_height - margin

            # add watermark to your image
            base_image.paste(watermark, (x, y), watermark)

            buffer = io.BytesIO()
            base_image.save(buffer,format=base_image.format)
            #buffer.seek(0)
            
            return buffer
        except Exception as e:
            #print('in watermark: {0}'.format(e))
            current_app.logger.error('in watermark: {0}'.format(e))
            return image
    
    # compress image to reduce size
    def compress_image(self, image, quality=85):
        #print('compress_image', file=sys.stderr)
        try:
            # compress image
            buffer = io.BytesIO()
            base_image = Image.open(image)
            base_image.save(buffer, format=base_image.format,optimize=True, quality=quality)
            #buffer.seek(0)
            return buffer
        except Exception as e:
            #print('in compress_image: {0}'.format(e))
            current_app.logger.error('in compress_image: {0}'.format(e))
            return image
    
    # thumbnail image
    def thumbnail_image(self, image, size=(100,100)):
        #print('thumbnail_image', file=sys.stderr)
        try:
            # compress image
            buffer = io.BytesIO()
            base_image = Image.open(image)
            base_image.thumbnail(size)
            base_image.save(buffer, format=base_image.format)
            #buffer.seek(0)
            return buffer
        except Exception as e:
            #print('in thumbnail_image: {0}'.format(e))
            current_app.logger.error('in thumbnail_image: {0}'.format(e))
            return image