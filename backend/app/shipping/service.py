from app.common import filters_serialization
from app.common.enum import ShippingStatusEnum
from app.common.error_handling import ResourceNotFoundError
from sqlalchemy_filters import apply_pagination, apply_sort
from app.common.queries import create_sorters, filter_and_sort_query
from app.utilities.common_utils import get_random_digits_value
from app.utilities.db_utils import session_scope
from app.utilities.error_utils import handle_errors
from .model import Shipping
from app.order.model import Order

class ShippingService:

    def get_shipping_model(self, shipping_info):
        if not shipping_info:
            return None
        return shipping_info.json()

    @handle_errors("Shipping")
    def get_shipping(self,id, filter=None):
        with session_scope() as session:
            query = session.query(Shipping, Order).filter(Shipping.order_id == Order.id)
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, [Shipping, Order])
                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                orders = query.all()
                result = {
                    'shipping': self.get_shipping_model(orders),
                    'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)
                }
            else:
                shipping = query.filter(Shipping.id == id).first()
                if shipping is None:
                    raise ResourceNotFoundError("Shipping")
                result = {'shipping': self.get_shipping_model(shipping)}
            return result, 200
        
    @handle_errors("Shipping")
    def get_shipping_by_order_id(self, order_id):
        with session_scope() as session:
            shipping_info = session.query(Shipping).filter(Shipping.order_id == order_id).first()
            if not shipping_info:
                raise ResourceNotFoundError("Shipping information for order")
            return self.get_shipping_model(shipping_info), 200

    @handle_errors("Shipping")
    def create_or_update_shipping(self, order_id, data):
        with session_scope() as session:
            order = session.query(Order).filter(Order.id == order_id).first()
            if not order:
                raise ResourceNotFoundError("Order")

            shipping_info = session.query(Shipping).filter(Shipping.order_id == order_id).first()

            if shipping_info:
                # Update existing shipping info
                shipping_info.carrier = data.get('carrier', shipping_info.carrier)
                shipping_info.tracking_number = data.get('tracking_number', shipping_info.tracking_number)
                shipping_info.shipping_cost = data.get('shipping_cost', shipping_info.shipping_cost)
                shipping_info.shipping_date = data.get('shipping_date', shipping_info.shipping_date)
                shipping_info.status = data.get('status', shipping_info.status)
                message = 'Shipping Information Updated'
                status_code = 200
            else:
                # Create new shipping info
                shipping_info = Shipping(
                    order_id=order_id,
                    carrier=data.get('carrier'),
                    tracking_number=data.get('tracking_number', get_random_digits_value(10)),
                    shipping_cost=data.get('shipping_cost'),
                    shipping_date=data.get('shipping_date'),
                    status=data.get('status', ShippingStatusEnum.PENDING)
                )
                session.add(shipping_info)
                message = 'Shipping Information Created'
                status_code = 201
            
            session.commit()
            return message, status_code