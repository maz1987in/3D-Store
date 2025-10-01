## service layer of the API
import json
import sqlalchemy as sql
from flask import current_app
from sqlalchemy_filters import apply_pagination, apply_sort
from app.utilities.common_utils import change_string_to_time, debug_return
from config import Config
from .model import Company
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query
from app.utilities.request_utils import not_exisit_in_request
from datetime import datetime, timezone
import uuid
from app.utilities.db_utils import session_scope
from app.common.error_handling import ResourceNotFoundError
from app.utilities.error_utils import handle_errors  # Import the decorator

class CompanyService:
    def get_company_model(self, companies):
        if isinstance(companies, list):
            return [company.json() for company in companies]
        return companies.json()

    @handle_errors("Company")
    def get_companies(self, id, filter): 
        with session_scope() as session:
            query = session.query(Company)
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Company)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                companies = query.all()
                result = {
                    'companies': self.get_company_model(companies),
                    'filters': filters_serialization.get_pagination_serialization(
                        pagination, filter.sort, filter.sort_order, filter.queries
                    )
                }
            else:
                companies = query.filter_by(id=id).all()
                result = {'companies': self.get_company_model(companies)}

            return result, 200

    @handle_errors("Company")
    def create_company(self, data):
        with session_scope() as session:
            company = Company(
                id=uuid.uuid4(),
                location=not_exisit_in_request(data, 'location', None),
                manager=not_exisit_in_request(data, 'manager', None),
                cr_number=not_exisit_in_request(data, 'cr_number', None),
                tax_id=not_exisit_in_request(data, 'tax_id', None),
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc)
            )  # type: ignore
            for local in Config.AVAILABLE_LOCALES.keys():
                if isinstance(data['name'], str):
                    company.translations[local].name = json.loads(data['name'])[local]
                else:
                    company.translations[local].name = data['name'][local]

            session.add(company)
            session.commit()
            return 'Company Created', 201

    @handle_errors("Company")
    def update_company(self, id, data):
        with session_scope() as session:
            company = session.query(Company).filter_by(id=id).first()
            if company is None:
                raise ResourceNotFoundError("Company")
            
            company.location = not_exisit_in_request(data, 'location', company.location)
            company.manager = not_exisit_in_request(data, 'manager', company.manager)
            company.cr_number = not_exisit_in_request(data, 'cr_number', company.cr_number)
            company.tax_id = not_exisit_in_request(data, 'tax_id', company.tax_id)
            company.modified_date = datetime.now(timezone.utc)
            
            for local in Config.AVAILABLE_LOCALES.keys():
                if isinstance(data['name'], str):
                    company.translations[local].name = json.loads(data['name'])[local]
                else:
                    company.translations[local].name = data['name'][local]
            
            session.commit()
            return 'Updated', 200

    @handle_errors("Company")
    def delete_company(self, id):
        with session_scope() as session:
            company = session.query(Company).filter_by(id=id).first()
            if company is None:
                raise ResourceNotFoundError("Company")
            
            session.delete(company)
            session.commit()
            return 'Company deleted', 200
