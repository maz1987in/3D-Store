## service layer of the API
import json
import sqlalchemy as sql

from flask import current_app,jsonify
from sqlalchemy_filters import apply_pagination, apply_sort
from app.common.error_handling import ResourceNotFoundError
from app.utilities.common_utils import change_string_to_time, debug_return
from config import BaseConfig, Config
from .model import Cart, Item
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query, filter_query, create_filters
from app.utilities.request_utils import not_exisit_in_request
from datetime import date, datetime, timezone
import uuid
from app.utilities.db_utils import get_session_with_retries, session_scope
from app.utilities.error_utils import handle_errors

class CartService:

    def get_cart_model(self, carts):
        if isinstance(carts, list):
            result = []
            for cart in carts:
                data = {}
                if hasattr(cart, 'Item') and hasattr(cart, 'Cart'):
                    data['Cart'] = cart.Cart.json()
                    data['Item'] = cart.Item.json()
                elif hasattr(cart, 'Cart'):
                    data = cart.Cart.json()
                elif hasattr(cart, 'Item'):
                    data = cart.Item.json()
                else:
                    data = cart.json()
                result.append(data)
            return result
        else:
            data = {}
            if hasattr(cart, 'Item') and hasattr(cart, 'Cart'):
                data['Cart'] = cart.Cart.json()
                data['Item'] = cart.Item.json()
            elif hasattr(cart, 'Cart'):
                data = cart.Cart.json()
            elif hasattr(cart, 'Item'):
                data = cart.Item.json()
            else:
                data = cart.json()
            return data

    @handle_errors("Cart")
    def get_carts(self, id, filter): 
        with session_scope() as session:
            query = session.query(Cart)
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Cart)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                carts = query.all()
                result = {
                    'carts': self.get_cart_model(carts),
                    'filters': filters_serialization.get_pagination_serialization(
                        pagination, filter.sort, filter.sort_order, filter.queries
                    )
                }
            else:
                carts = query.filter_by(id=id).all()
                result = {'carts': self.get_cart_model(carts)}

            return result, 200

    @handle_errors("Cart")
    def get_carts_my(self, id): 
        with session_scope() as session:
            query = session.query(Cart)
            carts = query.filter_by(user_id=id).all()
            result = {'carts': self.get_cart_model(carts)}
            return result, 200

    @handle_errors("Cart")
    def create_cart(self, data):
        with session_scope() as session:
            cart = Cart(
                id=uuid.uuid4(),
                user_id=not_exisit_in_request(data, 'user_id', None),
                total=not_exisit_in_request(data, 'total', None),
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc)
            )  # type: ignore

            session.add(cart)
            session.commit()
            return 'Cart Created', 201

    @handle_errors("Cart")
    def update_cart(self, id, data):
        with session_scope() as session:
            cart = session.query(Cart).filter_by(id=id).first()
            if cart is None:
                raise ResourceNotFoundError("Cart")
            cart.total = not_exisit_in_request(data, 'total', cart.total)
            cart.modified_date = datetime.now(timezone.utc)
            session.commit()
            return 'Updated', 200

    @handle_errors("Cart")
    def delete_cart(self, id):
        with session_scope() as session:
            cart = session.query(Cart).filter_by(id=id).first()
            if cart is None:
                raise ResourceNotFoundError("Cart")
            session.delete(cart)
            session.commit()
            return 'Cart deleted', 200

    @handle_errors("Item")
    def create_item(self, cart_id, data):
        with session_scope() as session:
            item = Item(
                id=uuid.uuid4(),
                price=not_exisit_in_request(data, 'price', 0),
                quantity=not_exisit_in_request(data, 'quantity', 1),
                service_id=not_exisit_in_request(data, 'service_id', None),
                service_type=not_exisit_in_request(data, 'service_type', None),
                cart_id=cart_id,
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc)
            )  # type: ignore

            for local in Config.AVAILABLE_LOCALES.keys():
                item.translations[local].title = data['title'][local]

            session.add(item)
            session.commit()
            return 'Item Created', 201

    @handle_errors("Item")
    def update_item(self, id, data):
        with session_scope() as session:
            item = session.query(Item).filter_by(id=id).first()
            if item is None:
                raise ResourceNotFoundError("Item")
            item.price = not_exisit_in_request(data, 'price', item.price)
            item.quantity = not_exisit_in_request(data, 'quantity', item.quantity)
            item.service_id = not_exisit_in_request(data, 'service_id', item.service_id)
            item.service_type = not_exisit_in_request(data, 'service_type', item.service_type)
            item.modified_date = datetime.now(timezone.utc)
            for local in Config.AVAILABLE_LOCALES.keys():
                item.translations[local].title = data['title'][local]

            session.commit()
            return 'Updated', 200

    @handle_errors("Item")
    def get_items(self, id, filter): 
        with session_scope() as session:
            query = session.query(Item)
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Item)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                items = query.all()
                result = {
                    'items': self.get_cart_model(items),
                    'filters': filters_serialization.get_pagination_serialization(
                        pagination, filter.sort, filter.sort_order, filter.queries
                    )
                }
            else:
                items = query.filter_by(id=id).all()
                result = {'items': self.get_cart_model(items)}

            return result, 200

    @handle_errors("Item")
    def get_cart_items(self, cart_id): 
        with session_scope() as session:
            query = session.query(Item)
            items = query.filter_by(cart_id=cart_id).all()
            result = {'items': self.get_cart_model(items)}
            return result, 200

    @handle_errors("Item")
    def delete_item(self, id):
        with session_scope() as session:
            item = session.query(Item).filter_by(id=id).first()
            if item is None:
                raise ResourceNotFoundError("Item")
            session.delete(item)
            session.commit()
            return 'Item deleted', 200