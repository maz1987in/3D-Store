## service layer of the API
import json
import sqlalchemy as sql

from flask import current_app, jsonify
from sqlalchemy_filters import apply_pagination, apply_sort
from app.branch.model import Branch
from app.common.error_handling import ResourceNotFoundError
from app.product.model import Product
from app.store.model import Store
from app.utilities.common_utils import change_string_to_time, debug_return
from config import Config
from .model import Inventory
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query
from app.utilities.request_utils import not_exisit_in_request
from datetime import datetime, timezone
import uuid
from app.utilities.db_utils import session_scope
from app.transaction.service import TransactionService
from app.utilities.error_utils import handle_errors  # Import the decorator
from collections import defaultdict
from app.category.model import Category

class InventoryService:
    def get_inventory_model(self, inventories):
        if isinstance(inventories, list):
            result = []
            for inventory in inventories:
                data = {}
                if hasattr(inventory, 'Inventory'):
                    data['inventory'] = inventory.Inventory.json()
                if hasattr(inventory, 'Store'):
                    data['store'] = inventory.Store.json() if inventory.Store else None
                if hasattr(inventory, 'Branch'):
                    data['branch'] = inventory.Branch.json() if inventory.Branch else None
                if hasattr(inventory, 'Product'):
                    data['product'] = inventory.Product.json() if inventory.Product else None
                if hasattr(inventory, 'Category'):
                    data['category'] = inventory.Category.json() if inventory.Category else None
                result.append(data)
            return result
        else:
            data = {}
            if hasattr(inventories, 'Inventory'):
                data['inventory'] = inventories.Inventory.json()
            if hasattr(inventories, 'Store'):
                data['store'] = inventories.Store.json() if inventories.Store else None
            if hasattr(inventories, 'Branch'):
                data['branch'] = inventories.Branch.json() if inventories.Branch else None
            if hasattr(inventories, 'Product'):
                data['product'] = inventories.Product.json() if inventories.Product else None
            if hasattr(inventories, 'Category'):
                data['category'] = inventories.Category.json() if inventories.Category else None
            return data
    
    def get_inventory_model_specific(self, inventories):
        data = {}
        data['inventory'] = inventories.json()
        
        return data

    def get_grouped_inventory_model(self, inventories):
        if not isinstance(inventories, list):
            inventories = [inventories]

        grouped = {}

        for inventory in inventories:
            # Support both tuple format and named attribute (hybrid model)
            inv = getattr(inventory, 'Inventory', inventory[0] if isinstance(inventory, tuple) else None)
            store = getattr(inventory, 'Store', inventory[1] if isinstance(inventory, tuple) else None)
            branch = getattr(inventory, 'Branch', inventory[2] if isinstance(inventory, tuple) else None)
            product = getattr(inventory, 'Product', inventory[3] if isinstance(inventory, tuple) else None)

            if not all([inv, product]):
                continue

            title = {
                "en": product.title.get("en", "Unknown") if isinstance(product.title, dict) else product.title,
                "ar": product.title.get("ar", "غير معروف") if isinstance(product.title, dict) else product.title
            }

            key = (product.code, title['en'])

            if key not in grouped:
                grouped[key] = {
                    "code": product.code,
                    "name": title,
                    "unit": product.unit.value,
                    "price": product.price,
                    "inventories": []
                }

            grouped[key]["inventories"].append({
                "quantity": inv.quantity,
                "quantity_alert": inv.quantity_alert,
                "store": store.json() if store else None,
                "branch": branch.json() if branch else None,
                "inventory_id": inv.id,
                "modified_date": inv.modified_date
            })

        return list(grouped.values())

    @handle_errors("Inventory")
    def get_inventories(self, id, filter): 
        with session_scope() as session:
            query = (
                session.query(Inventory, Store, Branch, Product)
                .outerjoin(Store, Inventory.store_id == Store.id)
                .outerjoin(Branch, Inventory.branch_id == Branch.id)
                .outerjoin(Product, Inventory.product_id == Product.id)
            )
            
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, [Inventory, Product])

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                inventories = query.all()
                result = {'inventories': self.get_inventory_model(inventories), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                inventories = query.filter_by(id=id).first()
                if inventories is None:
                    raise ResourceNotFoundError("Inventory")
                result = {'inventories': self.get_inventory_model(inventories)}

            return result, 200
    
    @handle_errors("Inventory")
    def get_inventories_status(self, id): 
        with session_scope() as session:
            query = session.query(Inventory)
            
            result = None
            
            inventories = query.filter(Inventory.product_id==id).first()
            if inventories is None:
                raise ResourceNotFoundError("Inventory")
            result = {'inventories': self.get_inventory_model_specific(inventories)}

            return result, 200
    
    @handle_errors("Inventory")
    def get_inventories_supplier(self, id, filter): 
        with session_scope() as session:
            query = (
                session.query(Inventory, Product, Category)
                .outerjoin(Product, Inventory.product_id == Product.id)
                .outerjoin(Category, Product.category_id == Category.id)
            )

            query = query.filter(Product.supplier_id==id)
            
            result = None

            if filter.sort is None:
                filter.sorters = create_sorters('modified_date', 'desc')
            query = filter_and_sort_query(filter.filters, filter.sorters, query, [Inventory, Product])

            query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
            
            inventories = query.all()

            result = {'inventories': self.get_inventory_model(inventories), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}

            return result, 200
    
    @handle_errors("Inventory")
    def get_inventories_products(self, id, filter): 
        with session_scope() as session:
            query = (
                session.query(Inventory, Product, Category)
                .outerjoin(Product, Inventory.product_id == Product.id)
                .outerjoin(Category, Product.category_id == Category.id)
            )
            
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, [Inventory, Product])

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                inventories = query.all()
                result = {'inventories': self.get_inventory_model(inventories), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                inventories = query.filter_by(id=id).first()
                if inventories is None:
                    raise ResourceNotFoundError("Inventory")
                result = {'inventories': self.get_inventory_model(inventories)}

            return result, 200
    
    @handle_errors("Inventory")
    def get_inventories_supplier(self, id, filter): 
        with session_scope() as session:
            query = (
                session.query(Inventory, Product, Category)
                .outerjoin(Product, Inventory.product_id == Product.id)
                .outerjoin(Category, Product.category_id == Category.id)
            )

            query = query.filter(Product.supplier_id==id)
            
            result = None

            if filter.sort is None:
                filter.sorters = create_sorters('modified_date', 'desc')
            query = filter_and_sort_query(filter.filters, filter.sorters, query, [Inventory, Product])

            query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
            
            inventories = query.all()

            result = {'inventories': self.get_inventory_model(inventories), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}

            return result, 200
        
    @handle_errors("Inventory")
    def get_inventories_grouping(self, id, filter): 
        with session_scope() as session:
            query = (
                session.query(Inventory, Store, Branch, Product)
                .outerjoin(Store, Inventory.store_id == Store.id)
                .outerjoin(Branch, Inventory.branch_id == Branch.id)
                .outerjoin(Product, Inventory.product_id == Product.id)
            )
            
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, [Inventory, Product])

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                inventories = query.all()
                result = {'inventories': self.get_grouped_inventory_model(inventories), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                inventories = query.filter_by(id=id).first()
                if inventories is None:
                    raise ResourceNotFoundError("Inventory")
                result = {'inventories': self.get_grouped_inventory_model(inventories)}

            return result, 200

    @handle_errors("Inventory")
    def get_inventories_stock(self, store, product): 
        with session_scope() as session:
            query = session.query(Inventory)
            inventories = query.filter(Inventory.store_id == store, Inventory.product_id == product).first()
            result = {'inventories': inventories.json()} if inventories else None

            return result, 200

    @handle_errors("Inventory")
    def get_inventories_branch(self, branch, product): 
        with session_scope() as session:
            query = session.query(Inventory)
            inventories = query.filter(Inventory.branch_id == branch, Inventory.product_id == product).first()
            result = {'inventories': inventories.json()} if inventories else None

            return result, 200

    @handle_errors("Inventory")
    def get_inventories_on_branch(self, branch, filter): 
        with session_scope() as session:
            query = session.query(Inventory, Product).filter(Inventory.product_id == Product.id).filter(Inventory.branch_id == branch)
            
            if filter.sort is None:
                filter.sorters = create_sorters('modified_date', 'desc')
            query = filter_and_sort_query(filter.filters, filter.sorters, query, Product)

            query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
            inventories = query.all()
            result = {'inventories': self.get_inventory_model(inventories), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            
            return result, 200

    @handle_errors("Inventory")
    def create_inventory(self, data):
        with session_scope() as session:
            inventory = Inventory(
                id=uuid.uuid4(),
                product_id=not_exisit_in_request(data, 'product_id', None),
                branch_id=not_exisit_in_request(data, 'branch_id', None),
                store_id=not_exisit_in_request(data, 'store_id', None),
                quantity=not_exisit_in_request(data, 'quantity', 0),
                quantity_alert=not_exisit_in_request(data, 'quantity_alert', 0),
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc)
            )  # type: ignore
            
            session.add(inventory)
            session.commit()
            
            return 'Inventory Created', 201

    @handle_errors("Inventory")
    def update_inventory(self, id, data):
        with session_scope() as session:
            inventory = session.query(Inventory).filter_by(id=id).first()

            if inventory is None:
                raise ResourceNotFoundError("Inventory")
            inventory.product_id = not_exisit_in_request(data, 'product_id', inventory.product_id)
            inventory.branch_id = not_exisit_in_request(data, 'branch_id', inventory.branch_id)
            inventory.store_id = not_exisit_in_request(data, 'store_id', inventory.store_id)
            inventory.quantity = not_exisit_in_request(data, 'quantity', inventory.quantity)
            inventory.quantity_alert = not_exisit_in_request(data, 'quantity_alert', inventory.quantity_alert)
            inventory.modified_date = datetime.now(timezone.utc)

            session.commit()

            return 'Updated', 200

    @handle_errors("Inventory")
    def update_stock(self, id, data, session=None):
        own_session = False
        if session is None:
            own_session = True
            session_ctx = session_scope()
            session = session_ctx.__enter__()

        try:
            #print(f"Updating stock for inventory_id={id}, product_id={data['product_id']}, qty={data['quantity']}")

            inventory = (
                session.query(Inventory)
                .filter_by(id=id)
                .with_for_update()
                .first()
            )

            if inventory is None:
                return False

            quantity = int(data['quantity'])

            if inventory.quantity < quantity:
                raise ValueError("Not enough stock available!")

            inventory.quantity = inventory.quantity - quantity
            inventory.modified_date = datetime.now(timezone.utc)
                
            # Create transaction inside same session
            body = {
                'product_id': data['product_id'],
                'from_location_id': data['branch_id'],
                'to_location_id': None,
                'quantity': quantity,
                'transaction_type': 'SALE',
                'transaction_date': datetime.now(timezone.utc)
            }
            service1 = TransactionService()
            service1.create_transaction(body, session=session)

            if own_session:
                session.commit()

            return True
        except Exception:
            if own_session:
                session.rollback()
            raise
        finally:
            if own_session:
                session_ctx.__exit__(None, None, None)
    
    @handle_errors("Inventory")
    def update_stock_refund(self, id, data):
        with session_scope() as session:
            inventory = session.query(Inventory).filter_by(id=id).first()
            if inventory is None:
                return False
            
            quantity = int(data['quantity'])
            current_stock = int(inventory.quantity)
            updated_stock = current_stock + quantity # add the quantity back to the stock

            inventory.quantity = updated_stock
            inventory.modified_date = datetime.now(timezone.utc)

            # create transaction
            body = {
                'product_id': data['product_id'],
                'from_location_id': data['branch_id'],
                'to_location_id': None,
                'quantity': quantity,
                'transaction_type': 'RETURN',
                'transaction_date': datetime.now(timezone.utc)
            }
            service1 = TransactionService()
            service1.create_transaction(body)

            session.commit()

            return True

    @handle_errors("Inventory")
    def delete_inventory(self, id):
        with session_scope() as session:
            inventory = session.query(Inventory).filter_by(id=id).first()

            if inventory is None:
                raise ResourceNotFoundError("Inventory")
            
            session.delete(inventory)
            session.commit()

            return 'Inventory deleted', 200

    @handle_errors("Inventory")
    def get_total_products_quantity(self, filter=None):
        """
        Get the total quantity of products in the inventory, optionally filtered by criteria.
        """
        with session_scope() as session:
            query = session.query(sql.func.sum(Inventory.quantity))
            
            # Apply filters if provided
            if filter:
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Inventory)

            total_quantity = query.scalar()
            return {'total_products_quantity': total_quantity or 0}, 200
    
    @handle_errors("Inventory")
    def get_products_status(self, items):
        with session_scope() as session:
            unavailable = []
            for item in items:
                inv_item = Inventory.query.filter_by(product_id=item['id']).first()
                if not inv_item or inv_item.quantity <= 0 or inv_item.quantity < item['quantity']:
                    unavailable.append(item)

            if unavailable:
                return {
                    "available": False,
                    "unavailable_items": unavailable
                }, 404
            else:
                return {"available": True}, 200
