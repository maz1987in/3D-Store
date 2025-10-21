import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters

from .model import Seller, SellerCommission, SellerPayment, SellerPerformance, SellerDocument
from app.utilities.db_utils import get_session_with_retries
import uuid
from datetime import datetime, timezone

__uri__ = 'sellers'
__blueprint__ = 'sellers'

sellers = Blueprint(__uri__, __name__)

@sellers.route('/', methods=['GET'])
def get_sellers():
    """Get all sellers"""
    try:
        with get_session_with_retries() as session:
            sellers_list = session.query(Seller).all()
            return jsonify({
                'status': 200,
                'message': 'Success',
                'data': [seller.json() for seller in sellers_list]
            })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error retrieving sellers: {str(e)}',
            'data': []
        }), 500

@sellers.route('/<seller_id>', methods=['GET'])
def get_seller(seller_id):
    """Get a specific seller by ID"""
    try:
        with get_session_with_retries() as session:
            seller = session.query(Seller).filter(Seller.id == seller_id).first()
            if not seller:
                return jsonify({
                    'status': 404,
                    'message': 'Seller not found',
                    'data': None
                }), 404
            
            return jsonify({
                'status': 200,
                'message': 'Success',
                'data': seller.json()
            })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error retrieving seller: {str(e)}',
            'data': None
        }), 500

@sellers.route('/', methods=['POST'])
def create_seller():
    """Create a new seller"""
    try:
        data = request.get_json()
        
        with get_session_with_retries() as session:
            seller = Seller(
                id=uuid.uuid4(),
                user_id=data.get('user_id'),
                business_name=data.get('business_name'),
                business_type=data.get('business_type'),
                tax_id=data.get('tax_id'),
                business_license=data.get('business_license'),
                business_address=data.get('business_address'),
                business_phone=data.get('business_phone'),
                business_email=data.get('business_email'),
                bank_name=data.get('bank_name'),
                bank_account_number=data.get('bank_account_number'),
                bank_routing_number=data.get('bank_routing_number'),
                bank_swift_code=data.get('bank_swift_code'),
                commission_type=data.get('commission_type', 'percentage'),
                commission_rate=data.get('commission_rate', 5.0),
                minimum_payout=data.get('minimum_payout', 50.0),
                payment_frequency=data.get('payment_frequency', 'monthly'),
                contact_person=data.get('contact_person'),
                contact_phone=data.get('contact_phone'),
                contact_email=data.get('contact_email'),
                description=data.get('description'),
                website=data.get('website'),
                social_media=data.get('social_media')
            )
            
            session.add(seller)
            session.commit()
            
            return jsonify({
                'status': 201,
                'message': 'Seller created successfully',
                'data': seller.json()
            }), 201
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error creating seller: {str(e)}',
            'data': None
        }), 500

@sellers.route('/<seller_id>/commissions', methods=['GET'])
def get_seller_commissions(seller_id):
    """Get commissions for a specific seller"""
    try:
        with get_session_with_retries() as session:
            commissions = session.query(SellerCommission).filter(SellerCommission.seller_id == seller_id).all()
            return jsonify({
                'status': 200,
                'message': 'Success',
                'data': [commission.json() for commission in commissions]
            })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error retrieving commissions: {str(e)}',
            'data': []
        }), 500

@sellers.route('/<seller_id>/commissions', methods=['POST'])
def create_seller_commission(seller_id):
    """Create a new commission for a seller"""
    try:
        data = request.get_json()
        
        with get_session_with_retries() as session:
            commission = SellerCommission(
                id=uuid.uuid4(),
                seller_id=seller_id,
                commission_type=data.get('commission_type'),
                base_rate=data.get('base_rate'),
                tier_1_rate=data.get('tier_1_rate'),
                tier_1_threshold=data.get('tier_1_threshold'),
                tier_2_rate=data.get('tier_2_rate'),
                tier_2_threshold=data.get('tier_2_threshold'),
                tier_3_rate=data.get('tier_3_rate'),
                effective_from=data.get('effective_from'),
                effective_to=data.get('effective_to'),
                minimum_commission=data.get('minimum_commission'),
                maximum_commission=data.get('maximum_commission'),
                agreement_terms=data.get('agreement_terms')
            )
            
            session.add(commission)
            session.commit()
            
            return jsonify({
                'status': 201,
                'message': 'Commission created successfully',
                'data': commission.json()
            }), 201
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error creating commission: {str(e)}',
            'data': None
        }), 500

@sellers.route('/<seller_id>/payments', methods=['GET'])
def get_seller_payments(seller_id):
    """Get payments for a specific seller"""
    try:
        with get_session_with_retries() as session:
            payments = session.query(SellerPayment).filter(SellerPayment.seller_id == seller_id).all()
            return jsonify({
                'status': 200,
                'message': 'Success',
                'data': [payment.json() for payment in payments]
            })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error retrieving payments: {str(e)}',
            'data': []
        }), 500

@sellers.route('/<seller_id>/performance', methods=['GET'])
def get_seller_performance(seller_id):
    """Get performance data for a specific seller"""
    try:
        with get_session_with_retries() as session:
            performance = session.query(SellerPerformance).filter(SellerPerformance.seller_id == seller_id).all()
            return jsonify({
                'status': 200,
                'message': 'Success',
                'data': [perf.json() for perf in performance]
            })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error retrieving performance: {str(e)}',
            'data': []
        }), 500

@sellers.route('/<seller_id>/documents', methods=['GET'])
def get_seller_documents(seller_id):
    """Get documents for a specific seller"""
    try:
        with get_session_with_retries() as session:
            documents = session.query(SellerDocument).filter(SellerDocument.seller_id == seller_id).all()
            return jsonify({
                'status': 200,
                'message': 'Success',
                'data': [doc.json() for doc in documents]
            })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error retrieving documents: {str(e)}',
            'data': []
        }), 500

@sellers.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for seller service"""
    return jsonify({
        'status': 200,
        'message': 'Seller service is running',
        'data': {
            'service': '3D Store Seller Service',
            'version': '1.0.0',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    })





