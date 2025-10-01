## service layer of the API
import json
from depot.fields.specialized.image import UploadedImageWithThumb
from depot.manager import DepotManager
from depot.fields.sqlalchemy import UploadedFileField
import uuid
from depot.fields.upload import UploadedFile
import sqlalchemy as sql
from flask import current_app, jsonify
from sqlalchemy_filters import apply_pagination, apply_sort
from werkzeug.utils import secure_filename
from app.common.error_handling import ResourceNotFoundError
from app.utilities.common_utils import debug_return, validate_file_content
from config import BaseConfig
from app.utilities.db_utils import session_scope
from .model import Media
from app.common import filters_serialization
from config import FileUploadConfig
from datetime import datetime, timezone
from app.common.queries import filter_and_sort_query
from app.utilities.request_utils import get_media_url, not_exisit_in_request
from app.utilities.image_process import ImageProcess
from app.utilities.error_utils import handle_errors  # Import the decorator

image_process = ImageProcess()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in FileUploadConfig.ALLOWED_EXTENSIONS

class MediaService:
    @handle_errors("Media")
    def get_all_medias(self, id, filter):
        with session_scope() as session:
            query = session.query(Media)
            
            if id is None:
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Media)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                medias = query.all()
            else:
                medias = query.filter_by(id=id).all()
            
            result = []

            for media in medias:
                data = {
                    'id': media.id,
                    'model_type': media.model_type,
                    'model_id': media.model_id,
                    'collection_name': media.collection_name,
                    'name': media.name,
                    'mime_type': media.mime_type,
                    'disk': media.disk,
                    'size': media.size,
                    'order_column': media.order_column,
                    'file': media.file,
                    'custom_properties': media.custom_properties,
                    'create_date': media.create_date,
                    'last_modified': media.last_modified,
                }
                result.append(data)
            
            if id is None:
                result = {'medias': result, 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                result = {'medias': result}
            return result

    @handle_errors("Media")
    def get_media_obj_by_id(self, id):
        with session_scope() as session:
            media = session.query(Media).filter_by(id=id).first()
            if media is None:
                raise ResourceNotFoundError("Media")
            return media, 200

    @handle_errors("Media")
    def get_model_medias(self, model_type, model_id, filter):
        with session_scope() as session:
            query = session.query(Media)
            query = filter_and_sort_query(filter.filters, filter.sorters, query, Media)

            if model_id is None:
                query = query.filter_by(model_type=model_type)
            else:
                query = query.filter_by(model_type=model_type, model_id=model_id)
            
            query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
            medias = query.all()
            result = []

            for media in medias:
                data = {
                    'id': media.id,
                    'model_type': media.model_type,
                    'model_id': media.model_id,
                    'collection_name': media.collection_name,
                    'name': media.name,
                    'mime_type': media.mime_type,
                    'disk': media.disk,
                    'size': media.size,
                    'order_column': media.order_column,
                    'file': media.file,
                    'custom_properties': media.custom_properties,
                    'create_date': media.create_date,
                    'last_modified': media.last_modified,
                }
                result.append(data)

            result = {'medias': result, 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            return result

    @handle_errors("Media")
    def get_medias_obj_by_model(self, model_type, model_id):
        with session_scope() as session:
            query = session.query(Media).filter_by(model_type=model_type, model_id=model_id)
            query = query.order_by(Media.order_column.asc(), Media.create_date.asc())
            medias = query.all()
            if not medias:
                raise ResourceNotFoundError("Media")
            return medias, 200

    @handle_errors("Media")
    def create_media(self, data):
        with session_scope() as session:
            custom_properties = data.get('custom_properties')
            if custom_properties is not None:
                custom_properties = json.dumps(custom_properties)
            
            model_id = data.get('model_id')
            if isinstance(model_id, uuid.UUID):
                model_id = str(model_id)
            
            media = Media(
                id=uuid.uuid4(),
                model_type=data['model_type'], 
                model_id=model_id, 
                collection_name=not_exisit_in_request(data, 'collection_name'),
                name=data['name'],
                mime_type=not_exisit_in_request(data, 'mime_type'),
                disk=data['disk'],
                size=not_exisit_in_request(data, 'size'),
                order_column=data['order_column'] if 'order_column' in data else 1,
                file=data['file'],
                custom_properties=custom_properties if custom_properties is not None else None,
                create_date=datetime.now(timezone.utc),
                last_modified=datetime.now(timezone.utc)
            )  # type: ignore

            session.add(media)
            session.commit()

            return 'Media Created', 201, media.id, media.file

    @handle_errors("Media")
    def update_media(self, id, data):
        with session_scope() as session:
            media = session.query(Media).filter_by(id=id).first()
            if media is None:
                raise ResourceNotFoundError("Media")

            media.model_type = data['model_type']
            media.model_id = data['model_id']
            media.collection_name = data['collection_name']
            media.name = data['name']
            media.mime_type = data['mime_type']
            media.disk = data['disk']
            media.size = data['size']
            media.order_column = data['order_column']
            media.file = data['file']
            media.custom_properties = data['custom_properties']
            media.last_modified = datetime.now(timezone.utc)

            session.commit()

            return 'Media updated', 200

    @handle_errors("Media")
    def delete_media(self, id):
        with session_scope() as session:
            media = session.query(Media).filter_by(id=id).first()
            if media is None:
                raise ResourceNotFoundError("Media")
            session.delete(media)
            session.commit()
            return 'Media deleted', 200

    @handle_errors("Media")
    def delete_media_by_model_type_and_id(self, model_type, model_id):
        with session_scope() as session:
            session.query(Media).filter_by(model_type=model_type, model_id=model_id).delete(synchronize_session=False)
            session.commit()
            return 'Media deleted', 200

    @handle_errors("Media")
    def update_media_model_id(self, model_id, new_model_id, model_type=None):
        with session_scope() as session:
            query = session.query(Media)
            if model_type is not None:
                query = query.filter_by(model_type=model_type)
            query = query.filter_by(model_id=model_id)
            query.update({'model_id': new_model_id})
            session.commit()
            return 'Media updated', 200

    @handle_errors("Media")
    def upload(self, request_files, request_json, config=None):
        response = []
        files = request_files
        disk = request_json['disk']
        for file in files:
            if file and (allowed_file(file.filename) or validate_file_content(file, FileUploadConfig.ALLOWED_CONTENT_TYPES)):
                mimetype = file.content_type
                filename = secure_filename(file.filename)
                data = {}
                retry = 0
                while retry < 3:
                    try:
                        if mimetype.startswith('image') and 'xml' not in mimetype:
                            if config is not None:
                                if config.get('watermark'):
                                    file.stream = image_process.add_watermark(file)
                                if config.get('compress'):
                                    file.stream = image_process.compress_image(file, config.get('compress'))
                            upload_file = UploadedImageWithThumb(file, disk)
                        else:
                            upload_file = UploadedFile(file, disk)
                        break
                    except Exception as e:
                        current_app.logger.error(e)
                        retry += 1
                        current_app.logger.error(f'Depot: {disk} - Retry: {retry}')
                else:
                    raise Exception(f'DepotManager.configure failed for {disk}')
                data.update({
                    'model_type': request_json['model_type'],
                    'model_id': request_json['model_id'],
                    'collection_name': not_exisit_in_request(request_json, 'collection_name', 'G'),
                    'name': filename,
                    'mime_type': mimetype,
                    'disk': disk,
                    'size': None,
                    'file': upload_file,
                    'order_column': not_exisit_in_request(request_json, 'order_column', 1),
                    'custom_properties': json.dumps(request_json.get('custom_properties')),
                    'create_date': datetime.now(timezone.utc),
                    'last_modified': datetime.now(timezone.utc),
                })
                message, status, media_id, media_file = self.create_media(data)
            else:
                message = 'File type is not allowed'
                status = 400
            resp = {
                'filename': file.filename,
                'message': message,
                'status': status,
                'id': media_id if status == 201 else None,
                'file': get_media_url(media_file) if status == 201 else None,
            }
            response.append(resp)
        return response

    @handle_errors("Media")
    def show(self, depot, fileid):
        depot = DepotManager.get(depot)
        if not depot:
            raise ResourceNotFoundError("Media")
        try:
            file = depot.get(fileid)
        except (IOError, ValueError):
            raise ResourceNotFoundError("Media")

        public_url = file.public_url
        if public_url is not None:
            return public_url, 301
        return file, 200

