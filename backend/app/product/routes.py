import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters
from app.decorators.validation import validate_json, validate_form_data
from app.utils.response import APIResponse
from .schemas import ProductCreateSchema, ProductUpdateSchema, PrintMaterialSchema, PrintSettingsSchema, ProductPackagingSchema, ProductShippingCitySchema

from .service import ProductService

__uri__ = 'products'
__blueprint__ = 'products'

products = Blueprint(__uri__, __name__)

service = ProductService()

@products.route('/', methods=['GET'])
@cross_origin()
@permissions.has_permission(['product.show'])
@roles.token_required
@filters.filters
def get_all_products(filter, self):
    products, status = service.get_products(None,filter)
    if status == 200:
        return APIResponse.success(products, "Products retrieved successfully")
    else:
        return APIResponse.error("Failed to retrieve products", status_code=status)

@products.route('/<id>', methods=['GET'])
@cross_origin()
@permissions.has_permission(['product.show'])
@roles.token_required
@filters.filters
def get_product(filter,self, id):
    products, status = service.get_products(id, filter)
    if status == 200:
        return APIResponse.success(products, "Product retrieved successfully")
    else:
        return APIResponse.error("Failed to retrieve product", status_code=status)

@products.route('/', methods=['POST'])
@cross_origin()
@permissions.has_permission(['product.add'])
@roles.token_required
@validate_form_data(ProductCreateSchema)
def add_product(self, validated_data):
    message, status = service.create_product(validated_data, request.files)
    if status == 200:
        return APIResponse.success(message=message)
    else:
        return APIResponse.error(message, status_code=status)

@products.route('/<id>', methods=['PATCH'])
@cross_origin()
@permissions.has_permission(['product.edit'])
@roles.token_required
@validate_form_data(ProductUpdateSchema)
def update_product(self, validated_data, id):
    message, status = service.update_product(id, validated_data, request.files)
    if status == 200:
        return APIResponse.success(message=message)
    else:
        return APIResponse.error(message, status_code=status)


@products.route('/<id>', methods=['DELETE'])
@cross_origin()
@permissions.has_permission(['product.delete'])
@roles.token_required
def delete_product(self, id):
    message, status = service.delete_product(id)
    if status == 200:
        return APIResponse.success(message=message)
    else:
        return APIResponse.error(message, status_code=status)

@products.route('/<id>/reindex', methods=['GET'])
@permissions.has_permission(['product.show.all','product.show.own'])
@roles.token_required
def reindex_product(self,id):
    response, status = service.reindex_product_images_and_attachments(id)
    if status == 200:
        return APIResponse.success(response, "Product reindexed successfully")
    else:
        return APIResponse.error("Failed to reindex product", status_code=status)

@products.route('/upload/<type>/<id>/<int:order>',defaults={'new':None}, methods=['POST'])
@products.route('/upload/<type>/<id>/<int:order>/<new>', methods=['POST'])
@permissions.has_permission(['product.add.all','product.add.own'])
@roles.token_required
def product_upload_file(self,type,id,order,new=None):
    if not request.files:
        return APIResponse.error("No files provided", status_code=400)
    is_new = new is not None

    if type == 'image':
        message,files, status = service.upload_products_files(id,request.files.getlist('file'),[],order,is_new)
    elif type == 'attachment':
        message,files, status = service.upload_products_files(id,[],request.files.getlist('file'),order,is_new)
    else:
        return APIResponse.error("File type not allowed", status_code=403)
    
    if status == 200:
        return APIResponse.success({'files': files}, message)
    else:
        return APIResponse.error(message, status_code=status)

@products.route('/upload/<id>', methods=['DELETE'])
@permissions.has_permission(['product.add.all','product.add.own'])
@roles.token_required
def product_delete_upload_file(self,id):
    message, status = service.delete_products_file(id)
    if status == 200:
        return APIResponse.success(message=message)
    else:
        return APIResponse.error(message, status_code=status)

@products.route('/<product_id>/shipping-cities', methods=['GET'])
@roles.token_required
def get_product_shipping_cities(self, product_id):
    """Get shipping cities for a product"""
    cities, status = service.get_products_shipping_cities(product_id)
    return jsonify({'shipping_cities': cities}), status

@products.route('/<product_id>/shipping-cities', methods=['POST'])
@roles.token_required
def update_product_shipping_cities(self, product_id):
    """Update shipping cities for a product"""
    if not request.json or 'city_ids' not in request.json:
        return jsonify({'error': 'city_ids required'}), 400
    
    message, status = service.update_product_shipping_cities(product_id, request.json['city_ids'])
    return jsonify({'msg': message}), status

@products.route('/<product_id>/shipping-availability/<city_name>', methods=['GET'])
def check_shipping_availability(product_id, city_name):
    """Check if product can be shipped to a city"""
    available, status = service.check_product_shipping_availability(product_id, city_name)
    return jsonify({'available': available}), status

