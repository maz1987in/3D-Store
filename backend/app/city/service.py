## service layer of the API
import json
import sqlalchemy as sql
from flask import current_app
from sqlalchemy_filters import apply_pagination, apply_sort
from app.utilities.common_utils import debug_return
from app.utilities.db_utils import session_scope
from config import Config
from .model import City, CityTranslation
from app.common import filters_serialization
from app.common.queries import filter_and_sort_query
from app.utilities import request_utils
from datetime import datetime, timezone
import uuid
from app.common.error_handling import ResourceNotFoundError
from app.utilities.error_utils import handle_errors

class CityService:
    
    @handle_errors("City")
    def get_cities(self, city_id=None, filter_data=None):
        with session_scope() as session:
            query = session.query(City)
            
            result = None
            if city_id is None:
                query = filter_and_sort_query(filter.filters, filter.sorters, query, City)
                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                cities = query.all()
                result = {
                    'cities': [city.json() for city in cities],
                    'filters': filters_serialization.get_pagination_serialization(
                        pagination, filter.sort, filter.sort_order, filter.queries
                    )
                }
            else:
                cities = query.filter_by(id=id).first()
                result = {'cities': cities.json()}

            return result, 200

    @handle_errors("City")
    def create_city(self, data):
        with session_scope() as session:
            # Check if city code already exists
            existing_city = session.query(City).filter(City.code == data.get('code')).first()
            if existing_city:
                return 'City with this code already exists', 400
            
            city_id = uuid.uuid4()
            
            # Create city
            city = City(
                id=city_id,
                code=data.get('code'),
                country=data.get('country', 'Oman'),
                is_active=data.get('is_active', True),
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc)
            )
            
            for local in Config.AVAILABLE_LOCALES.keys():
                if isinstance(data['name'], str):
                    city.translations[local].name = json.loads(data['name'])[local]
                else:
                    city.translations[local].name = data['name'][local]
            session.add(city)
            session.commit()
            return 'City Created', 201
    
    @handle_errors("City")
    def update_city(self, city_id, data):
        with session_scope() as session:
            city = session.query(City).filter(City.id == city_id).first()
            if not city:
                raise ResourceNotFoundError("City")
            
            # Check if new code conflicts with existing city
            if 'code' in data and data['code'] != city.code:
                existing = session.query(City).filter(
                    City.code == data['code'],
                    City.id != city_id
                ).first()
                if existing:
                    return 'City with this code already exists', 400
            
            # Update city fields
            city.code = data.get('code', city.code)
            city.country = data.get('country', city.country)
            city.is_active = data.get('is_active', city.is_active)
            city.modified_date = datetime.now(timezone.utc)
            
            for local in Config.AVAILABLE_LOCALES.keys():
                if isinstance(data['name'], str):
                    city.translations[local].name = json.loads(data['name'])[local]
                else:
                    city.translations[local].name = data['name'][local]
                    
            
            session.commit()
            return 'City Updated', 200
    
    @handle_errors("City")
    def delete_city(self, city_id):
        with session_scope() as session:
            city = session.query(City).filter(City.id == city_id).first()
            if not city:
                raise ResourceNotFoundError("City")
            
            # Check if city is being used by products
            if city.product_shipping_cities:
                return 'Cannot delete city that is used by products', 400
            
            session.delete(city)
            session.commit()
            return 'City Deleted', 200
    
    @handle_errors("City")
    def get_active_cities(self):
        """Get only active cities for public use"""
        with session_scope() as session:
            cities = session.query(City).filter(City.is_active == True).all()
            cities_data = [city.json() for city in cities]
            return {'cities': cities_data}, 200