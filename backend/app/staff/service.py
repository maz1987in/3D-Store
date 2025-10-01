## service layer of the API
import json
import sqlalchemy as sql

from flask import current_app
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy_filters import apply_pagination
from app.common.error_handling import ResourceNotFoundError
from app.utilities.common_utils import change_string_to_time, debug_return
from config import Config
from app.utilities.request_utils import not_exisit_in_request, get_media_url
from app.utilities.db_utils import session_scope
from app.medias.service import MediaService
from datetime import datetime, timezone
import uuid
from .model import Staff
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query
from app.utilities.file_upload_utils import upload_files, delete_file, reindex_media
from app.utilities.error_utils import handle_errors  # Import the decorator

media_service = MediaService()

class StaffService:
    def get_staff_model(self, staffs):
        if isinstance(staffs, list):
            return [staff.json() for staff in staffs]
        return staffs.json()

    @handle_errors("Staff")
    def get_staffs(self, id, filter): 
        with session_scope() as session:
            query = session.query(Staff)
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Staff)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                staffs = query.all()
                result = {'staffs': self.get_staff_model(staffs), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                staffs = query.filter_by(id=id).first()
                if staffs is None:
                    raise ResourceNotFoundError("Staff")
                result = {'staffs': self.get_staff_model(staffs)}

            return result, 200

    @handle_errors("Staff")
    def create_staff(self, data, files):
        with session_scope() as session:
            staff_id = uuid.uuid4()
            staff = Staff(
                id=staff_id,
                nationality=not_exisit_in_request(data, 'nationality', None),
                name=not_exisit_in_request(data, 'name', None),
                id_card_number=not_exisit_in_request(data, 'id_card_number', None),
                expiry_date=change_string_to_time(data['expiry_date']),
                salary=not_exisit_in_request(data, 'salary', 0.0),
                details=not_exisit_in_request(data, 'details', None),
                attachments=[],
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc)
            )

            session.add(staff)
            session.commit()

            self.upload_staff_files(str(staff_id), files.getlist('attachments') if 'attachments' in files else [])

            return 'Staff Created', 201

    @handle_errors("Staff")
    def update_staff(self, id, data, files):
        with session_scope() as session:
            staff = session.query(Staff).filter_by(id=id).first()
            if staff is None:
                raise ResourceNotFoundError("Staff")
            staff.nationality = not_exisit_in_request(data, 'nationality', staff.nationality)
            staff.name = not_exisit_in_request(data, 'name', staff.name)
            staff.id_card_number = not_exisit_in_request(data, 'id_card_number', staff.id_card_number)
            staff.expiry_date = change_string_to_time(data['expiry_date']) if 'expiry_date' in data else staff.expiry_date
            staff.salary = not_exisit_in_request(data, 'salary', staff.salary)
            staff.details = not_exisit_in_request(data, 'details', staff.details)
            staff.modified_date = datetime.now(timezone.utc)

            if files:
                self.upload_staff_files(staff.id, files.getlist('attachments') if 'attachments' in files else [])
            else:
                self.reindex_staff_attachments(id)

            session.commit()

            return 'Updated', 200

    @handle_errors("Staff")
    def delete_staff(self, id):
        with session_scope() as session:
            staff = session.query(Staff).filter_by(id=id).first()
            if staff is None:
                raise ResourceNotFoundError("Staff")
            session.delete(staff)
            session.commit()
            return 'Staff deleted', 200

    @handle_errors("Staff")
    def upload_staff_files(self, id, attachments, order=1, is_new=False):
        with session_scope() as session:
            return upload_files(
                session, Staff, 'staff', id, attachments, 'attachments', order, is_new
            )

    @handle_errors("Staff")
    def delete_staff_file(self, media_id):
        return delete_file(media_service, 'staff', media_id)

    @handle_errors("Staff")
    def reindex_staff_attachments(self, staff_id):
        with session_scope() as session:
            return reindex_media(session, Staff, 'staff', staff_id)
