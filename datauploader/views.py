from django.http import HttpResponse
from controllers import DataUploadController
from utils import serialize_to_json

def file_upload_from_dashboard(request):
    file = request.FILES['data_upload']
    file_id = request.POST.get('file_id') or None
    data_point_type = request.POST.get('data_point_type')
    duc = DataUploadController(file, file_id, data_point_type)
    data_point, errors = duc.parse_uploaded_file()
    return HttpResponse(serialize_to_json({'data_point':data_point, 'errors':errors or []}))