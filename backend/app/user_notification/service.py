## service layer of the API
import json
import sqlalchemy as sql

from flask import current_app
from sqlalchemy_filters import apply_pagination, apply_sort
from app.common.error_handling import ResourceNotFoundError
from app.utilities.common_utils import debug_return
from config import BaseConfig
from .model import UserNotification
from app.common import filters_serialization
from app.common.queries import filter_and_sort_query, filter_query, create_filters
from datetime import datetime, timezone
import uuid
from app.utilities.db_utils import session_scope
from app.utilities.error_utils import handle_errors  # Import the decorator

class UserNotificationService:
    def get_user_notification_model(self, user_notifications):
        if isinstance(user_notifications, list):
            return [user_notification.json() for user_notification in user_notifications]
        return user_notifications.json()

    @handle_errors("UserNotification")
    def get_user_notifications(self, id, filter): 
        with session_scope() as session:
            query = session.query(UserNotification)

            if id is None:
                query = filter_and_sort_query(filter.filters, filter.sorters, query, UserNotification)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                user_notifications = query.all()
                result = {'user_notifications': self.get_user_notification_model(user_notifications), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                user_notifications = query.filter_by(id=id).first()
                if user_notifications is None:
                    raise ResourceNotFoundError("UserNotification")
                result = {'user_notifications': self.get_user_notification_model(user_notifications)}

            return result, 200

    @handle_errors("UserNotification")
    def update_user_notification(self, id, data):
        with session_scope() as session:
            user_notification = session.query(UserNotification).filter_by(id=id).first()
            if user_notification is None:
                raise ResourceNotFoundError("UserNotification")

            user_notification.name = data['name']
            user_notification.user_id = data['user_id']
            user_notification.read = data['read']
            user_notification.message = data['message']

            session.commit()

            return 'Updated', 200

    @handle_errors("UserNotification")
    def create_user_notification(self, data):
        with session_scope() as session:
            user_notification = UserNotification(
                id=uuid.uuid4(),
                name=data['name'],
                user_id=data['user_id'],
                read=data['read'],
                message=data['message'],
                timestamp=datetime.now(timezone.utc)
            )
            session.add(user_notification)
            session.commit()

            return 'UserNotification Created', 201

    @handle_errors("UserNotification")
    def delete_user_notification(self, id):
        with session_scope() as session:
            user_notification = session.query(UserNotification).filter_by(id=id).first()

            if user_notification is None:
                raise ResourceNotFoundError("UserNotification")
            
            session.delete(user_notification)
            session.commit()

            return 'UserNotification deleted', 200

    @handle_errors("UserNotification")
    def read_user_notification(self, id):
        with session_scope() as session:
            user_notification = session.query(UserNotification).filter_by(id=id).first()
            if user_notification is None:
                raise ResourceNotFoundError("UserNotification")
            user_notification.read = True

            session.commit()

            return 'Read', 200

    @handle_errors("UserNotification")
    def get_user_notifications_by_user_id(self, user_id, filter): 
        with session_scope() as session:
            query = session.query(UserNotification)
            query = query.filter_by(user_id=user_id)
            
            query = filter_and_sort_query(filter.filters, filter.sorters, query, UserNotification)

            query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))

            user_notifications = query.all()
            result = {'user_notifications': self.get_user_notification_model(user_notifications), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            return result, 200

    @handle_errors("UserNotification")
    def get_unread_count_user_notifications_by_user_id(self, user_id): 
        with session_scope() as session:
            count_by_user_id = session.query(UserNotification).filter_by(user_id=user_id).filter(UserNotification.read == False).count()

            return count_by_user_id, 200

    @handle_errors("UserNotification")
    def read_all_user_notifications_by_user_id(self, user_id):
        with session_scope() as session:
            num_rows_updated = session.query(UserNotification).filter_by(user_id=user_id).update({UserNotification.read: True})
            session.commit()

            return 'Read All: ' + str(num_rows_updated), 200

    @handle_errors("UserNotification")
    def delete_all_user_notifications_by_user_id(self, user_id):
        with session_scope() as session:
            num_rows_deleted = session.query(UserNotification).filter_by(user_id=user_id).delete()
            session.commit()

            return 'UserNotification deleted: ' + str(num_rows_deleted), 200