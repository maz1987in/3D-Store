## service layer of the API
import json
import requests
from requests.auth import HTTPBasicAuth
import sqlalchemy as sql

from flask import current_app,jsonify, url_for
from sqlalchemy_filters import apply_pagination, apply_sort
from app.common.enum import PaymentStatusEnum
from app.utilities.common_utils import change_string_to_time, debug_return, format_mobile
from config import OMPayConfig
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query, filter_query, create_filters
from app.utilities.request_utils import not_exisit_in_request
from datetime import date, datetime
import uuid
from app.utilities.db_utils import get_session_with_retries
from app.payment_transaction.service import PaymentTransactionsService

class OMPayService:
    #def __init__(self):
    #    self.session = get_session_with_retries()

    def get_ompay_model(self, ompays):
        result = []
        #print(ompay.__dict__)
        for ompay in ompays:
            data = {}
            if hasattr(ompay, 'Thawani'):
                ompay = ompay.Thawani
            if hasattr(ompay, 'Item'):
                ompay = ompay.Item
            data = ompay.json()
            
            result.append(data)
        return result
    
    def create_session(self, data):
        payload = {
            "amount": data['amount'],
            "currency": "OMR",
            "uiMode": "checkout",
            #"receiptId": data['invoice_id'],
            "description": data['description'],
            "customerFields": {
                "email": data['email'],
                "phone": format_mobile(data['phone']),
                "name": data['name']
            },
            #"curn": data['invoice_id'],
            "redirectType": "redirect"
        }

        response = requests.post(f"{OMPayConfig.OMPAY_BASE_URL}/nac/api/v1/pg/orders/create-checkout", 
                                 json=payload, 
                                 headers=OMPayConfig.OMPAY_HEADERS, 
                                 auth=HTTPBasicAuth(OMPayConfig.OMPAY_CLIENT_ID, OMPayConfig.OMPAY_CLIENT_SECRET))

        if response.status_code == 200:
            #client_url = f"{OMPayConfig.OMPAY_CHECKOUT_URL}/nac/public/checkout.js"
            return response.json(), response.status_code
        else:
            return {"error": response.text}, response.status_code

    def receipt(self, payload: dict, verified: bool):
        """
        Persist payment status coming from webhook/redirect.
        payload keys: orderId, paymentId, status, receiptId, amount, signature, timestamp, paymentDetails{...}
        """
        order_id = payload.get('orderId')
        payment_id = payload.get('paymentId')
        status = (payload.get('status') or '').lower()

        current_app.logger.info(f'OMPay receipt: order={order_id} payment={payment_id} status={status} verified={verified}')
        
        if status == 'success':
            update = {
                'payment_status': PaymentStatusEnum.success.value,
                'gateway_status': 'success',
                'payment_id': payment_id,
                'signature_verified': verified,
                'gateway_payload': json.dumps(payload),
            }
        elif status == 'failure':
            update = {
                'payment_status': PaymentStatusEnum.fail.value,
                'gateway_status': 'failure',
                'payment_id': payment_id,
                'signature_verified': verified,
                'gateway_payload': json.dumps(payload),
            }
        else:
            # Handle unknown/invalid status
            update = {
                'payment_status': PaymentStatusEnum.pending.value,
                'gateway_status': status or 'unknown',
                'payment_id': payment_id,
                'signature_verified': verified,
                'gateway_payload': json.dumps(payload),
            }
        
        model, id = PaymentTransactionsService().update_payment_ompay(payload.get('ref'), update)

        # TODO: lookup your transaction/order by order_id, then update fields:
        # - payment_id
        # - status (e.g., "success"/"failure")
        # - verified_signature (bool)
        # - raw_payload (audit)
        #
        # Example (pseudo):
        # with session_scope() as session:
        #     tx = session.query(Transaction).filter_by(order_id=order_id).first()
        #     if not tx: return
        #     tx.payment_id = payment_id
        #     tx.gateway_status = status
        #     tx.signature_verified = verified
        #     tx.gateway_payload = payload
        #     session.commit()
        
        return {
            'message': 'Payment receipt processed',
            'order_id': order_id,
            'payment_id': payment_id,
            'status': status,
            'model_type': model,
            'model_id': str(id)
        }, 200

    def payment_status(self, session_id):
        response = requests.get(f"{OMPayConfig.OMPAY_BASE_URL}/nac/api/v1/pg/orders/check-status?orderId={session_id}", headers=OMPayConfig.OMPAY_HEADERS)
        if response.status_code == 200:
            return response.json(), response.status_code
        else:
            return {"error": response.text}, response.status_code