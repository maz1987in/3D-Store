## service layer of the API
import sqlalchemy as sql
from flask import current_app, jsonify, g
from sqlalchemy_filters import apply_pagination, apply_sort
from app.common.error_handling import ResourceNotFoundError
from app.utilities.common_utils import change_string_to_time, debug_return, get_fiscal_year_id
from .model import Transaction
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query
from app.utilities.request_utils import not_exisit_in_request
from datetime import timezone, datetime
import uuid
from app.utilities.db_utils import session_scope
from app.store.model import Store
from app.branch.model import Branch
from app.product.model import Product
from sqlalchemy.orm import aliased
from app.utilities.error_utils import handle_errors  # Import the decorator

class TransactionService:
    def get_transaction_model(self, transactions):
        if isinstance(transactions, list):
            result = []
            for transaction_tuple in transactions:  
                transaction, from_store, from_branch, to_store, to_branch, product = transaction_tuple  

                data = {}

                if transaction:
                    data['transaction'] = transaction.json()

                # from_location can be either a Store or a Branch
                if from_store:
                    data['from_location'] = from_store.json()
                elif from_branch:
                    data['from_location'] = from_branch.json()
                else:
                    data['from_location'] = None  

                # to_location can be either a Store or a Branch
                if to_store:
                    data['to_location'] = to_store.json()
                elif to_branch:
                    data['to_location'] = to_branch.json()
                else:
                    data['to_location'] = None  

                if product:
                    data['product'] = product.json()

                result.append(data)
            return result
        return transactions.json()
    
    @handle_errors("Transaction")
    def get_transactions(self, id, filter): 
        with session_scope() as session:
            FromStore = aliased(Store)  # Store for from_location_id
            FromBranch = aliased(Branch)  # Branch for from_location_id
            ToStore = aliased(Store)  # Store for to_location_id
            ToBranch = aliased(Branch)  # Branch for to_location_id

            query = (
                session.query(Transaction, FromStore, FromBranch, ToStore, ToBranch, Product)
                .outerjoin(FromStore, Transaction.from_location_id == FromStore.id)  # from_location_id might be Store
                .outerjoin(FromBranch, Transaction.from_location_id == FromBranch.id)  # from_location_id might be Branch
                .outerjoin(ToStore, Transaction.to_location_id == ToStore.id)  # to_location_id might be Store
                .outerjoin(ToBranch, Transaction.to_location_id == ToBranch.id)  # to_location_id might be Branch
                .outerjoin(Product, Transaction.product_id == Product.id)
            )

            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Transaction)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                transactions = query.all()
                result = {'transactions': self.get_transaction_model(transactions), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                transactions = query.filter_by(id=id).first()
                if transactions is None:
                    raise ResourceNotFoundError("Transaction")
                result = {'transactions': self.get_transaction_model(transactions)}

            return result, 200
    
    @handle_errors("Transaction")
    def create_transaction(self, data, session=None):
        """Create a transaction record.
        
        Args:
            data (dict): transaction details
            session (Session, optional): SQLAlchemy session. 
                If None, a new session will be created and committed.
        """
        own_session = False
        if session is None:
            own_session = True
            session_ctx = session_scope()
            session = session_ctx.__enter__()

        try:
            financial_year_id = get_fiscal_year_id()
            transaction = Transaction(
                id=uuid.uuid4(),
                product_id=data['product_id'],
                from_location_id=not_exisit_in_request(data, 'from_location_id', None),
                to_location_id=not_exisit_in_request(data, 'to_location_id', None),
                quantity=not_exisit_in_request(data, 'quantity', 0),
                transaction_type=not_exisit_in_request(data, 'transaction_type', None),
                transaction_date=change_string_to_time(data['transaction_date']),
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc),
                financial_year_id=financial_year_id
            )  # type: ignore

            session.add(transaction)

            if own_session:  # only commit if we created the session
                session.commit()

            return 'Transaction Created', 201

        except Exception:
            if own_session:
                session.rollback()
            raise

        finally:
            if own_session:
                session_ctx.__exit__(None, None, None)


    @handle_errors("Transaction")
    def update_transaction(self, id, data):
        with session_scope() as session:
            financial_year_id = get_fiscal_year_id()
            transaction = session.query(Transaction).filter_by(id=id).first()
            if transaction is None:
                raise ResourceNotFoundError("Transaction")
            transaction.product_id = not_exisit_in_request(data, 'product_id', transaction.product_id)
            transaction.from_location_id = not_exisit_in_request(data, 'from_location_id', transaction.from_location_id)
            transaction.to_location_id = not_exisit_in_request(data, 'to_location_id', transaction.to_location_id)
            transaction.quantity = not_exisit_in_request(data, 'quantity', transaction.quantity)
            transaction.transaction_type = not_exisit_in_request(data, 'transaction_type', transaction.transaction_type)
            transaction.transaction_date = change_string_to_time(data['transaction_date'])
            transaction.financial_year_id = financial_year_id

            session.commit()

            return 'Updated', 200
    
    @handle_errors("Transaction")
    def delete_transaction(self, id):
        with session_scope() as session:
            transaction = session.query(Transaction).filter_by(id=id).first()

            if transaction is None:
                raise ResourceNotFoundError("Transaction")
            
            session.delete(transaction)
            session.commit()

            return 'Transaction deleted', 200

    @handle_errors("Transaction")
    def get_total_transactions_by_type(self, transaction_type=None, filters=None):
        """
        Get the total number of transactions, optionally filtered by transaction_type and other criteria.
        """
        with session_scope() as session:
            query = session.query(sql.func.count(Transaction.id))
            
            # Filter by transaction_type if provided
            if transaction_type:
                query = query.filter(Transaction.transaction_type == transaction_type)
            
            # Apply additional filters if provided
            if filters:
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Transaction)

            total_count = query.scalar()
            return {'total_transactions_count': total_count or 0}, 200

    @handle_errors("Transaction")
    def get_total_transactions(self, filter=None):
        """
        Get the total number of transactions, optionally filtered by criteria.
        """
        with session_scope() as session:
            query = session.query(sql.func.count(Transaction.id))
            
            # Apply additional filters if provided
            if filter:
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Transaction)

            total_count = query.scalar()
            return {'total_transactions_count': total_count or 0}, 200
