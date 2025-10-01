import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g, url_for, current_app, redirect
import requests
from app.common.enum import PlatformEnum
from config import ThawaniConfig

from app.security import roles, permissions
from app.common import filters

from .service import ThawaniService

__uri__ = 'thawanis'
__blueprint__ = 'thawanis'

thawanis = Blueprint(__uri__, __name__)

service = ThawaniService()


@thawanis.route('/', methods=['POST'])
#@cross_origin()
#@permissions.has_permission(['thawani.show'])
#@roles.token_required
def create_payment():
    data = request.json
    response, status,client_url = service.create_session(data)
    #response['client_url'] = client_url
    return jsonify(response), status

@thawanis.route('/payment_success', methods=['POST', 'GET'])
def payment_success():
    current_app.logger.info("Payment success")

    service.payment_success(request.args)
    #return response, status
    url = 'http://localhost:4200/' if request.url_root == 'http://127.0.0.1:5000/' else ThawaniConfig.WEBSITE_URL
    return redirect('{}profile'.format(url))

@thawanis.route('/payment_cancel', methods=['POST', 'GET'])
def payment_cancel():
    current_app.logger.info("Payment Cancel")
    
    service.payment_cancel(request.args)
    #return response, status
    url = 'http://localhost:4200/' if request.url_root == 'http://127.0.0.1:5000/' else ThawaniConfig.WEBSITE_URL
    return redirect('{}profile'.format(url))

@thawanis.route('/payment_status/<session_id>', methods=['GET'])
def payment_status(session_id):
    response, status = service.payment_status(session_id)
    return response, status