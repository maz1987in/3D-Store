## service layer of the API
import json
import sqlalchemy as sql
from flask import current_app
from sqlalchemy_filters import apply_pagination, apply_sort
from app.common.enum import MediaTypeEnum
from app.common.error_handling import ResourceNotFoundError
from app.utilities.common_utils import debug_return, uuid_to_string
from app.utilities.request_utils import not_exisit_in_request
from config import BaseConfig, Config
from .model import TemplatesContent
from app.common import filters_serialization
from app.common.queries import filter_and_sort_query, filter_query, create_filters
from datetime import datetime, timezone
import uuid
from app.utilities.db_utils import session_scope
from app.utilities.error_utils import handle_errors  # Import the decorator

class TemplatesContentService:
    def get_templates_content_model(self, templates_contents):
        if isinstance(templates_contents, list):
            result = [tc.json() for tc in templates_contents]
        else:
            result = templates_contents.json()
        return result

    @handle_errors("TemplatesContent")
    def get_templates_contents(self, id, filter): 
        with session_scope() as session:
            query = session.query(TemplatesContent)
                    
            if id is None:
                query = filter_and_sort_query(filter.filters, filter.sorters, query, TemplatesContent)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                templates_contents = query.all()
                result = {'templates_contents': self.get_templates_content_model(templates_contents), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                templates_contents = query.filter_by(id=id).first()
                if templates_contents is None:
                    raise ResourceNotFoundError("TemplatesContent")
                result = {'templates_contents': self.get_templates_content_model(templates_contents)}
        
            return result, 200

    @handle_errors("TemplatesContent")
    def update_templates_content(self, id, data):
        with session_scope() as session:
            templates_content = session.query(TemplatesContent).filter_by(id=id).first()
            if templates_content is None:
                raise ResourceNotFoundError("TemplatesContent")

            templates_content.key = data['key']
            templates_content.media_type = MediaTypeEnum(not_exisit_in_request(data, 'media_type', templates_content.model_type))
            templates_content.model_type = not_exisit_in_request(data, 'model_type', templates_content.model_type)
            templates_content.model_op = data['model_op']
            templates_content.model_id = not_exisit_in_request(data, 'model_id')
            templates_content.description = not_exisit_in_request(data, 'description')
            templates_content.modified_date = datetime.now(timezone.utc)
            for local in Config.AVAILABLE_LOCALES.keys():
                if isinstance(data['subject'], str):
                    templates_content.translations[local].subject = json.loads(data['subject'])[local]
                    templates_content.translations[local].content = json.loads(data['content'])[local]
                else:
                    templates_content.translations[local].subject = data['subject'][local]
                    templates_content.translations[local].content = data['content'][local]

            session.commit()

            return 'Updated', 200

    @handle_errors("TemplatesContent")
    def create_templates_content(self, data):
        with session_scope() as session:
            templates_content = TemplatesContent(
                id=uuid.uuid4(),
                key=data['key'],
                model_type=data['model_type'],
                model_op=data['model_op'],
                model_id=not_exisit_in_request(data, 'model_id'),
                media_type=MediaTypeEnum(not_exisit_in_request(data, 'media_type', MediaTypeEnum.SMS)),
                description=not_exisit_in_request(data, 'description'),
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc)
            )  # type: ignore
            for local in Config.AVAILABLE_LOCALES.keys():
                templates_content.translations[local].subject = data['subject'][local]
                templates_content.translations[local].content = data['content'][local]

            session.add(templates_content)
            session.commit()

            return 'TemplatesContent Created', 201

    @handle_errors("TemplatesContent")
    def delete_templates_content(self, id):
        with session_scope() as session:
            templates_content = session.query(TemplatesContent).filter_by(id=id).first()

            if templates_content is None:
                raise ResourceNotFoundError("TemplatesContent")
            
            session.delete(templates_content)
            session.commit()

            return 'TemplatesContent deleted', 200

    @handle_errors("TemplatesContent")
    def get_templates_contents_by_key(self, key): 
        with session_scope() as session:
            query = session.query(TemplatesContent)
            query = query.filter(TemplatesContent.key == key)
            templates_contents = query.all()
        
            if templates_contents is None:
                raise ResourceNotFoundError("TemplatesContent")
            return self.get_templates_content_model(templates_contents), 200

    @handle_errors("TemplatesContent")
    def delete_templates_contents_by_key_and_model_id(self, key, model_id):
        with session_scope() as session:
            templates_content = session.query(TemplatesContent).filter_by(key=key, model_id=model_id).first()

            if templates_content is None:
                raise ResourceNotFoundError("TemplatesContent")
            
            session.delete(templates_content)
            session.commit()

            return 'TemplatesContent deleted', 200