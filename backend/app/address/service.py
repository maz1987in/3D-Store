from datetime import datetime, timezone
from app.common.error_handling import ResourceNotFoundError
from app.utilities.error_utils import handle_errors
from sqlalchemy_filters import apply_pagination, apply_sort
from app.utilities.request_utils import not_exisit_in_request
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query, filter_query, create_filters
from .model import ShippingAddress
from app.utilities.db_utils import session_scope
import uuid
from app.product.service import ProductService

class ShippingAddressService:
    def get_address_model(self, addresses):
        if isinstance(addresses, list):
            return [address.json() for address in addresses]
        return addresses.json()


    @handle_errors("ShippingAddress")
    def add_address(self, user_id, data):
        with session_scope() as session:
            address = ShippingAddress(
                id=uuid.uuid4(),
                user_id=user_id,
                address_line1=not_exisit_in_request(data,'address_line1',None),
                address_line2=not_exisit_in_request(data,'address_line2',None),
                city=not_exisit_in_request(data,'city',None),
                state=not_exisit_in_request(data,'state',None),
                postal_code=not_exisit_in_request(data,'postal_code',None),
                country=not_exisit_in_request(data,'country','Oman'),
                phone=not_exisit_in_request(data,'phone',None),
                label=not_exisit_in_request(data,'label',None),
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc)
            )
            session.add(address)
            session.commit()
            return 'ShippingAddress Created', 201

    @handle_errors("ShippingAddress")
    def get_addresses(self, id, filter): 
        with session_scope() as session:
            query = session.query(ShippingAddress)
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, ShippingAddress)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                addresses = query.all()
                result = {
                    'addresses': self.get_address_model(addresses),
                    'filters': filters_serialization.get_pagination_serialization(
                        pagination, filter.sort, filter.sort_order, filter.queries
                    )
                }
            else:
                addresses = query.filter_by(id=id).first()
                if addresses is None:
                    raise ResourceNotFoundError("ShippingAddress")
                result = {'addresses': self.get_address_model(addresses)}

            return result, 200
    
    @handle_errors("ShippingAddress")
    def update_address(self, id, data):
        with session_scope() as session:
            address = session.query(ShippingAddress).filter_by(id=id).first()  
            if address is None:
                raise ResourceNotFoundError("ShippingAddress")
            address.address_line1 = not_exisit_in_request(data, 'address_line1', address.address_line1)
            address.address_line2 = not_exisit_in_request(data, 'address_line2', address.address_line2)
            address.city = not_exisit_in_request(data, 'city', address.city)
            address.state = not_exisit_in_request(data, 'state', address.state)
            address.postal_code = not_exisit_in_request(data, 'postal_code', address.postal_code)
            address.country = not_exisit_in_request(data, 'country', address.country)
            address.phone = not_exisit_in_request(data, 'phone', address.phone)
            address.label = not_exisit_in_request(data, 'label', address.label)
            address.modified_date = datetime.now(timezone.utc)
            
            session.commit()

            return 'Updated', 200

    @handle_errors("ShippingAddress")
    def delete_address(self, id):
        with session_scope() as session:
            address = session.query(ShippingAddress).filter_by(id=id).first()

            if address is None:
                raise ResourceNotFoundError("ShippingAddress")
            
            session.delete(address)
            session.commit()

            return 'ShippingAddress deleted', 200
        
    @handle_errors("ShippingAddress")
    def validate_shipping_address_for_products(self, address_id, product_ids):
        """Validate if shipping address city supports all products"""
        with session_scope() as session:
            address = session.query(ShippingAddress).filter_by(id=address_id).first()
            if not address:
                raise ResourceNotFoundError("ShippingAddress")
            
            product_service = ProductService()
            unavailable_products = []
            
            for product_id in product_ids:
                available, _ = product_service.check_product_shipping_availability(product_id, address.city)
                if not available:
                    unavailable_products.append(product_id)
            
            return {
                'valid': len(unavailable_products) == 0,
                'unavailable_products': unavailable_products,
                'city': address.city
            }, 200
