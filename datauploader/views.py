from django.http import HttpResponse
from controllers import DataUploadController
from utils import serialize_to_json

def return_uploaders_that_can_parse_file(request):
    file = request.FILES['data_upload']
    file_id = request.POST.get('file_id') or None
    duc = DataUploadController(file_id, uploaded_file=file)
    if not duc.is_valid():
        return HttpResponse(serialize_to_json({'uploaders':[]}))
    uploaders = duc.list_available_uploaders()
    if not uploaders:
        return HttpResponse(serialize_to_json({'uploaders':[]}))
    duc.persist_file()
    return HttpResponse(serialize_to_json({'uploaders':uploaders}))

def process_file_with_datauploader(request):
    file_id = request.GET.get('file_id')
    datauploader_name = request.GET.get('datauploader_name')
    data_point_type = request.GET.get('data_point_type')
    duc = DataUploadController(file_id, data_point_type=data_point_type, datauploader_name=datauploader_name)
    data_point, errors = duc.run_datauploader()
    if not errors:
        duc.clean_up()
    return HttpResponse(serialize_to_json({'data_point':data_point, 'errors':errors or []}))