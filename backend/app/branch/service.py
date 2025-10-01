## service layer of the API
import json
import sqlalchemy as sql

from flask import current_app,jsonify
from sqlalchemy_filters import apply_pagination, apply_sort
from app.common.error_handling import ResourceNotFoundError
from app.utilities.common_utils import change_string_to_time, debug_return
from app.utilities.error_utils import handle_errors
from config import BaseConfig, Config
from .model import Branch
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query, filter_query, create_filters
from app.utilities.request_utils import not_exisit_in_request
from datetime import date, datetime
import uuid
from app.utilities.db_utils import get_session_with_retries, session_scope
from datetime import timezone

class BranchService:
    def get_branch_model(self, branchs):
        if isinstance(branchs, list):
            return [branch.json() for branch in branchs]
        return branchs.json()

    @handle_errors("Branch")
    def get_branchs(self, id, filter): 
        with session_scope() as session:
            query = session.query(Branch)
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Branch)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                branchs = query.all()
                result = {
                    'branchs': self.get_branch_model(branchs),
                    'filters': filters_serialization.get_pagination_serialization(
                        pagination, filter.sort, filter.sort_order, filter.queries
                    )
                }
            else:
                branchs = query.filter_by(id=id).first()
                if branchs is None:
                    raise ResourceNotFoundError("Branch")
                result = {'branchs': self.get_branch_model(branchs)}

            return result, 200

    @handle_errors("Branch")
    def create_branch(self, data):
        with session_scope() as session:
            branch = Branch(
                id=uuid.uuid4(),
                location=not_exisit_in_request(data, 'location', None),
                manager=not_exisit_in_request(data, 'manager', None),
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc)
            )  # type: ignore
            for local in Config.AVAILABLE_LOCALES.keys():
                if isinstance(data['name'], str):
                    branch.translations[local].name = json.loads(data['name'])[local]
                else:
                    branch.translations[local].name = data['name'][local]

            session.add(branch)  
            session.commit()

            return 'Branch Created', 201

    @handle_errors("Branch")
    def update_branch(self, id, data):
        with session_scope() as session:
            branch = session.query(Branch).filter_by(id=id).first()  
            if branch is None:
                raise ResourceNotFoundError("Branch")
            branch.location = not_exisit_in_request(data, 'location', branch.location)
            branch.manager = not_exisit_in_request(data, 'manager', branch.manager)
            branch.modified_date = datetime.now(timezone.utc)
            for local in Config.AVAILABLE_LOCALES.keys():
                if isinstance(data['name'], str):
                    branch.translations[local].name = json.loads(data['name'])[local]
                else:
                    branch.translations[local].name = data['name'][local]
            session.commit()

            return 'Updated', 200

    @handle_errors("Branch")
    def delete_branch(self, id):
        with session_scope() as session:
            branch = session.query(Branch).filter_by(id=id).first()

            if branch is None:
                raise ResourceNotFoundError("Branch")
            
            session.delete(branch)
            session.commit()

            return 'Branch deleted', 200
