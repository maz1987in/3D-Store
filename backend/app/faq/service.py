## service layer of the API
import json
import sqlalchemy as sql
from flask import current_app
from sqlalchemy_filters import apply_pagination, apply_sort
from app.utilities.common_utils import debug_return, change_string_to_time
from config import BaseConfig, Config
from .model import Faq, FaqTopic
from app.common import filters_serialization
from app.common.queries import filter_and_sort_query
from datetime import datetime, timezone
from extensions import cache
import uuid
from app.utilities.db_utils import session_scope
from app.common.error_handling import ResourceNotFoundError
from app.utilities.error_utils import handle_errors  # Import the decorator

class FaqService:
    def get_faq_model(self, faqs):
        if isinstance(faqs, list):
            result = [self.get_faq_item(faq) for faq in faqs]
        else:
            result = self.get_faq_item(faqs)
        return result

    def get_faq_item(self, faq):
        result = {}
        if faq is not None:
            topic = None
            if hasattr(faq, 'FaqTopic'):
                if faq.FaqTopic:
                    topic = faq.FaqTopic.for_short()
            if hasattr(faq, 'Faq'):
                faq = faq.Faq
            result = faq.json()
            if topic is not None:
                result['faq_topic'] = topic
        return result

    def get_faq_topic_model(self, faq_topics):
        if isinstance(faq_topics, list):
            result = [faq_topic.json() for faq_topic in faq_topics]
        else:
            result = faq_topics.json()
        return result

    @handle_errors("Faq")
    @cache.memoize(60 * 60)
    def get_faqs(self, id, filter):
        with session_scope() as session:
            query = session.query(Faq, FaqTopic)
            query = query.join(FaqTopic, Faq.faq_topic_id == FaqTopic.id, isouter=True)

            if id is None:
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Faq)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                faqs = query.all()

                result = {'faqs': self.get_faq_model(faqs), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                faqs = query.filter_by(id=id).first()
                if faqs is None:
                    raise ResourceNotFoundError("Faq")
                result = {'faqs': self.get_faq_model(faqs)}

            return result, 200

    @handle_errors("Faq")
    def update_faq(self, id, data):
        with session_scope() as session:
            faq = session.query(Faq).filter_by(id=id).first()
            if faq is None:
                raise ResourceNotFoundError("Faq")
            faq.faq_topic_id = data['faq_topic_id']

            faq.modified_date = datetime.now(timezone.utc)
            for local in Config.AVAILABLE_LOCALES.keys():
                if isinstance(data['content'], str):
                    faq.translations[local].content = json.loads(data['content'])[local]
                    faq.translations[local].question = json.loads(data['question'])[local]
                else:
                    faq.translations[local].content = data['content'][local]
                    faq.translations[local].question = data['question'][local]

            session.commit()
            return 'Updated', 200

    @handle_errors("Faq")
    def create_faq(self, data):
        with session_scope() as session:
            faq = Faq(
                id=uuid.uuid4(),
                faq_topic_id=data['faq_topic_id'],
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc)
            )
            for local in Config.AVAILABLE_LOCALES.keys():
                faq.translations[local].content = data['content'][local]
                faq.translations[local].question = data['question'][local]

            session.add(faq)
            session.commit()

            return 'Faq Created', 201

    @handle_errors("Faq")
    def delete_faq(self, id):
        with session_scope() as session:
            faq = session.query(Faq).filter_by(id=id).first()

            if faq is None:
                raise ResourceNotFoundError("Faq")

            session.delete(faq)
            session.commit()

            return 'Faq deleted', 200

    @handle_errors("Faq")
    def get_faqs_by_faq_topic(self, faq_topic_id):
        with session_scope() as session:
            faqs = session.query(Faq).filter_by(faq_topic_id=faq_topic_id).all()

            if not faqs:
                raise ResourceNotFoundError("Faq")
            result = {'faqs': self.get_faq_model(faqs)}
            return result, 200

    @handle_errors("FaqTopic")
    def get_faq_topics(self, id, filter):
        with session_scope() as session:
            query = session.query(FaqTopic)

            if id is None:
                query = filter_and_sort_query(filter.filters, filter.sorters, query, FaqTopic)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                faq_topics = query.all()
                result = {'faq_topics': self.get_faq_topic_model(faq_topics), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                faq_topics = query.filter_by(id=id).first()
                if faq_topics is None:
                    raise ResourceNotFoundError("FaqTopic")
                result = {'faq_topics': self.get_faq_topic_model(faq_topics)}

            return result, 200

    @handle_errors("FaqTopic")
    def update_faq_topic(self, id, data):
        with session_scope() as session:
            faq_topic = session.query(FaqTopic).filter_by(id=id).first()
            if faq_topic is None:
                raise ResourceNotFoundError("FaqTopic")

            faq_topic.modified_date = datetime.now(timezone.utc)
            for local in Config.AVAILABLE_LOCALES.keys():
                faq_topic.translations[local].title = data['title'][local]

            session.commit()
            return 'Updated', 200

    @handle_errors("FaqTopic")
    def create_faq_topic(self, data):
        with session_scope() as session:
            faq_topic = FaqTopic(
                id=uuid.uuid4(),
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc)
            )
            for local in Config.AVAILABLE_LOCALES.keys():
                faq_topic.translations[local].title = data['title'][local]

            session.add(faq_topic)
            session.commit()

            return 'FaqTopic Created', 201

    @handle_errors("FaqTopic")
    def delete_faq_topic(self, id):
        with session_scope() as session:
            faq_topic = session.query(FaqTopic).filter_by(id=id).first()

            if faq_topic is None:
                raise ResourceNotFoundError("FaqTopic")

            session.delete(faq_topic)
            session.commit()

            return 'FaqTopic deleted', 200