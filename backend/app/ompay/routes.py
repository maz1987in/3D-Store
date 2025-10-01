import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g, url_for, current_app, redirect
import requests
from app.common.enum import PlatformEnum
from config import OMPayConfig
import hmac, hashlib  # <-- add

from app.security import roles, permissions
from app.common import filters

from .service import OMPayService

__uri__ = 'ompay'
__blueprint__ = 'ompay'

ompay = Blueprint(__uri__, __name__)

service = OMPayService()


@ompay.route('/', methods=['POST'])
def create_payment():
    data = request.json
    response, status = service.create_session(data)
    #response['client_url'] = client_url
    return jsonify(response), status

@ompay.route('/receipt', methods=['POST', 'GET'])
def receipt():
    # Gather payload from POST (JSON webhook) or GET (querystring redirect)
    payload = request.get_json(silent=True) if request.method == 'POST' else request.args.to_dict()
    if not payload:
        return jsonify({'msg': 'invalid payload'}), 400

    order_id = (payload.get('orderId') or '').strip()
    payment_id = (payload.get('paymentId') or '').strip()
    signature = (payload.get('signature') or '').strip()
    status = (payload.get('status') or '').strip()

    # Verify signature: HMAC-SHA256(secret, "orderId|paymentId")
    secret = getattr(OMPayConfig, 'OMPAY_CLIENT_SECRET', None)
    if not secret:
        current_app.logger.error('CLIENT_SECRET is not configured')
        return jsonify({'msg': 'server not configured'}), 500

    message = f'{order_id}|{payment_id}'
    generated_signature = hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    verified = hmac.compare_digest(generated_signature, signature)

    # Persist/handle status
    try:
        service.receipt(payload, verified)
    except Exception as e:
        current_app.logger.exception('Failed to handle receipt')
        if request.method == 'POST':
            return jsonify({'verified': verified, 'status': status, 'msg': 'failed to handle receipt'}), 500

    if request.method == 'POST':
        # Webhook acknowledgement
        return jsonify({'verified': verified, 'status': status}), 200

    # Browser redirect
    base_url = 'http://localhost:4200/' if request.url_root.startswith('http://127.0.0.1:5000/') else OMPayConfig.WEBSITE_URL
    # Redirect with query params so frontend can show result
    target = f"{base_url}profile?payment_status={status}&verified={'true' if verified else 'false'}&orderId={order_id}&paymentId={payment_id}"
    return redirect(target)

@ompay.route('/payment_status/<session_id>', methods=['GET'])
def payment_status(session_id):
    response, status = service.payment_status(session_id)
    return response, status