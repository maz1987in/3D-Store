## service layer of the API
import json
import sqlalchemy as sql
from sqlalchemy.orm.attributes import flag_modified
from flask import current_app
from sqlalchemy_filters import apply_pagination, apply_sort
from app.common.error_handling import ResourceNotFoundError
from app.medias.service import MediaService
from app.utilities.common_utils import change_string_to_time, debug_return
from config import BaseConfig, Config
from .model import Product
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query
from app.utilities.request_utils import not_exisit_in_request
from datetime import datetime, timezone
import uuid
from app.utilities.db_utils import session_scope
from app.category.model import Category
from app.utilities.file_upload_utils import upload_files, reindex_media
from app.utilities.error_utils import handle_errors  # Import the decorator
from app.product.model import ProductShippingCity
from app.city.model import City
from .repository import ProductRepository

media_service = MediaService()

class ProductService:
    def __init__(self):
        self.product_repo = ProductRepository()
    def get_product_model(self, products):
        result = []
        if isinstance(products, list):
            for product in products:
                result.append(
                    {'product': product.Product.json(),
                     'category': product.Category.json()})
            return result
        else:
            return {'product': products.Product.json(), 'category': products.Category.json()}

    @handle_errors("Product")
    def get_products(self, id, filter): 
        if id is None:
            # Use repository for paginated list with filtering
            result = self.product_repo.get_products_with_category(filter)
            return {
                'products': self.get_product_model(result['products']),
                'filters': result['filters']
            }, 200
        else:
            # Use repository for single product with details
            product_details = self.product_repo.get_product_with_details(id)
            if product_details is None:
                raise ResourceNotFoundError("Product")
            return {'products': self.get_product_model(product_details)}, 200

    @handle_errors("Product")
    def create_product(self, data, files):
        with session_scope() as session:
            # Prepare product data
            product_data = {
                'price': not_exisit_in_request(data, 'price', 0),
                'code': not_exisit_in_request(data, 'code', ''),
                'images': [],
                'attachments': [],
                'category_id': not_exisit_in_request(data, 'category_id', None),
                'supplier_id': not_exisit_in_request(data, 'supplier_id', None),
                'unit': not_exisit_in_request(data, 'unit', 'PIECE'),
                'quantity': not_exisit_in_request(data, 'quantity', 0),
                'min_quantity': not_exisit_in_request(data, 'min_quantity', 0),
                'create_date': datetime.now(timezone.utc),
                'modified_date': datetime.now(timezone.utc)
            }
            
            # Use repository to create product
            product = self.product_repo.create(product_data, session=session)
            
            # Handle translations
            for local in Config.AVAILABLE_LOCALES.keys():
                if isinstance(data['title'], str):
                    product.translations[local].title = json.loads(data['title'])[local]
                    product.translations[local].description = json.loads(data['description'])[local]
                else:
                    product.translations[local].title = data['title'][local]
                    product.translations[local].description = data['description'][local]

            session.commit()

            self.upload_products_files(str(product_id), files.getlist('images') if 'images' in files else [], files.getlist('attachments') if 'attachments' in files else [])

            if 'media_id' in data:
                media_service.update_media_model_id(str(data['media_id']), str(product_id))
                self.reindex_product_images_and_attachments(product_id)

            return 'Product Created', 201

    @handle_errors("Product")
    def update_product(self, id, data, files):
        with session_scope() as session:
            product = session.query(Product).filter_by(id=id).first()
            if product is None:
                raise ResourceNotFoundError("Product")
            product.price = not_exisit_in_request(data, 'price', product.price)
            product.code = not_exisit_in_request(data, 'code', product.code)
            product.images = not_exisit_in_request(data, 'images', product.images)
            product.attachments = not_exisit_in_request(data, 'attachments', product.attachments)
            product.category_id = not_exisit_in_request(data, 'category_id', product.category_id)
            product.supplier_id = not_exisit_in_request(data, 'supplier_id', product.supplier_id)
            product.unit = not_exisit_in_request(data, 'unit', product.unit)
            product.quantity = not_exisit_in_request(data, 'quantity', product.quantity)
            product.min_quantity = not_exisit_in_request(data, 'min_quantity', product.min_quantity)
            for local in Config.AVAILABLE_LOCALES.keys():
                if isinstance(data['title'], str):
                    product.translations[local].title = json.loads(data['title'])[local]
                    product.translations[local].description = json.loads(data['description'])[local]
                else:
                    product.translations[local].title = data['title'][local]
                    product.translations[local].description = data['description'][local]

            product.modified_date = datetime.now(timezone.utc)
            session.commit()

            if files:
                self.upload_products_files(product.id, files.getlist('images') if 'images' in files else [], files.getlist('attachments') if 'attachments' in files else [])
            else:
                self.reindex_product_images_and_attachments(id)

            return 'Updated', 200

    @handle_errors("Product")
    def delete_product(self, id):
        with session_scope() as session:
            product = session.query(Product).filter_by(id=id).first()

            if product is None:
                raise ResourceNotFoundError("Product")

            session.delete(product)
            session.commit()

            return 'Product deleted', 200

    @handle_errors("Product")
    def upload_products_files(self, id, images, attachments, order=1, is_new=False):
        with session_scope() as session:
            message, processed_images, status = upload_files(
                session, Product, 'product', id, images, 'images', order, is_new
            )
            if status != 200:
                return message, processed_images, status

            message, processed_attachments, status = upload_files(
                session, Product, 'product', id, attachments, 'attachments', order, is_new
            )
            return message, processed_images + processed_attachments, status

    @handle_errors("Product")
    def reindex_product_images_and_attachments(self, product_id):
        with session_scope() as session:
            return reindex_media(session, Product, 'product', product_id)

    @handle_errors("Product")
    def update_product_shipping_cities(self, product_id, city_ids):
        """Update shipping cities for a product"""
        with session_scope() as session:
            product = session.query(Product).filter_by(id=product_id).first()
            if not product:
                raise ResourceNotFoundError("Product")

            # Remove existing shipping cities
            session.query(ProductShippingCity).filter_by(product_id=product_id).delete()
            
            # Add new shipping cities
            for city_id in city_ids:
                city = session.query(City).filter_by(id=city_id).first()
                if city:
                    shipping_city = ProductShippingCity(
                        product_id=product_id,
                        city_id=city_id
                    )
                    session.add(shipping_city)
            
            session.commit()
            return 'Product shipping cities updated', 200

    @handle_errors("Product")
    def check_product_shipping_availability(self, product_id, city_name):
        """Check if product can be shipped to a specific city"""
        with session_scope() as session:
            result = session.query(ProductShippingCity, City).join(
                City, ProductShippingCity.city_id == City.id
            ).filter(
                ProductShippingCity.product_id == product_id,
                ProductShippingCity.is_active == True,
                City.__name__.ilike(f'%{city_name}%')
            ).first()
            
            return result is not None, 200

    @handle_errors("Product")
    def get_products_shipping_cities(self, product_id):
        """Get shipping cities for a product"""
        with session_scope() as session:
            product = session.query(Product).filter_by(id=product_id).first()
            if not product:
                raise ResourceNotFoundError("Product")
            
            cities = [sc.json() for sc in product.shipping_cities if sc.is_active]
            return cities, 200
