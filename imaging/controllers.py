from django.conf import settings
import os
import StringIO
from logger import Logger

class ImagingController(object):
    @classmethod
    def GenerateNotFoundImage(cls, width, height, fill_color):
        import cairo
        text_sizes = (14, 10) if width > 100 else (10, 7)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        context = cairo.Context(surface)
        context.set_source_rgb(1.0, 1.0, 1.0)
        context.rectangle(0, 0, width, height)
        context.fill()
        text = 'metaLayer'
        context.set_source_rgb(0, 0, 0)
        context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        context.set_font_size(text_sizes[0])
        x, y, w, h = context.text_extents(text)[:4]
        context.move_to((width / 2) - (w / 2) - x, (height / 2) - (h / 2) - y)
        context.show_text(text)
        text = 'no image'
        context.set_source_rgb(0, 0, 0)
        context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        context.set_font_size(text_sizes[1])
        x, y, w, h = context.text_extents(text)[:4]
        context.move_to((width / 2) - (w / 2) - x, (height / 2) - (h / 2) - y + 14)
        context.show_text(text)
        string_io = StringIO.StringIO()
        surface.write_to_png(string_io)
        string_io.seek(0)
        return string_io

    @classmethod
    def ReadImageFromCache(cls, file_name, expiry_time):
        try:
            if os.path.getmtime(file_name) >= expiry_time:
                #return settings.DYNAMIC_IMAGES_WEB_ROOT + file_name.split('/')[-1]
                return open(file_name, 'rb')
            os.remove(file_name)
        except OSError:
            pass
        return None

    @classmethod
    def WriteImageDataToCache(cls, file_name, image_data):
        try:
            image_data.seek(0)
            output = open(file_name, 'wb')
            output.write(image_data.read())
            output.close()
            image_data.seek(0)
        except Exception, e:
            Logger.Error('%s - ImagingController.WriteImageDataToCache - error writing to cache' % __name__)
            Logger.Debug('%s - ImagingController.WriteImageDataToCache - error: %s' % (__name__, e))