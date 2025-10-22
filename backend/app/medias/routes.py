import os
from flask_cors import CORS, cross_origin
from flask import Blueprint, redirect, request, jsonify, abort, make_response, g, current_app, send_file
from werkzeug.utils import secure_filename
from depot.manager import DepotManager
from depot.fields.specialized.image import UploadedImageWithThumb
from depot.fields.upload import UploadedFile
from depot.io.utils import file_from_content
from datetime import datetime, timezone
import io
import tempfile
from app.common import filters
from app.security import roles, permissions
from app.utils.response import APIResponse

from .service import MediaService
from config import FileUploadConfig

__uri__ = 'medias'
__blueprint__ = 'medias'

medias = Blueprint(__uri__, __name__)

service = MediaService()


@medias.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['media.show'])
@filters.filters
def get_medias(self, filter):
    medias = service.get_all_medias(None, filter)
    return APIResponse.success(medias, "Media files retrieved successfully")

@medias.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['media.show'])
def get_media(self, id):
    medias = service.get_all_medias(id, None)
    if medias:
        return APIResponse.success(medias, "Media file retrieved successfully")
    return APIResponse.not_found("Media file not found")

@medias.route('/model/<model_type>', defaults={'model_id': None})
@medias.route('/model/<model_type>/<model_id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['media.show'])
@filters.filters
def get_media_by_model(self, filter, model_type=None, model_id=None):
    medias = service.get_model_medias(model_type, model_id, filter)
    return APIResponse.success({'medias': medias}, "Model media files retrieved successfully")

@medias.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['media.add'])
def add_media(self):
    if 'files' not in request.files:
        return APIResponse.validation_error("No file part in the request")
    
    if not request.form or 'disk' not in request.form:
        return APIResponse.validation_error("Disk parameter is required")
    
    message = service.upload(request.files.getlist('files'), request.form)
    return APIResponse.created({'msg': message}, "Media files uploaded successfully")

@medias.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['media.edit'])
def update_media(self, id):
    if not request.json:
        return APIResponse.validation_error("No data provided")
    
    message, status = service.update_media(id, request.json)
    if status == 200:
        return APIResponse.success(message, "Media file updated successfully")
    elif status == 404:
        return APIResponse.not_found("Media file not found")
    return APIResponse.error(message, status_code=status)

@medias.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['media.delete'])
def delete_media(self, id):
    message, status = service.delete_media(id)
    if status == 200:
        return APIResponse.success(message, "Media file deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Media file not found")
    return APIResponse.error(message, status_code=status)

@medias.route('/files-upload/<disk>/<model_type>', defaults={'model_id': None}, methods=['POST'])
@medias.route('/files-upload/<disk>/<model_type>/<model_id>', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['media.edit'])
def upload_file(self, disk='media', model_type=None, model_id=None):
    try:
        # check if the post request has the file part
        if 'files' not in request.files:
            return APIResponse.validation_error("No file part in the request")
        
        request_json = {
            'disk': disk,
            'model_type': model_type,
            'model_id': model_id
        }
        response = service.upload(request.files.getlist('files'), request_json)
        return APIResponse.success(response, "Files uploaded successfully")
    except Exception as e:
        current_app.logger.error(e)
        return APIResponse.server_error(f"Error uploading files: {str(e)}")

@medias.route('/files-upload/<model_type>/<model_id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['media.delete'])
def delete_media_by_model_type_and_id(self, model_type, model_id):
    message, status = service.delete_media_by_model_type_and_id(model_type, model_id)
    if status == 200:
        return APIResponse.success(message, "Media files deleted successfully")
    elif status == 404:
        return APIResponse.not_found("Media files not found")
    return APIResponse.error(message, status_code=status)

@medias.route('/uploads/<depot>/<fileid>', defaults={'file_name': None}, methods=['GET'])
@medias.route('/uploads/<depot>/<fileid>/<file_name>', methods=['GET'])
@cross_origin()
def upload(depot, fileid, file_name):
    file, status = service.show(depot, fileid)
    if status == 404:
        abort(404)
    elif status == 301:
        return redirect(file)
    else:
        # Read the file content into memory
        # Create a temporary file to store the content
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file.read())
            temp_file_path = temp_file.name
        # Send the file using send_file
        response = send_file(temp_file_path, as_attachment=True, download_name=file.filename)

        # Clean up the temporary file after sending
        os.unlink(temp_file_path)

        return response
