import sqlalchemy as sql
import enum
from sqlalchemy_utils import UUIDType
import uuid
from sqlalchemy.orm import relationship
from app.common.enum import PaymentStatusEnum

from database import Base
from enum import Enum
from datetime import datetime, timezone



# Define the PaymentGateway data-model exp: Smartpay, Thawani, etc.
class PaymentGateway(Base):
    __tablename__ = 'payment_gateway'
    name = sql.Column(sql.String(50), primary_key=True)
    payment_transactions = relationship('PaymentTransaction')

    def json(self):
        data = {}
        data['name'] = self.name
        return data

# Define the PaymentType data-model exp: Online, Cash, Card, etc.
class PaymentType(Base):
    __tablename__ = 'payment_type'
    name = sql.Column(sql.String(50), primary_key=True)
    payment_transactions = relationship('PaymentTransaction')

    def json(self):
        data = {}
        data['name'] = self.name
        return data

class PaymentConfig(Base):
    __tablename__ = 'payment_config'
    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = sql.Column(sql.String(255), nullable=False,index=True, unique=True)
    payment_gateway = sql.Column(sql.String(length=255), sql.ForeignKey('payment_gateway.name', name='fk_payment_config_payment_gateway'), nullable=False)
    fee = sql.Column(sql.Numeric(precision=10, scale=3, asdecimal=False), default=0.000)
    fee_cap = sql.Column(sql.Numeric(precision=10, scale=3, asdecimal=False), default=0.000)
    limit = sql.Column(sql.Numeric(precision=10, scale=3, asdecimal=False), default=0.000)
    is_default = sql.Column(sql.Boolean(), default=False)
    url = sql.Column(sql.String(length=255), default='')
    access_key = sql.Column(sql.String(length=255), default='')
    secret_key = sql.Column(sql.String(length=255), default='')
    merchant_key1 = sql.Column(sql.String(length=255), default='')
    merchant_key2 = sql.Column(sql.String(length=255), default='')
    merchant_key3 = sql.Column(sql.String(length=255), default='')
    merchant_key4 = sql.Column(sql.String(length=255), default='')
    merchant_key5 = sql.Column(sql.String(length=255), default='')

    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))

    def json(self):
        data = {}
        data['id'] = self.id
        data['name'] = self.name
        data['payment_gateway'] = self.payment_gateway
        #data['online_status'] = self.online_status.value if self.online_status else None
        data['fee'] = str(self.fee)
        data['fee_cap'] = str(self.fee_cap)
        data['limit'] = str(self.limit)
        data['is_default'] = self.is_default
        data['url'] = self.url
        data['access_key'] = self.access_key
        data['secret_key'] = self.secret_key
        data['merchant_key1'] = self.merchant_key1
        data['merchant_key2'] = self.merchant_key2
        data['merchant_key3'] = self.merchant_key3
        data['merchant_key4'] = self.merchant_key4
        data['merchant_key5'] = self.merchant_key5

        return data
    
    def for_short(self):
        data = {}
        data['id'] = self.id
        data['name'] = self.name
        data['payment_gateway'] = self.payment_gateway
		#data['online_status'] = self.online_status.value if self.online_status else None
        return data
class PaymentTransaction(Base):
    __tablename__ = 'payment_transaction'
 
    id = sql.Column(UUIDType(binary=False), primary_key=True)
    active = sql.Column('is_active', sql.Boolean(), nullable=False, server_default='1')
    requester = sql.Column(UUIDType(binary=False), index=True)
    reference_id = sql.Column(sql.String(length=255), nullable=False, index=True, unique=True)
    payment_status = sql.Column('payment_status', sql.Enum(PaymentStatusEnum), index=True)
    gateway_transaction_id = sql.Column(sql.String(length=255), nullable=True, index=True)
    gateway_status = sql.Column(sql.String(length=255))
    amount = sql.Column(sql.Float, index=True)
    vat = sql.Column(sql.Float) 

    model_type = sql.Column(sql.String(length=255), index=True)
    model_id = sql.Column(sql.String(length=255), index=True)
    model_action = sql.Column(sql.String(length=255))
    response_code = sql.Column(sql.String(length=255))
    response_decision = sql.Column(sql.String(length=255))
    card_number = sql.Column(sql.String(length=20))
    card_name = sql.Column(sql.String(length=20))
    card_expiry_date = sql.Column(sql.String(length=10))
    note = sql.Column(sql.String(length=255))

    base_url = sql.Column(sql.String(length=255))

    retry = sql.Column(sql.Integer, server_default='0', default=0)

    dump_response = sql.Column(sql.Text)
    custom_properties = sql.Column(sql.JSON)
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))
    last_modified = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))

    config_id = sql.Column(UUIDType(binary=False))

    is_online = sql.Column(sql.Boolean(), default=False, index=True)
    
    payment_gateway = sql.Column(sql.String(length=255), sql.ForeignKey('payment_gateway.name'))
    payment_type = sql.Column(sql.String(length=255), sql.ForeignKey('payment_type.name'))

    def json(self):
        data = {}
        data['id'] = self.id
        data['requester'] = self.requester
        data['reference_id'] = self.reference_id
        data['payment_status'] = self.payment_status
        data['gateway_transaction_id'] = self.gateway_transaction_id
        data['gateway_status'] = self.gateway_status
        data['amount'] = str(self.amount)
        data['vat'] = str(self.vat)
        data['model_type'] = self.model_type
        data['model_id'] = self.model_id
        data['model_action'] = self.model_action
        data['response_code'] = self.response_code
        data['response_decision'] = self.response_decision
        data['card_number'] = self.card_number
        data['card_name'] = self.card_name
        data['card_expiry_date'] = self.card_expiry_date
        data['note'] = self.note

        if isinstance(self.custom_properties, dict):
            data['custom_properties'] = self.custom_properties

        if isinstance(self.dump_response, dict):
            data['dump_response'] = self.dump_response

        if isinstance(self.create_date, datetime):
            data['create_date'] = str(self.create_date)

        if isinstance(self.last_modified, datetime):
            data['last_modified'] = str(self.last_modified)

        if isinstance(self.base_url, str):
            data['base_url'] = self.base_url

        if isinstance(self.retry, int):
            data['retry'] = str(self.retry)

        if isinstance(self.config_id, uuid.UUID):
            data['config_id'] = str(self.config_id)

        if isinstance(self.is_online, bool):
            data['is_online'] = str(self.is_online)

        if isinstance(self.payment_gateway, str):
            data['payment_gateway'] = self.payment_gateway

        if isinstance(self.payment_type, str):
            data['payment_type'] = self.payment_type



