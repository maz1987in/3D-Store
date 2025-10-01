## service layer of the API
import json
import sqlalchemy as sql
from datetime import datetime, timezone, timedelta
from flask import current_app
from sqlalchemy.sql.sqltypes import Float
from sqlalchemy_filters import apply_pagination, apply_sort
from app.common.enum import PaymentStatusEnum
from app.common.error_handling import ResourceNotFoundError
from app.users.model import User
from app.utilities.common_utils import debug_return
from app.utilities.request_utils import is_exisit_in_request, not_exisit_in_request, str_to_bool
from config import BaseConfig
from .model import PaymentTransaction, PaymentConfig, PaymentGateway, PaymentType
from app.common import filters_serialization
from sqlalchemy_utils.types.uuid import UUIDType
import uuid
from app.common.queries import create_sorters, filter_and_sort_query
from app.utilities.db_utils import session_scope
from app.utilities.error_utils import handle_errors  # Import the decorator

class PaymentTransactionsService:

    def get_payment_transaction_item(self, pt):
        user = None
        if hasattr(pt, 'User'):
            user = pt.User
        
        if hasattr(pt, 'PaymentTransaction'): 
            pt = pt.PaymentTransaction
        data = pt.json()
        if user:
            data['requester'] = user.for_short()
        return data

    def get_payment_transactions_model(self, payment_transactions):
        if isinstance(payment_transactions, list):
            return [self.get_payment_transaction_item(pt) for pt in payment_transactions]
        return self.get_payment_transaction_item(payment_transactions)

    @handle_errors("PaymentTransaction")
    def get_all_payment_transactions(self, id, filter):
        with session_scope() as session:
            query = session.query(PaymentTransaction, User).filter(PaymentTransaction.requester == User.id)
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('create_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, [PaymentTransaction, User])
                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                payment_transactions = query.all()
                result = {
                    'payments': self.get_payment_transactions_model(payment_transactions),
                    'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries),
                }
            else:
                payment_transactions = query.filter(PaymentTransaction.id == id).all()
                result = {'payments': self.get_payment_transactions_model(payment_transactions)}
            return result, 200

    @handle_errors("PaymentGateway")
    def get_gateways(self):
        with session_scope() as session:
            gateways = session.query(PaymentGateway).all()
            result = [{'name': gateway.name} for gateway in gateways]
            return result, 200

    @handle_errors("PaymentGateway")
    def create_payment_gateway(self, data):
        with session_scope() as session:
            payment_gateway = PaymentGateway(name=data['name'])
            session.add(payment_gateway)
            session.commit()
            return 'PaymentGateway Created', 201

    @handle_errors("PaymentGateway")
    def delete_payment_gateway(self, id):
        with session_scope() as session:
            payment_gateway = session.query(PaymentGateway).filter_by(id=id).first()
            if payment_gateway is None:
                raise ResourceNotFoundError("PaymentGateway")
            session.delete(payment_gateway)
            session.commit()
            return 'PaymentGateway Deleted', 200

    @handle_errors("PaymentTransaction")
    def create_payment_transaction(self, data):
        with session_scope() as session:
            pt = PaymentTransaction(
                id=uuid.uuid4(),
                active=not_exisit_in_request(data, 'active', True),
                requester=data['requester'],
                reference_id=data['reference_id'],
                gateway_transaction_id=not_exisit_in_request(data, 'gateway_transaction_id'),
                payment_status=data['payment_status'],
                gateway_status=not_exisit_in_request(data, 'gateway_status'),
                amount=data['amount'],
                vat=data['vat'] if 'vat' in data else float(0),
                model_type=data['model_type'], 
                model_id=not_exisit_in_request(data, 'model_id'),
                model_action=data['model_action'],
                response_code=not_exisit_in_request(data, 'response_code'),
                response_decision=not_exisit_in_request(data, 'response_decision'),
                card_number=not_exisit_in_request(data, 'card_number'),
                card_name=not_exisit_in_request(data, 'card_name'),
                card_expiry_date=not_exisit_in_request(data, 'card_expiry_date'),
                note=not_exisit_in_request(data, 'note'),
                dump_response=not_exisit_in_request(data, 'dump_response'),
                base_url=not_exisit_in_request(data, 'base_url'),
                custom_properties=not_exisit_in_request(data, 'custom_properties'),
                create_date=datetime.now(timezone.utc),
                last_modified=datetime.now(timezone.utc),
                config_id=not_exisit_in_request(data, 'config_id'),
                is_online=str_to_bool(data, 'is_online', True),
                payment_gateway=not_exisit_in_request(data, 'payment_gateway'),
                payment_type=not_exisit_in_request(data, 'payment_type'),
            )
            session.add(pt)
            session.commit()
            return 'PaymentTransaction Created', 201, pt.id

    @handle_errors("PaymentTransaction")
    def delete_payment_transaction(self, id):
        with session_scope() as session:
            pt = session.query(PaymentTransaction).filter_by(id=id).first()
            if pt is None:
                raise ResourceNotFoundError("PaymentTransaction")
            session.delete(pt)
            session.commit()
            return 'PaymentTransaction deleted', 200

    @handle_errors("PaymentTransaction")
    def get_model_payment_transactions(self, model_type, model_id, filter):
        with session_scope() as session:
            query = session.query(PaymentTransaction)
            query = filter_and_sort_query(filter.filters, filter.sorters, query, PaymentTransaction)

            if model_id is None:
                query = query.filter_by(model_type=model_type)
            else:
                query = query.filter_by(model_type=model_type, model_id=model_id)
            
            query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
            payment_transactions = query.all()
            result = {'payments': self.get_payment_transactions_model(payment_transactions), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            return result

    def get_payment_transaction_by_reference_id(self, reference_id):
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                with session_scope() as session:
                    payment_transactions = session.query(PaymentTransaction).filter_by(reference_id=reference_id).first()
                    if payment_transactions is None:
                        raise ResourceNotFoundError("PaymentTransaction")
                    return self.get_payment_transactions_model(payment_transactions), 200
            except Exception as e:
                current_app.logger.error(e)
                if attempt < max_attempts - 1:
                    continue
                else:
                    return debug_return('{}'.format(e)), 500
    
    @handle_errors("PaymentTransaction")
    def get_payment_transaction_by_id(self, id):
        with session_scope() as session:
            payment_transactions = session.query(PaymentTransaction).filter_by(id=id).first()
            if payment_transactions is None:
                raise ResourceNotFoundError("PaymentTransaction")
            return self.get_payment_transactions_model(payment_transactions), 200

    @handle_errors("PaymentTransaction")
    def get_payment_transaction_by_gateway_transaction_id(self, gateway_transaction_id):
        with session_scope() as session:
            payment_transactions = session.query(PaymentTransaction).filter_by(gateway_transaction_id=gateway_transaction_id).all()
            return self.get_payment_transactions_model(payment_transactions)

    @handle_errors("PaymentTransaction")
    def update_payment_transaction(self, id, data):
        with session_scope() as session:
            pt = session.query(PaymentTransaction).filter_by(id=id).first()
            if pt is None:
                raise ResourceNotFoundError("PaymentTransaction")
            pt.active = not_exisit_in_request(data, 'active', True)
            pt.requester = not_exisit_in_request(data, 'requester', pt.requester)
            pt.reference_id = not_exisit_in_request(data, 'reference_id', pt.reference_id)
            pt.gateway_transaction_id = not_exisit_in_request(data, 'gateway_transaction_id', pt.gateway_transaction_id)
            pt.payment_status = not_exisit_in_request(data, 'payment_status', pt.payment_status)
            pt.gateway_status = not_exisit_in_request(data, 'gateway_status', pt.gateway_status)
            pt.amount = not_exisit_in_request(data, 'amount', pt.amount)
            pt.vat = not_exisit_in_request(data, 'vat', pt.vat)
            pt.model_type = not_exisit_in_request(data, 'model_type', pt.model_type)
            pt.model_id = not_exisit_in_request(data, 'model_id', pt.model_id)
            pt.model_action = not_exisit_in_request(data, 'model_action', pt.model_action)
            pt.response_code = not_exisit_in_request(data, 'response_code', pt.response_code)
            pt.response_decision = not_exisit_in_request(data, 'response_decision', pt.response_decision)
            pt.card_number = not_exisit_in_request(data, 'card_number', pt.card_number)
            pt.card_name = not_exisit_in_request(data, 'card_name', pt.card_name)
            pt.card_expiry_date = not_exisit_in_request(data, 'card_expiry_date', pt.card_expiry_date)
            pt.note = not_exisit_in_request(data, 'note', pt.note)
            if is_exisit_in_request(data, 'retry'):
                pt.retry = data['retry']
            pt.dump_response = not_exisit_in_request(data, 'dump_response', pt.dump_response)
            pt.base_url = not_exisit_in_request(data, 'base_url')
            pt.is_online = str_to_bool(data, 'is_online', pt.is_online)
            pt.custom_properties = not_exisit_in_request(data, 'custom_properties', pt.custom_properties)
            pt.last_modified = datetime.now(timezone.utc)
            session.commit()
            return 'PaymentTransaction updated', 200

    @handle_errors("PaymentTransaction")
    def update_payment_thawani(self, id, data):
        with session_scope() as session:
            pt = session.query(PaymentTransaction).filter_by(id=id).first()
            if pt is None:
                raise ResourceNotFoundError("PaymentTransaction")
            pt.payment_status = not_exisit_in_request(data, 'payment_status', pt.payment_status)
            pt.gateway_status = not_exisit_in_request(data, 'gateway_status', pt.gateway_status)
            pt.last_modified = datetime.now(timezone.utc)
            session.commit()
            return pt.model_type, pt.model_id
        
    @handle_errors("PaymentTransaction")
    def update_payment_ompay(self, id, data):
        with session_scope() as session:
            pt = session.query(PaymentTransaction).filter_by(id=id).first()
            if pt is None:
                raise ResourceNotFoundError("PaymentTransaction")
            pt.payment_status = not_exisit_in_request(data, 'payment_status', pt.payment_status)
            pt.gateway_status = not_exisit_in_request(data, 'gateway_status', pt.gateway_status)
            pt.last_modified = datetime.now(timezone.utc)
            session.commit()
            return pt.model_type, pt.model_id

    @handle_errors("PaymentTransaction")
    def check_payment_transaction_by_reference_id(self, reference_id):
        with session_scope() as session:
            payment_transactions = session.query(PaymentTransaction).filter_by(reference_id=reference_id).first()
            if payment_transactions is None:
                raise ResourceNotFoundError("PaymentTransaction")
            #if payment_transactions.payment_gateway.lower() == 'Smartpay'.lower():
            #    from app.smartpay.service import SmartPayService
            #    smartpay_service = SmartPayService()
            #    msg, status = smartpay_service.payment_request_order_status(reference_id)
            #    return msg, status
            else:
                raise ResourceNotFoundError("PaymentTransaction")

    @handle_errors("PaymentTransaction")
    def check_all_pending_payment_transaction(self):
        with session_scope() as session:
            query = session.query(PaymentTransaction)
            query = query.filter(sql.func.lower(PaymentTransaction.payment_status) == 'pending'.lower())
            query = query.filter(sql.func.lower(PaymentTransaction.payment_type) == 'Online'.lower())
            query = query.filter(PaymentTransaction.active == True)
            query = query.filter(PaymentTransaction.retry <= 3)
            query = query.filter(PaymentTransaction.create_date <= datetime.now(timezone.utc) - timedelta(minutes=5))
            payment_transactions = query.all()
            if payment_transactions is None:
                raise ResourceNotFoundError("PaymentTransaction")
            for payment_transaction in payment_transactions:
                self.check_payment_transaction_by_reference_id(payment_transaction.reference_id)
            return 'PaymentTransaction Done', 200
        
    @handle_errors("PaymentTransaction")
    def refund_payment_transaction(self, id, amount=0):
        with session_scope() as session:
            pt = session.query(PaymentTransaction).filter_by(id=id).first()
            if pt is None:
                return 'Not Found', 404, None
            #if pt.payment_gateway.lower() == 'Smartpay'.lower():
            #    from app.smartpay.service import SmartPayService
            #    msg, status, pt_id = SmartPayService().payment_request_order_refund(pt.id, amount)
            #    return msg, status, pt_id
            else:
                return 'Not Found', 404, None
            
    @handle_errors("PaymentTransaction")
    def has_panding_payment(self, model_type, model_id, model_action, is_online=False):
        with session_scope() as session:
            query = session.query(PaymentTransaction)
            query = query.filter(sql.func.lower(PaymentTransaction.model_type) == model_type.lower())
            query = query.filter(sql.func.lower(PaymentTransaction.model_id) == model_id.lower())
            query = query.filter(sql.func.lower(PaymentTransaction.model_action) == model_action.lower())
            query = query.filter(sql.func.lower(PaymentTransaction.payment_status) == 'pending'.lower())
            query = query.filter(PaymentTransaction.active == True)
            query = query.filter(PaymentTransaction.is_online == is_online)
            payment_transactions = query.all()
            if payment_transactions:
                return True
            return False


    def get_payment_config_model(self, payment_configs):
        if isinstance(payment_configs, list):
            return [payment_config.json() for payment_config in payment_configs]
        return payment_configs.json()

    @handle_errors("PaymentConfig")
    def create_payment_config(self, data):
        payment_config = PaymentConfig(
            name = not_exisit_in_request(data,'name'),
            payment_gateway = data['payment_gateway'],
            fee = data['fee'],
            fee_cap = data['fee_cap'],
            limit = data['limit'],
            is_default = data['is_default'],
            url = not_exisit_in_request(data,'url'),
            access_key = not_exisit_in_request(data,'access_key'),
            secret_key = not_exisit_in_request(data,'secret_key'),
            merchant_key1 = not_exisit_in_request(data,'merchant_key1'),
            merchant_key2 = not_exisit_in_request(data,'merchant_key2'),
            merchant_key3 = not_exisit_in_request(data,'merchant_key3'),
            merchant_key4 = not_exisit_in_request(data,'merchant_key4'),
            merchant_key5 = not_exisit_in_request(data,'merchant_key5'),
            create_date=datetime.now(timezone.utc),
            modified_date=datetime.now(timezone.utc)
        )
        self.session.add(payment_config)
        self.session.commit()

        return 'PaymentConfig Created', 201

    @handle_errors("PaymentConfig")
    def get_payment_config(self, id, filter):
        query = self.session.query(PaymentConfig)
        
        if id is None:
            query = filter_and_sort_query(filter.filters, filter.sorters, query, PaymentConfig)

            query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
            payment_config = query.all()
            result = {'payment_config':self.get_payment_config_model(payment_config), 'filters':filters_serialization.get_pagination_serialization(pagination,filter.sort,filter.sort_order,filter.queries) }
        else:
            payment_config = query.filter_by(id=id).all()
            result = {'payment_config':self.get_payment_config_model(payment_config) }
        return result

    @handle_errors("PaymentConfig")
    def get_payment_config_by_id(self,id):
        payment_config = self.session.query(PaymentConfig).filter_by(id=id).first()
        if payment_config is None:
            raise ResourceNotFoundError("PaymentConfig")
        return self.get_payment_config_model(payment_config), 200

    @handle_errors("PaymentConfig")
    def get_payment_config_by_name(self,name):
        payment_config = self.session.query(PaymentConfig).filter(PaymentConfig.name==name).first()
        if payment_config is None:
            raise ResourceNotFoundError("PaymentConfig")
        return self.get_payment_config_model(payment_config), 200

    @handle_errors("PaymentConfig")
    def get_payment_config_default(self):
        payment_configs = self.session.query(PaymentConfig).filter(PaymentConfig.is_default==True).all()
        if payment_configs is None:
            raise ResourceNotFoundError("PaymentConfig")
        return self.get_payment_config_model(payment_configs), 200

    @handle_errors("PaymentConfig")
    def get_payment_config_by_ids(self, ids, with_default=False):
        query = self.session.query(PaymentConfig)
        
        if with_default:
            query = query.filter(sql.or_(PaymentConfig.id.in_(ids), PaymentConfig.is_default==True))
        else:
            query = query.filter(PaymentConfig.id.in_(ids))

        payment_configs = query.all()
        if payment_configs is None:
            raise ResourceNotFoundError("PaymentConfig")
        return self.get_payment_config_model(payment_configs), 200

    @handle_errors("PaymentConfig")
    def update_payment_config(self, id, data):
        payment_config = self.session.query(PaymentConfig).filter_by(id=id).first()
        if payment_config == None:
            raise ResourceNotFoundError("PaymentConfig")
        payment_config.name = not_exisit_in_request(data,'name')
        payment_config.payment_gateway = data['payment_gateway']
        payment_config.fee = data['fee']
        payment_config.fee_cap = data['fee_cap']
        payment_config.limit = data['limit']
        payment_config.is_default = data['is_default']
        payment_config.url = data['url']
        payment_config.access_key = not_exisit_in_request(data,'access_key')
        payment_config.secret_key = not_exisit_in_request(data,'secret_key')
        payment_config.merchant_key1 = not_exisit_in_request(data,'merchant_key1')
        payment_config.merchant_key2 = not_exisit_in_request(data,'merchant_key2')
        payment_config.merchant_key3 = not_exisit_in_request(data,'merchant_key3')
        payment_config.merchant_key4 = not_exisit_in_request(data,'merchant_key4')
        payment_config.merchant_key5 = not_exisit_in_request(data,'merchant_key5')
        payment_config.modified_date=datetime.now(timezone.utc)
        self.session.commit()

        return 'PaymentConfig updated', 200

    @handle_errors("PaymentConfig")
    def delete_payment_config(self, id):
        payment_config = self.session.query(PaymentConfig).filter_by(id=id).first()
        if payment_config == None:
            raise ResourceNotFoundError("PaymentConfig")
        
        self.session.delete(payment_config)
        self.session.commit()

        return 'PaymentConfig deleted', 200

    @handle_errors("PaymentTransaction")
    def get_offline_panding_payment_transactions(self, data):
        query = self.session.query(PaymentTransaction)
        query = query.filter(PaymentTransaction.payment_status==PaymentStatusEnum.pending)
        query = query.filter(PaymentTransaction.is_online==False)
        query = query.filter(PaymentTransaction.model_type==data['model_type'])
        query = query.filter(PaymentTransaction.model_id==data['model_id'])
        if 'model_action' in data:
            query = query.filter(PaymentTransaction.model_action==data['model_action'])
        if 'payment_type' in data:
            query = query.filter(PaymentTransaction.payment_type==data['payment_type'])

        query = query.order_by(PaymentTransaction.create_date.desc())
        payment_transactions = query.all()
        if payment_transactions == None:
            raise ResourceNotFoundError("PaymentTransaction")
        result = self.get_payment_transactions_model(payment_transactions)
        return result, 200


    def get_payment_type_model(self, payment_types):
        if isinstance(payment_types, list):
            return [payment_type.json() for payment_type in payment_types]
        return payment_types.json()
    
    @handle_errors("PaymentType")
    def get_payment_type(self):
        payment_types = self.session.query(PaymentType).all()
        if payment_types == None:
            raise ResourceNotFoundError("PaymentType")
        return self.get_payment_type_model(payment_types), 200
            
    @handle_errors("PaymentType")
    def get_payment_transactions_statistics(self):
        query = self.session.query(PaymentTransaction.payment_status, sql.func.count(PaymentTransaction.id))
        query = query.group_by(PaymentTransaction.payment_status)
        payment_transactions = query.all()
        if payment_transactions == None:
            raise ResourceNotFoundError("PaymentTransaction")
        result = {}
        for payment_transaction in payment_transactions:
            result.update({payment_transaction.payment_status : payment_transaction.count})
        return result, 200
