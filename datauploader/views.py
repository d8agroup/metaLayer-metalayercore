from django.http import HttpResponse
from controllers import DataUploadController
from utils import serialize_to_json, JSONResponse

def get_all_templates_with_options(request):
    """
    Return all the available uploaders with their content item templates

    Notes
    -----
    At present this function does not support options passed as a request parameter but in future this will allow
    the list of uploaders to be filtered by only ones applicable to a user.

    Returns
    -------
    Array[dict{name, template}]: Array of dict's containing the uploader name and the content item template
    """
    all_available_uploaders = DataUploadController.AllAvailableUploaders()
    #TODO Filter by options
    uploader_names_and_templates = [{
        'name':u.get_display_config()['name'],
        'template':u.get_content_item_template()}
        for u in all_available_uploaders
    ]
    return JSONResponse(uploader_names_and_templates)


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

def get_content_item_template(request, datauploader_name):
    """
    Return the HTML template associated with the provided datauploader_name

    Arguments
    ---------
    datauploader_name (string): the name of the DataUploader to call the HTML template from

    Returns
    -------
    JSONResponse({template:string(HTML), datauploader_name:string})
    """
    datauploader = DataUploadController.GetUploaderByName(datauploader_name)
    template = datauploader.get_content_item_template() if datauploader else ''
    return JSONResponse({'template':template, 'datauploader_name':datauploader_name} )

