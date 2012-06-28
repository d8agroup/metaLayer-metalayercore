import StringIO
import datetime
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import redirect
import os
import time
from metalayercore.dashboards.controllers import DashboardsController
from metalayercore.imaging.controllers import ImagingController
from logger import Logger

def last_modified(request, dashboard_id, *args, **kwargs):
    cache_key = 'imaging_views_last_modified'
    cache_values = cache.get(cache_key, -1)
    if cache_values == -1:
        dashboard = DashboardsController.GetDashboardById(dashboard_id, False)
        if dashboard:
            cache_values = datetime.datetime.fromtimestamp(dashboard['last_saved'])
        else:
            cache_values = datetime.datetime.now()
        cache.add(cache_key, cache_values, settings.LOW_LEVEL_CACHE_LIMITS[cache_key])
    return cache_values

def build_file_name(type, id, width, height):
    return '%s_%s_%i_%i.png' % (type, id, width, height)

#@condition(last_modified_func=last_modified)
def crop(request, dashboard_id, width='200', height='200'):
    import cairo
    import rsvg
    width = int(width)
    height = int(height)

    dashboard = DashboardsController.GetDashboardById(dashboard_id, False)
    if not dashboard or not dashboard.has_visualizations():
        image_data = ImagingController.GenerateNotFoundImage(width, height, None)
        response = HttpResponse(image_data, mimetype='image/png')
        return response

    file_name = build_file_name('crop', dashboard_id, width, height)
    dashboard_last_saved = dashboard['last_saved']

    try:
        name = settings.DYNAMIC_IMAGES_ROOT + file_name
        if os.path.getmtime(name) >= dashboard_last_saved:
            return redirect(settings.DYNAMIC_IMAGES_WEB_ROOT + file_name, permanent=False)
        os.remove(name)
    except OSError:
        pass

    visualization_svg = dashboard.visualization_for_image()
    if not visualization_svg:
        Logger.Warn('%s - crop - empty visualization_svg extracted' % __name__)
        Logger.Debug('%s - crop - empty visualization_svg extracted from dashboard with id: %s' % (__name__, dashboard_id))
        image_data = ImagingController.GenerateNotFoundImage(int(width), int(height), None)
        response = HttpResponse(image_data, mimetype='image/png')
        return response
    try:
        svg = rsvg.Handle(data=visualization_svg)
    except Exception, e:
        Logger.Warn('%s - crop - error reading svg' % __name__)
        Logger.Debug('%s - crop - error reading svg:%s' % (__name__, visualization_svg), exception=Exception, request=request)
        image_data = ImagingController.GenerateNotFoundImage(int(width), int(height), None)
        response = HttpResponse(image_data, mimetype='image/png')
        return response

    image_height = svg.props.height
    required_height = height * 1.8
    scale = (float(required_height) / float(image_height))
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)
    context.scale(scale, scale)
    context.translate((width + width/4) * -1, (height / 2) * -1)
    svg.render_cairo(context)
    image_data = StringIO.StringIO()
    surface.write_to_png(image_data)
    ImagingController.WriteImageDataToCache(settings.DYNAMIC_IMAGES_ROOT + file_name, image_data)
    return redirect(settings.DYNAMIC_IMAGES_WEB_ROOT + file_name, permanent=False)

#@condition(last_modified_func=last_modified)
def shrink(request, dashboard_id, max_width, max_height, visualization_id=None):
    import cairo
    import rsvg
    max_width = int(max_width)
    max_height = int(max_height)

    return_as_attachment = request.GET.get('as_attachment')
    return_as_attachment = True if return_as_attachment else False

    dashboard = DashboardsController.GetDashboardById(dashboard_id, False)
    if not dashboard or not dashboard.has_visualizations():
        image_data = ImagingController.GenerateNotFoundImage(max_width, max_height, None)
        response = HttpResponse(image_data, mimetype='image/png')
        return response

    if visualization_id:
        file_name = 'shrink_%s_%i_%i.png' % (visualization_id, max_width, max_height)
    else:
        file_name = 'shrink_%s_%i_%i.png' % (dashboard_id, max_width, max_height)

    dashboard_last_saved = dashboard['last_saved']

    if not return_as_attachment:
        try:
            name = settings.DYNAMIC_IMAGES_ROOT + file_name
            if os.path.getmtime(name) >= dashboard_last_saved:
                return redirect(settings.DYNAMIC_IMAGES_WEB_ROOT + file_name, permanent=False)
            os.remove(name)
        except OSError:
            pass

    max_width = int(max_width)
    max_height = int(max_height)
    if visualization_id:
        visualization_svg = dashboard.visualization_by_id(visualization_id)
    else:
        visualization_svg = dashboard.visualization_for_image()
    if not visualization_svg:
        Logger.Warn('%s - crop - empty visualization_svg extracted' % __name__)
        Logger.Debug('%s - crop - empty visualization_svg extracted from dashboard with id: %s' % (__name__, dashboard_id))
        image_data = ImagingController.GenerateNotFoundImage(int(max_width), int(max_height), None)
        response = HttpResponse(image_data, mimetype='image/png')
        return response
    try:
        svg = rsvg.Handle(data=visualization_svg)
    except Exception, e:
        Logger.Warn('%s - crop - error reading svg:%s' % (__name__, visualization_svg), exception=Exception, request=request)
        image_data = ImagingController.GenerateNotFoundImage(int(max_width), int(max_height), None)
        response = HttpResponse(image_data, mimetype='image/png')
        return response

    x = width = svg.props.width
    y = height = svg.props.height
    y_scale = x_scale = 1
    if (max_height != 0 and width > max_width) or (max_height != 0 and height > max_height):
        x = max_width
        y = float(max_width)/float(width) * height
        if y > max_height:
            y = max_height
            x = float(max_height)/float(height) * width
        x_scale = float(x)/svg.props.width
        y_scale = float(y)/svg.props.height
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, x, y)
    context = cairo.Context(surface)
    context.scale(x_scale, y_scale)
    svg.render_cairo(context)
    image_data = StringIO.StringIO()
    surface.write_to_png(image_data)
    ImagingController.WriteImageDataToCache(settings.DYNAMIC_IMAGES_ROOT + file_name, image_data)
    if return_as_attachment:
        image_data.seek(0)
        response = HttpResponse(image_data, content_type='image/png')
        response['Content-Disposition'] = 'attachment; filename=metaLayer_image_export_%i.png' % int(time.time())
        return response
    return redirect(settings.DYNAMIC_IMAGES_WEB_ROOT + file_name, permanent=False)