# 3D Printing Routes
@products.route('/print/materials', methods=['GET'])
def get_print_materials():
    """Get all available print materials"""
    try:
        from .model import PrintMaterial
        from app.utilities.db_utils import get_session_with_retries
        
        with get_session_with_retries() as session:
            materials = session.query(PrintMaterial).filter(PrintMaterial.is_active == True).all()
            return jsonify({
                'status': 200,
                'message': 'Success',
                'data': [material.json() for material in materials]
            })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error retrieving print materials: {str(e)}',
            'data': []
        }), 500

@products.route('/print/settings', methods=['GET'])
def get_print_settings():
    """Get all available print settings"""
    try:
        from .model import PrintSettings
        from app.utilities.db_utils import get_session_with_retries
        
        with get_session_with_retries() as session:
            settings = session.query(PrintSettings).filter(PrintSettings.is_active == True).all()
            return jsonify({
                'status': 200,
                'message': 'Success',
                'data': [setting.json() for setting in settings]
            })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error retrieving print settings: {str(e)}',
            'data': []
        }), 500

@products.route('/print/packaging', methods=['GET'])
def get_packaging_options():
    """Get all available packaging options"""
    try:
        from .model import ProductPackaging
        from app.utilities.db_utils import get_session_with_retries
        
        with get_session_with_retries() as session:
            packaging = session.query(ProductPackaging).filter(ProductPackaging.is_active == True).all()
            return jsonify({
                'status': 200,
                'message': 'Success',
                'data': [pkg.json() for pkg in packaging]
            })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error retrieving packaging options: {str(e)}',
            'data': []
        }), 500

@products.route('/print/materials', methods=['POST'])
def create_print_material():
    """Create a new print material"""
    try:
        from .model import PrintMaterial
        from app.utilities.db_utils import get_session_with_retries
        
        data = request.get_json()
        if not data or not all(k in data for k in ['name', 'type', 'cost_per_gram', 'density']):
            return jsonify({
                'status': 400,
                'message': 'Missing required fields: name, type, cost_per_gram, density',
                'data': None
            }), 400
        
        with get_session_with_retries() as session:
            material = PrintMaterial(
                name=data['name'],
                type=data['type'],
                color=data.get('color'),
                cost_per_gram=data['cost_per_gram'],
                density=data['density'],
                print_temperature=data.get('print_temperature'),
                bed_temperature=data.get('bed_temperature')
            )
            session.add(material)
            session.commit()
            return jsonify({
                'status': 201,
                'message': 'Print material created successfully',
                'data': material.json()
            }), 201
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error creating print material: {str(e)}',
            'data': None
        }), 500

@products.route('/print/settings', methods=['POST'])
def create_print_setting():
    """Create a new print setting"""
    try:
        from .model import PrintSettings
        from app.utilities.db_utils import get_session_with_retries
        
        data = request.get_json()
        if not data or not all(k in data for k in ['name', 'quality', 'layer_height', 'infill_percentage', 'print_speed']):
            return jsonify({
                'status': 400,
                'message': 'Missing required fields: name, quality, layer_height, infill_percentage, print_speed',
                'data': None
            }), 400
        
        with get_session_with_retries() as session:
            setting = PrintSettings(
                name=data['name'],
                quality=data['quality'],
                layer_height=data['layer_height'],
                infill_percentage=data['infill_percentage'],
                print_speed=data['print_speed'],
                support_enabled=data.get('support_enabled', False),
                raft_enabled=data.get('raft_enabled', False),
                brim_enabled=data.get('brim_enabled', False),
                estimated_time_multiplier=data.get('estimated_time_multiplier', 1.0)
            )
            session.add(setting)
            session.commit()
            return jsonify({
                'status': 201,
                'message': 'Print setting created successfully',
                'data': setting.json()
            }), 201
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error creating print setting: {str(e)}',
            'data': None
        }), 500

@products.route('/print/packaging', methods=['POST'])
def create_packaging_option():
    """Create a new packaging option"""
    try:
        from .model import ProductPackaging
        from app.utilities.db_utils import get_session_with_retries
        
        data = request.get_json()
        if not data or not all(k in data for k in ['name', 'type', 'cost']):
            return jsonify({
                'status': 400,
                'message': 'Missing required fields: name, type, cost',
                'data': None
            }), 400
        
        with get_session_with_retries() as session:
            packaging = ProductPackaging(
                name=data['name'],
                type=data['type'],
                cost=data['cost'],
                description=data.get('description')
            )
            session.add(packaging)
            session.commit()
            return jsonify({
                'status': 201,
                'message': 'Packaging option created successfully',
                'data': packaging.json()
            }), 201
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error creating packaging option: {str(e)}',
            'data': None
        }), 500

@products.route('/print/health', methods=['GET'])
def print_health_check():
    """Health check endpoint for 3D printing service"""
    from datetime import datetime, timezone
    return jsonify({
        'status': 200,
        'message': '3D Printing service is running',
        'data': {
            'service': '3D Store Print Service',
            'version': '1.0.0',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    })