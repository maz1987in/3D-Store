## service layer of the API
import json
import requests
import sqlalchemy as sql

from flask import current_app,jsonify, url_for
from sqlalchemy_filters import apply_pagination, apply_sort
from app.common.enum import PaymentStatusEnum
from app.utilities.common_utils import change_string_to_time, debug_return
from config import BaseConfig, Config, ThawaniConfig
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query, filter_query, create_filters
from app.utilities.request_utils import not_exisit_in_request
from datetime import date, datetime
import uuid
from app.utilities.db_utils import get_session_with_retries
from app.payment_transaction.service import PaymentTransactionsService

class ThawaniService:
    #def __init__(self):
    #    self.session = get_session_with_retries()

    def get_thawani_model(self, thawanis):
        result = []
        #print(thawanis.__dict__)
        for thawani in thawanis:
            data = {}
            if hasattr(thawani, 'Thawani'):
                thawani = thawani.Thawani
            if hasattr(thawani, 'Item'):
                thawani = thawani.Item
            data = thawani.json()
            
            result.append(data)
        return result
    
    def create_session(self, data):
        payload = {
            "client_reference_id": data['client_reference_id'],
            "mode": data['mode'] if 'mode' in data else "payment",
            "products": data['products'],
            "success_url": url_for('thawanis.payment_success',ref=data['client_reference_id'], _external=True),
            "cancel_url": url_for('thawanis.payment_cancel', ref=data['client_reference_id'], _external=True),
            "metadata": data['metadata'] if 'metadata' in data else {},
        }

        response = requests.post(f"{ThawaniConfig.THAWANI_BASE_URL}/checkout/session", json=payload, headers=ThawaniConfig.THAWANI_HEADERS)
        if response.status_code == 200:
            client_url = f"{ThawaniConfig.THAWANI_CHECKOUT_URL}/pay/"+response.json()['data']['session_id'] + "?key=" + ThawaniConfig.THAWANI_PUBLISHABLE_KEY
            return response.json(), response.status_code, client_url
        else:
            return {"error": response.text}, response.status_code, None

    def payment_success(self, data):
        update = {
            'payment_status': PaymentStatusEnum.success.value,
            'gateway_status': 'success',
        }
        model, id = PaymentTransactionsService().update_payment_thawani(data.get('ref'), update)

        ## to do the logic here ....
        
        return "Payment successful!" , 200
    
    def payment_cancel(self, data):
        update = {
            'payment_status': PaymentStatusEnum.cancel.value,
            'gateway_status': 'cancel',
        }
        PaymentTransactionsService().update_payment_thawani(data.get('ref'), update)
        return "Payment canceled.", 200
    
    def payment_status(self, session_id):
        response = requests.get(f"{ThawaniConfig.THAWANI_BASE_URL}/checkout/session/{session_id}", headers=ThawaniConfig.THAWANI_HEADERS)
        if response.status_code == 200:
            return response.json(), response.status_code
        else:
            return {"error": response.text}, response.status_code