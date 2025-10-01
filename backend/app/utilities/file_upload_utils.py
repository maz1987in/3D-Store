import sqlalchemy as sql
from sqlalchemy.orm.attributes import flag_modified
from flask import current_app
from app.medias.service import MediaService
from app.utilities.request_utils import get_media_url
from app.utilities.error_utils import handle_errors  # Import the decorator

media_service = MediaService()

@handle_errors("FileUpload")
def upload_files(session, model, model_type, model_id, files, collection_name, order=1, is_new=False):
    """
    Handles file uploads for a given model.

    :param session: SQLAlchemy session
    :param model: SQLAlchemy model class
    :param model_type: Type of the model (e.g., 'product', 'staff')
    :param model_id: ID of the model instance
    :param files: List of files to upload
    :param collection_name: Collection name for the files (e.g., 'images', 'attachments')
    :param order: Order of the files
    :param is_new: Whether the model instance is new
    :return: Tuple (message, processed_media, status)
    """
    processed_media = []
    instance = session.query(model).filter(model.id == model_id).options(sql.orm.load_only(collection_name)).first()
    if instance is None and not is_new:
        return 'Not Found', [], 404

    if files:
        media = {
            'model_type': model_type,
            'model_id': model_id,
            'disk': model_type,
            'collection_name': collection_name,
            'order_column': order
        }
        media_files = media_service.upload(files, media)
        for file in media_files:
            if file['status'] == 201:
                simple_media_info = {'id': str(file['id']), 'file': file['file']}
                processed_media.append(simple_media_info)
                if not is_new:
                    if getattr(instance, collection_name) is not None:
                        getattr(instance, collection_name).append(simple_media_info)
                    else:
                        setattr(instance, collection_name, [simple_media_info])

        if not is_new:
            flag_modified(instance, collection_name)

    if not is_new:
        session.merge(instance)
        session.commit()

    return 'File uploaded', processed_media, 200


@handle_errors("FileUpload")
def delete_file(media_service, model_type, media_id):
    """
    Deletes a specific file by its media ID and reindexes the associated model.

    :param media_service: MediaService instance
    :param model_type: Type of the model (e.g., 'product', 'staff')
    :param media_id: ID of the media to delete
    :return: Tuple (message, status)
    """
    media, media_status = media_service.get_media_obj_by_id(media_id)
    if media_status != 200:
        return media, media_status

    model_id = media.model_id
    message, status = media_service.delete_media(media_id)
    if status != 200:
        return message, status

    return reindex_media(media_service, model_type, model_id)


@handle_errors("FileUpload")
def reindex_media(session, model, model_type, model_id):
    """
    Reindexes media (images and attachments) for a given model.

    :param session: SQLAlchemy session
    :param model: SQLAlchemy model class
    :param model_type: Type of the model (e.g., 'product', 'staff')
    :param model_id: ID of the model instance
    :return: Tuple (message, status)
    """
    instance = session.query(model).filter(model.id == model_id).first()
    if instance is None:
        return 'Not Found', 404

    medias, medias_status = media_service.get_medias_obj_by_model(model_type, model_id)
    if medias_status != 200:
        return medias, medias_status

    images = []
    attachments = []
    for media in medias:
        if media.collection_name == 'images':
            images.append({'id': str(media.id), 'file': get_media_url(media.file)})
        elif media.collection_name == 'attachments':
            attachments.append({'id': str(media.id), 'file': get_media_url(media.file)})

    if hasattr(instance, 'images'):
        instance.images = images
        flag_modified(instance, "images")
    if hasattr(instance, 'attachments'):
        instance.attachments = attachments
        flag_modified(instance, "attachments")

    session.merge(instance)
    session.commit()
    return 'Media reindexed', 200