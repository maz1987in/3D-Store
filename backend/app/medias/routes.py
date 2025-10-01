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
def get_medias(filter,self):
    medias = service.get_all_medias(None,filter)
    return jsonify(medias)

@medias.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['media.show'])
def get_media(self,id):
    medias = service.get_all_medias(id,None)
    return jsonify(medias)

@medias.route('/model/<model_type>', defaults={'model_id': None})
@medias.route('/model/<model_type>/<model_id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['media.show'])
@filters.filters
def get_media_by_model(filter,self,model_type=None, model_id=None):
    medias = service.get_model_medias(model_type,model_id,filter)
    return jsonify({'medias': medias})

@medias.route('/', methods=['POST'])
#@cross_origin()
#@permissions.has_permission(['media.add'])
@roles.token_required
def add_media(self):
	if 'files' not in request.files:
		resp = jsonify({'message' : 'No file part in the request'})
		resp.status_code = 400
		return resp
	if not request.form or not 'disk' in request.form:
		abort(404)
	message= service.upload(request.files.getlist('files'),request.form)
	
	return jsonify({'msg': message})

@medias.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['media.edit'])
def update_media(self,id):
    message, status = service.update_media(id, request.json)
    return jsonify({'msg': message}), status

@medias.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['media.delete'])
def delete_media(self,id):
    message, status = service.delete_media(id)
    return jsonify({'msg': message}), status

@medias.route('/files-upload/<disk>/<model_type>', defaults={'model_id': None}, methods=['POST'])
@medias.route('/files-upload/<disk>/<model_type>/<model_id>', methods=['POST'])
#@cross_origin()
#@permissions.has_permission(['media.edit'])
@roles.token_required
def upload_file(self,disk='media', model_type=None, model_id=None):
	try:
		# check if the post request has the file part
		if 'files' not in request.files:
			resp = jsonify({'message' : 'No file part in the request'})
			resp.status_code = 400
			return resp
		request_json = {
			'disk': disk,
			'model_type': model_type,
			'model_id': model_id
		}
		#request.json.update(request_json)
		response = service.upload(request.files.getlist('files'), request_json)
		return jsonify(response)
	except Exception as e:
		current_app.logger.error(e)

@medias.route('/files-upload/<model_type>/<model_id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['media.delete'])
def delete_media_by_model_type_and_id(self,model_type, model_id):
    message, status = service.delete_media_by_model_type_and_id(model_type,model_id)
    return jsonify({'msg': message}), status

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
		#file_content = file_from_content(file)
		# Create a temporary file to store the content
		with tempfile.NamedTemporaryFile(delete=False) as temp_file:
			temp_file.write(file.read())
			temp_file_path = temp_file.name
		# Send the file using send_file
		response = send_file(temp_file_path, as_attachment=True, download_name=file.filename)

		# Clean up the temporary file after sending
		os.unlink(temp_file_path)

		return response
		#return send_file(file_content, download_name=file.filename, as_attachment=True, last_modified=file.last_modified, mimetype=file.content_type)
    	#return send_from_directory(FileUploadConfig.UPLOAD_FOLDER, filename)