"""
Inventory Repository

This module provides the InventoryRepository class that implements data access
operations specific to the Inventory entity in the 3D Store application.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from app.repositories.base import BaseRepository
from app.inventory.model import Inventory
from app.product.model import Product
from app.branch.model import Branch
from app.store.model import Store
from app.utilities.error_utils import handle_errors
from app.utilities.db_utils import session_scope

class InventoryRepository(BaseRepository[Inventory]):
    """
    Repository class for Inventory entity operations.
    
    Extends BaseRepository with Inventory-specific data access methods.
    """
    
    def __init__(self):
        super().__init__(Inventory)
    
    @handle_errors("InventoryRepository")
    def get_inventory_with_details(self, inventory_id: str, session: Optional[Session] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve inventory with all its related details.
        
        Args:
            inventory_id: The unique identifier of the inventory
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing inventory with all related details
        """
        if session:
            inventory = session.query(Inventory).options(
                joinedload(Inventory.product),
                joinedload(Inventory.branch),
                joinedload(Inventory.store)
            ).filter_by(id=inventory_id).first()
            
            if not inventory:
                return None
            
            return {
                'inventory': inventory,
                'product': inventory.product,
                'branch': inventory.branch,
                'store': inventory.store
            }
        
        with session_scope() as session:
            return self.get_inventory_with_details(inventory_id, session)
    
    @handle_errors("InventoryRepository")
    def get_inventory_by_product(self, product_id: str, session: Optional[Session] = None) -> List[Inventory]:
        """
        Retrieve all inventory records for a specific product.
        
        Args:
            product_id: The unique identifier of the product
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of inventory records for the product
        """
        if session:
            return session.query(Inventory).filter_by(product_id=product_id).all()
        
        with session_scope() as session:
            return session.query(Inventory).filter_by(product_id=product_id).all()
    
    @handle_errors("InventoryRepository")
    def get_inventory_by_branch(self, branch_id: str, session: Optional[Session] = None) -> List[Inventory]:
        """
        Retrieve all inventory records for a specific branch.
        
        Args:
            branch_id: The unique identifier of the branch
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of inventory records for the branch
        """
        if session:
            return session.query(Inventory).filter_by(branch_id=branch_id).all()
        
        with session_scope() as session:
            return session.query(Inventory).filter_by(branch_id=branch_id).all()
    
    @handle_errors("InventoryRepository")
    def get_inventory_by_store(self, store_id: str, session: Optional[Session] = None) -> List[Inventory]:
        """
        Retrieve all inventory records for a specific store.
        
        Args:
            store_id: The unique identifier of the store
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of inventory records for the store
        """
        if session:
            return session.query(Inventory).filter_by(store_id=store_id).all()
        
        with session_scope() as session:
            return session.query(Inventory).filter_by(store_id=store_id).all()
    
    @handle_errors("InventoryRepository")
    def get_inventory_by_product_and_location(self, product_id: str, branch_id: str = None, store_id: str = None, session: Optional[Session] = None) -> Optional[Inventory]:
        """
        Retrieve inventory for a specific product at a specific location.
        
        Args:
            product_id: The unique identifier of the product
            branch_id: The unique identifier of the branch (optional)
            store_id: The unique identifier of the store (optional)
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The inventory record if found, None otherwise
        """
        if session:
            query = session.query(Inventory).filter_by(product_id=product_id)
            if branch_id:
                query = query.filter_by(branch_id=branch_id)
            if store_id:
                query = query.filter_by(store_id=store_id)
            return query.first()
        
        with session_scope() as session:
            return self.get_inventory_by_product_and_location(product_id, branch_id, store_id, session)
    
    @handle_errors("InventoryRepository")
    def get_low_stock_items(self, threshold: int = 10, session: Optional[Session] = None) -> List[Inventory]:
        """
        Retrieve inventory items that are below the specified threshold.
        
        Args:
            threshold: The quantity threshold to check against
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of inventory items below the threshold
        """
        if session:
            return session.query(Inventory).filter(Inventory.quantity <= threshold).all()
        
        with session_scope() as session:
            return session.query(Inventory).filter(Inventory.quantity <= threshold).all()
    
    @handle_errors("InventoryRepository")
    def get_out_of_stock_items(self, session: Optional[Session] = None) -> List[Inventory]:
        """
        Retrieve inventory items that are out of stock.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of out-of-stock inventory items
        """
        if session:
            return session.query(Inventory).filter(Inventory.quantity <= 0).all()
        
        with session_scope() as session:
            return session.query(Inventory).filter(Inventory.quantity <= 0).all()
    
    @handle_errors("InventoryRepository")
    def get_in_stock_items(self, session: Optional[Session] = None) -> List[Inventory]:
        """
        Retrieve inventory items that are in stock.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of in-stock inventory items
        """
        if session:
            return session.query(Inventory).filter(Inventory.quantity > 0).all()
        
        with session_scope() as session:
            return session.query(Inventory).filter(Inventory.quantity > 0).all()
    
    @handle_errors("InventoryRepository")
    def update_quantity(self, inventory_id: str, new_quantity: int, session: Optional[Session] = None) -> bool:
        """
        Update the quantity of an inventory item.
        
        Args:
            inventory_id: The unique identifier of the inventory item
            new_quantity: The new quantity
            session: Optional database session (if None, creates a new one)
            
        Returns:
            True if updated successfully
        """
        if session:
            inventory = session.query(Inventory).filter_by(id=inventory_id).first()
            if inventory:
                inventory.quantity = new_quantity
                session.flush()
                return True
            return False
        
        with session_scope() as session:
            return self.update_quantity(inventory_id, new_quantity, session)
    
    @handle_errors("InventoryRepository")
    def adjust_quantity(self, inventory_id: str, adjustment: int, session: Optional[Session] = None) -> bool:
        """
        Adjust the quantity of an inventory item by a specific amount.
        
        Args:
            inventory_id: The unique identifier of the inventory item
            adjustment: The amount to adjust (positive or negative)
            session: Optional database session (if None, creates a new one)
            
        Returns:
            True if adjusted successfully
        """
        if session:
            inventory = session.query(Inventory).filter_by(id=inventory_id).first()
            if inventory:
                inventory.quantity += adjustment
                session.flush()
                return True
            return False
        
        with session_scope() as session:
            return self.adjust_quantity(inventory_id, adjustment, session)
    
    @handle_errors("InventoryRepository")
    def get_inventory_alerts(self, session: Optional[Session] = None) -> List[Inventory]:
        """
        Retrieve inventory items that have quantity alerts set and are below the alert threshold.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of inventory items with alerts
        """
        if session:
            return session.query(Inventory).filter(
                and_(
                    Inventory.quantity_alert.isnot(None),
                    Inventory.quantity <= Inventory.quantity_alert
                )
            ).all()
        
        with session_scope() as session:
            return session.query(Inventory).filter(
                and_(
                    Inventory.quantity_alert.isnot(None),
                    Inventory.quantity <= Inventory.quantity_alert
                )
            ).all()
    
    @handle_errors("InventoryRepository")
    def get_total_quantity_by_product(self, product_id: str, session: Optional[Session] = None) -> int:
        """
        Get the total quantity of a product across all locations.
        
        Args:
            product_id: The unique identifier of the product
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Total quantity of the product across all locations
        """
        if session:
            result = session.query(Inventory).filter_by(product_id=product_id).with_entities(
                session.query(Inventory.quantity).label('total')
            ).all()
            return sum([inventory.total for inventory in result if inventory.total])
        
        with session_scope() as session:
            return self.get_total_quantity_by_product(product_id, session)
    
    @handle_errors("InventoryRepository")
    def get_inventory_summary_by_location(self, location_type: str, location_id: str, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get inventory summary for a specific location.
        
        Args:
            location_type: Type of location (branch or store)
            location_id: The unique identifier of the location
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing inventory summary
        """
        if session:
            if location_type == 'branch':
                inventory_items = session.query(Inventory).filter_by(branch_id=location_id).all()
            elif location_type == 'store':
                inventory_items = session.query(Inventory).filter_by(store_id=location_id).all()
            else:
                return {}
            
            total_items = len(inventory_items)
            total_quantity = sum([item.quantity for item in inventory_items])
            out_of_stock = len([item for item in inventory_items if item.quantity <= 0])
            low_stock = len([item for item in inventory_items if item.quantity_alert and item.quantity <= item.quantity_alert])
            
            return {
                'total_items': total_items,
                'total_quantity': total_quantity,
                'out_of_stock': out_of_stock,
                'low_stock': low_stock
            }
        
        with session_scope() as session:
            return self.get_inventory_summary_by_location(location_type, location_id, session)
    
    @handle_errors("InventoryRepository")
    def get_inventory_statistics(self, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Get inventory statistics for dashboard/reporting.
        
        Args:
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing inventory statistics
        """
        if session:
            total_items = session.query(Inventory).count()
            in_stock_items = session.query(Inventory).filter(Inventory.quantity > 0).count()
            out_of_stock_items = session.query(Inventory).filter(Inventory.quantity <= 0).count()
            low_stock_items = session.query(Inventory).filter(
                and_(
                    Inventory.quantity_alert.isnot(None),
                    Inventory.quantity <= Inventory.quantity_alert
                )
            ).count()
            
            total_quantity = session.query(Inventory).with_entities(
                session.query(Inventory.quantity).label('total')
            ).all()
            total_quantity_value = sum([item.total for item in total_quantity if item.total])
            
            return {
                'total_items': total_items,
                'in_stock_items': in_stock_items,
                'out_of_stock_items': out_of_stock_items,
                'low_stock_items': low_stock_items,
                'total_quantity': total_quantity_value
            }
        
        with session_scope() as session:
            return self.get_inventory_statistics(session)
