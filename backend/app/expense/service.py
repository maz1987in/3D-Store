## service layer of the API
import json
import sqlalchemy as sql

from flask import current_app, jsonify, g
from sqlalchemy_filters import apply_pagination, apply_sort
from app.utilities.common_utils import change_string_to_time, debug_return, get_fiscal_year_id
from config import BaseConfig, Config
from .model import Expense, ExpenseCategory
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query
from app.utilities.request_utils import not_exisit_in_request
from datetime import timezone, datetime
import uuid
from app.utilities.db_utils import session_scope
from app.utilities.file_upload_utils import upload_files, delete_file, reindex_media
from app.medias.service import MediaService
from app.common.error_handling import ResourceNotFoundError
from app.utilities.error_utils import handle_errors  # Import the decorator

media_service = MediaService()

class ExpenseService:
    def get_expense_model(self, expenses):
        if isinstance(expenses, list):
            return [expense.json() for expense in expenses]
        return expenses.json()

    @handle_errors("Expense")
    def get_expenses(self, id, filter): 
        with session_scope() as session:
            query = session.query(Expense).join(ExpenseCategory, Expense.category_id == ExpenseCategory.id)
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, [Expense, ExpenseCategory])

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                expenses = query.all()
                result = {'expenses': self.get_expense_model(expenses), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                expenses = query.filter_by(id=id).first()
                if expenses is None:
                    raise ResourceNotFoundError("Expense")
                result = {'expenses': self.get_expense_model(expenses)}

            return result, 200

    @handle_errors("Expense")
    def create_expense(self, data, files):
        with session_scope() as session:
            fiscal_year_id = get_fiscal_year_id()
            expense_id = uuid.uuid4()
            expense = Expense(
                id=expense_id,
                name=not_exisit_in_request(data, 'name', None),
                category_id=not_exisit_in_request(data, 'category_id', None),
                date=change_string_to_time(data['date']),
                amount=not_exisit_in_request(data, 'amount', 0.0),
                description=not_exisit_in_request(data, 'description', None),
                status=not_exisit_in_request(data, 'status', 'PENDING'),
                attachments=[],
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc),
                fiscal_year_id=fiscal_year_id
            )

            session.add(expense)
            session.commit()

            self.upload_expense_files(str(expense_id), files.getlist('attachments') if 'attachments' in files else [])

            return 'Expense Created', 201

    @handle_errors("Expense")
    def update_expense(self, id, data, files):
        with session_scope() as session:
            fiscal_year_id = get_fiscal_year_id()
            expense = session.query(Expense).filter_by(id=id).first()
            if expense is None:
                raise ResourceNotFoundError("Expense")

            expense.name = not_exisit_in_request(data, 'name', expense.name)
            expense.category_id = not_exisit_in_request(data, 'category_id', expense.category_id)
            expense.date = change_string_to_time(data['date']) if 'date' in data else expense.date
            expense.amount = not_exisit_in_request(data, 'amount', expense.amount)
            expense.description = not_exisit_in_request(data, 'description', expense.description)
            expense.status = not_exisit_in_request(data, 'status', expense.status)
            expense.modified_date = datetime.now(timezone.utc)
            expense.fiscal_year_id = fiscal_year_id

            if files:
                self.upload_expense_files(expense.id, files.getlist('attachments') if 'attachments' in files else [])
            else:
                self.reindex_expense_attachments(id)

            session.commit()

            return 'Updated', 200

    @handle_errors("Expense")
    def delete_expense(self, id):
        with session_scope() as session:
            expense = session.query(Expense).filter_by(id=id).first()

            if expense is None:
                raise ResourceNotFoundError("Expense")
            
            session.delete(expense)
            session.commit()

            return 'Expense deleted', 200

    @handle_errors("Expense")
    def upload_expense_files(self, id, attachments, order=1, is_new=False):
        with session_scope() as session:
            return upload_files(
                session, Expense, 'expense', id, attachments, 'attachments', order, is_new
            )

    @handle_errors("Expense")
    def delete_expense_file(self, media_id):
        return delete_file(media_service, 'expense', media_id)

    @handle_errors("Expense")
    def reindex_expense_attachments(self, expense_id):
        with session_scope() as session:
            return reindex_media(session, Expense, 'expense', expense_id)

    @handle_errors("Expense")
    def get_total_expenses_amount(self, filter=None):
        """
        Get the total amount of expenses, optionally filtered by criteria.
        """
        with session_scope() as session:
            query = session.query(sql.func.sum(Expense.amount))
            
            # Apply filters if provided
            if filter:
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Expense)

            total_amount = query.scalar()
            return {'total_expenses_amount': total_amount or 0.0}, 200

    def get_expense_category_model(self, categories):
        if isinstance(categories, list):
            return [category.json() for category in categories]
        return [categories.json()]
    
    @handle_errors("Expense Category")
    def get_expense_categories(self, id, filter): 
        with session_scope() as session:
            query = session.query(ExpenseCategory)
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, ExpenseCategory)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                categories = query.all()
                result = {'categories': self.get_expense_category_model(categories), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                categories = query.filter_by(id=id).all()
                result = {'categories': self.get_expense_category_model(categories)}

            return result, 200

    @handle_errors("Expense Category")
    def create_expense_category(self, data):
        with session_scope() as session:
            category = ExpenseCategory(
                id=uuid.uuid4(),
                parent_id=not_exisit_in_request(data, 'parent_id', None),
                order=not_exisit_in_request(data, 'order', 0)
            )
            for local in Config.AVAILABLE_LOCALES.keys():
                if isinstance(data['name'], str):
                    category.translations[local].name = json.loads(data['name'])[local]
                    category.translations[local].content = json.loads(data['content'])[local]
                else:
                    category.translations[local].name = data['name'][local]
                    category.translations[local].content = data['content'][local]

            session.add(category)
            session.commit()
        
            return 'Expense Category Created', 201

    @handle_errors("Expense Category")
    def update_expense_category(self, id, data):
        with session_scope() as session:
            category = session.query(ExpenseCategory).filter_by(id=id).first()
            category.parent_id = not_exisit_in_request(data, 'parent_id', category.parent_id)
            category.order = not_exisit_in_request(data, 'order', category.order)
            for local in Config.AVAILABLE_LOCALES.keys():
                if isinstance(data['name'], str):
                    category.translations[local].name = json.loads(data['name'])[local]
                    category.translations[local].content = json.loads(data['content'])[local]
                else:
                    category.translations[local].name = data['name'][local]
                    category.translations[local].content = data['content'][local]
            session.commit()

            return 'Updated', 200

    @handle_errors("Expense Category")
    def delete_expense_category(self, id):
        with session_scope() as session:
            category = session.query(ExpenseCategory).filter_by(id=id).first()

            if category is None:
                raise ResourceNotFoundError("Expense Category")
            
            session.delete(category)
            session.commit()

            return 'Expense Category deleted', 200
