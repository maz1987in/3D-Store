## service layer of the API
import sqlalchemy as sql
from flask import current_app, g
from sqlalchemy_filters import apply_pagination, apply_sort
from app.common.error_handling import ResourceNotFoundError
from app.utilities.common_utils import change_string_to_time, debug_return
from .model import FiscalYear, FiscalPeriod
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query
from app.utilities.request_utils import not_exisit_in_request
from datetime import timezone, datetime
import uuid
from app.utilities.db_utils import session_scope
from app.common.enum import FiscalYearStatusEnum
from app.utilities.error_utils import handle_errors  # Import the decorator

class FiscalYearService:
    def get_fiscal_year_model(self, fiscal_years):
        if isinstance(fiscal_years, list):
            result = [fiscal_year.json() for fiscal_year in fiscal_years]
        else:
            result = fiscal_years.json()
        return result

    @handle_errors("FiscalYear")
    def get_fiscal_years(self, id, filter): 
        with session_scope() as session:
            query = session.query(FiscalYear)
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, FiscalYear)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                fiscal_years = query.all()
                result = {'fiscal_years': self.get_fiscal_year_model(fiscal_years), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                fiscal_years = query.filter_by(id=id).all()
                result = {'fiscal_years': self.get_fiscal_year_model(fiscal_years)}

            return result, 200

    @handle_errors("FiscalYear")
    def create_fiscal_year(self, data):
        with session_scope() as session:
            fiscal_year = FiscalYear(
                id=uuid.uuid4(),
                company_id=not_exisit_in_request(data, 'company_id', None),
                start_date=not_exisit_in_request(data, 'start_date', None),
                end_date=not_exisit_in_request(data, 'end_date', None),
                status=FiscalYearStatusEnum(not_exisit_in_request(data, 'status', FiscalYearStatusEnum.OPEN.value)),
                locked=not_exisit_in_request(data, 'locked', False),
                notes=not_exisit_in_request(data, 'notes', None),
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc)
            )
            session.add(fiscal_year)
            session.commit()
        
            return 'FiscalYear Created', 201

    @handle_errors("FiscalYear")
    def update_fiscal_year(self, id, data):
        with session_scope() as session:
            fiscal_year = session.query(FiscalYear).filter_by(id=id).first()
            if fiscal_year is None:
                raise ResourceNotFoundError("FiscalYear")
            fiscal_year.company_id = not_exisit_in_request(data, 'company_id', fiscal_year.company_id)
            fiscal_year.start_date = not_exisit_in_request(data, 'start_date', fiscal_year.start_date)
            fiscal_year.end_date = not_exisit_in_request(data, 'end_date', fiscal_year.end_date)
            fiscal_year.status = FiscalYearStatusEnum(not_exisit_in_request(data, 'status', fiscal_year.status.value))
            fiscal_year.locked = not_exisit_in_request(data, 'locked', fiscal_year.locked)
            fiscal_year.notes = not_exisit_in_request(data, 'notes', fiscal_year.notes)
            fiscal_year.modified_date = datetime.now(timezone.utc)
            
            session.commit()

            return 'Updated', 200

    @handle_errors("FiscalYear")
    def delete_fiscal_year(self, id):
        with session_scope() as session:
            fiscal_year = session.query(FiscalYear).filter_by(id=id).first()

            if fiscal_year is None:
                raise ResourceNotFoundError("FiscalYear")
            
            session.delete(fiscal_year)
            session.commit()

            return 'FiscalYear deleted', 200

    @handle_errors("FiscalYear")
    def get_open_fiscal_years(self, filter):
        with session_scope() as session:
            query = session.query(FiscalYear).filter_by(status=FiscalYearStatusEnum.OPEN)
            if filter.sort is None:
                filter.sorters = create_sorters('start_date', 'asc')
            query = filter_and_sort_query(filter.filters, filter.sorters, query, FiscalYear)

            query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
            fiscal_years = query.all()
            result = {'fiscal_years': self.get_fiscal_year_model(fiscal_years), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            return result, 200

    @handle_errors("FiscalYear")
    def get_current_open_unlocked_fiscal_year(self):
        with session_scope() as session:
            current_year = datetime.now().year
            fiscal_year = session.query(FiscalYear).filter(
                sql.extract('year', FiscalYear.start_date) == current_year,
                FiscalYear.status == FiscalYearStatusEnum.OPEN,
                FiscalYear.locked == False
            ).first()
            if fiscal_year:
                result = self.get_fiscal_year_model(fiscal_year)
                g.fy_id = result['id']  # Store result in global variable
                return result, 200
            else:
                return 'No open and unlocked fiscal year found for the current year', 404

    def get_fiscal_period_model(self, fiscal_periods):
        if isinstance(fiscal_periods, list):
            result = [fiscal_period.json() for fiscal_period in fiscal_periods]
        else:
            result = fiscal_periods.json()
        return result

    @handle_errors("FiscalPeriod")
    def get_fiscal_periods(self, id, filter): 
        with session_scope() as session:
            query = session.query(FiscalPeriod)
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('start_date', 'asc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, FiscalPeriod)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                fiscal_periods = query.all()
                result = {'fiscal_periods': self.get_fiscal_period_model(fiscal_periods), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                fiscal_periods = query.filter_by(id=id).all()
                result = {'fiscal_periods': self.get_fiscal_period_model(fiscal_periods)}

            return result, 200

    @handle_errors("FiscalPeriod")
    def create_fiscal_period(self, data):
        with session_scope() as session:
            fiscal_period = FiscalPeriod(
                id=uuid.uuid4(),
                company_id=not_exisit_in_request(data, 'company_id', None),
                financial_year_id=not_exisit_in_request(data, 'financial_year_id', None),
                period_name=not_exisit_in_request(data, 'period_name', None),
                start_date=not_exisit_in_request(data, 'start_date', None),
                end_date=not_exisit_in_request(data, 'end_date', None),
                status=FiscalYearStatusEnum(not_exisit_in_request(data, 'status', FiscalYearStatusEnum.OPEN.value))
            )
            session.add(fiscal_period)
            session.commit()
        
            return 'FiscalPeriod Created', 201

    @handle_errors("FiscalPeriod")
    def update_fiscal_period(self, id, data):
        with session_scope() as session:
            fiscal_period = session.query(FiscalPeriod).filter_by(id=id).first()
            if fiscal_period is None:
                raise ResourceNotFoundError("FiscalPeriod")
            fiscal_period.company_id = not_exisit_in_request(data, 'company_id', fiscal_period.company_id)
            fiscal_period.financial_year_id = not_exisit_in_request(data, 'financial_year_id', fiscal_period.financial_year_id)
            fiscal_period.period_name = not_exisit_in_request(data, 'period_name', fiscal_period.period_name)
            fiscal_period.start_date = not_exisit_in_request(data, 'start_date', fiscal_period.start_date)
            fiscal_period.end_date = not_exisit_in_request(data, 'end_date', fiscal_period.end_date)
            fiscal_period.status = FiscalYearStatusEnum(not_exisit_in_request(data, 'status', fiscal_period.status.value))
            
            session.commit()

            return 'Updated', 200

    @handle_errors("FiscalPeriod")
    def delete_fiscal_period(self, id):
        with session_scope() as session:
            fiscal_period = session.query(FiscalPeriod).filter_by(id=id).first()

            if fiscal_period is None:
                raise ResourceNotFoundError("FiscalPeriod")
            
            session.delete(fiscal_period)
            session.commit()

            return 'FiscalPeriod deleted', 200
