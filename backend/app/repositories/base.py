"""
Base Repository Pattern Implementation

This module provides the base repository class that implements common CRUD operations
and data access patterns for all entities in the 3D Store application.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Union
from sqlalchemy.orm import Session, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_filters import apply_pagination, apply_sort
from app.utilities.db_utils import session_scope
from app.common.error_handling import ResourceNotFoundError
from app.exceptions.base import DatabaseException
from app.common.queries import create_sorters, filter_and_sort_query
from app.common import filters_serialization
from app.utilities.error_utils import handle_errors
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """
    Base repository class that provides common CRUD operations and data access patterns.
    
    This class implements the Repository pattern to abstract data access logic
    and provide a consistent interface for database operations across all entities.
    """
    
    def __init__(self, model_class: Type[T]):
        """
        Initialize the repository with a specific model class.
        
        Args:
            model_class: The SQLAlchemy model class this repository manages
        """
        self.model_class = model_class
        self.table_name = model_class.__tablename__
    
    @handle_errors("Repository")
    def get_by_id(self, entity_id: str, session: Optional[Session] = None) -> Optional[T]:
        """
        Retrieve an entity by its ID.
        
        Args:
            entity_id: The unique identifier of the entity
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The entity if found, None otherwise
        """
        if session:
            return session.query(self.model_class).filter_by(id=entity_id).first()
        
        with session_scope() as session:
            return session.query(self.model_class).filter_by(id=entity_id).first()
    
    @handle_errors("Repository")
    def get_by_id_or_404(self, entity_id: str, session: Optional[Session] = None) -> T:
        """
        Retrieve an entity by its ID or raise 404 error if not found.
        
        Args:
            entity_id: The unique identifier of the entity
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The entity if found
            
        Raises:
            ResourceNotFoundError: If entity is not found
        """
        entity = self.get_by_id(entity_id, session)
        if not entity:
            raise ResourceNotFoundError(self.model_class.__name__)
        return entity
    
    @handle_errors("Repository")
    def get_all(self, session: Optional[Session] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """
        Retrieve all entities with optional pagination.
        
        Args:
            session: Optional database session (if None, creates a new one)
            limit: Maximum number of entities to return
            offset: Number of entities to skip
            
        Returns:
            List of entities
        """
        if session:
            query = session.query(self.model_class)
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        
        with session_scope() as session:
            query = session.query(self.model_class)
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
    
    @handle_errors("Repository")
    def get_filtered(self, filters: Dict[str, Any], session: Optional[Session] = None) -> List[T]:
        """
        Retrieve entities based on filter criteria.
        
        Args:
            filters: Dictionary of filter criteria
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of filtered entities
        """
        if session:
            query = session.query(self.model_class)
            query = filter_and_sort_query(filters, [], query, self.model_class)
            return query.all()
        
        with session_scope() as session:
            query = session.query(self.model_class)
            query = filter_and_sort_query(filters, [], query, self.model_class)
            return query.all()
    
    @handle_errors("Repository")
    def get_paginated(self, filter_obj, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Retrieve entities with pagination and filtering.
        
        Args:
            filter_obj: Filter object containing pagination and sorting parameters
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Dictionary containing entities and pagination metadata
        """
        if session:
            query = session.query(self.model_class)
            
            # Apply sorting
            if filter_obj.sort is None:
                filter_obj.sorters = create_sorters('modified_date', 'desc')
            query = filter_and_sort_query(filter_obj.filters, filter_obj.sorters, query, self.model_class)
            
            # Apply pagination
            query, pagination = apply_pagination(
                query, 
                page_number=int(filter_obj.page), 
                page_size=int(filter_obj.per_page)
            )
            
            entities = query.all()
            
            return {
                'entities': entities,
                'filters': filters_serialization.get_pagination_serialization(
                    pagination, filter_obj.sort, filter_obj.sort_order, filter_obj.queries
                )
            }
        
        with session_scope() as session:
            return self.get_paginated(filter_obj, session)
    
    @handle_errors("Repository")
    def create(self, entity_data: Dict[str, Any], session: Optional[Session] = None) -> T:
        """
        Create a new entity.
        
        Args:
            entity_data: Dictionary containing entity data
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The created entity
        """
        if session:
            entity = self.model_class(**entity_data)
            session.add(entity)
            session.flush()  # Flush to get the ID without committing
            return entity
        
        with session_scope() as session:
            entity = self.model_class(**entity_data)
            session.add(entity)
            session.flush()
            return entity
    
    @handle_errors("Repository")
    def update(self, entity_id: str, entity_data: Dict[str, Any], session: Optional[Session] = None) -> Optional[T]:
        """
        Update an existing entity.
        
        Args:
            entity_id: The unique identifier of the entity
            entity_data: Dictionary containing updated entity data
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The updated entity if found, None otherwise
        """
        if session:
            entity = session.query(self.model_class).filter_by(id=entity_id).first()
            if entity:
                for key, value in entity_data.items():
                    if hasattr(entity, key):
                        setattr(entity, key, value)
                session.flush()
            return entity
        
        with session_scope() as session:
            entity = session.query(self.model_class).filter_by(id=entity_id).first()
            if entity:
                for key, value in entity_data.items():
                    if hasattr(entity, key):
                        setattr(entity, key, value)
                session.flush()
            return entity
    
    @handle_errors("Repository")
    def update_or_404(self, entity_id: str, entity_data: Dict[str, Any], session: Optional[Session] = None) -> T:
        """
        Update an existing entity or raise 404 error if not found.
        
        Args:
            entity_id: The unique identifier of the entity
            entity_data: Dictionary containing updated entity data
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The updated entity
            
        Raises:
            ResourceNotFoundError: If entity is not found
        """
        entity = self.update(entity_id, entity_data, session)
        if not entity:
            raise ResourceNotFoundError(self.model_class.__name__)
        return entity
    
    @handle_errors("Repository")
    def delete(self, entity_id: str, session: Optional[Session] = None) -> bool:
        """
        Delete an entity by its ID.
        
        Args:
            entity_id: The unique identifier of the entity
            session: Optional database session (if None, creates a new one)
            
        Returns:
            True if entity was deleted, False if not found
        """
        if session:
            entity = session.query(self.model_class).filter_by(id=entity_id).first()
            if entity:
                session.delete(entity)
                session.flush()
                return True
            return False
        
        with session_scope() as session:
            entity = session.query(self.model_class).filter_by(id=entity_id).first()
            if entity:
                session.delete(entity)
                session.flush()
                return True
            return False
    
    @handle_errors("Repository")
    def delete_or_404(self, entity_id: str, session: Optional[Session] = None) -> bool:
        """
        Delete an entity by its ID or raise 404 error if not found.
        
        Args:
            entity_id: The unique identifier of the entity
            session: Optional database session (if None, creates a new one)
            
        Returns:
            True if entity was deleted
            
        Raises:
            ResourceNotFoundError: If entity is not found
        """
        if not self.delete(entity_id, session):
            raise ResourceNotFoundError(self.model_class.__name__)
        return True
    
    @handle_errors("Repository")
    def exists(self, entity_id: str, session: Optional[Session] = None) -> bool:
        """
        Check if an entity exists by its ID.
        
        Args:
            entity_id: The unique identifier of the entity
            session: Optional database session (if None, creates a new one)
            
        Returns:
            True if entity exists, False otherwise
        """
        if session:
            return session.query(self.model_class).filter_by(id=entity_id).first() is not None
        
        with session_scope() as session:
            return session.query(self.model_class).filter_by(id=entity_id).first() is not None
    
    @handle_errors("Repository")
    def count(self, filters: Optional[Dict[str, Any]] = None, session: Optional[Session] = None) -> int:
        """
        Count entities matching the given filters.
        
        Args:
            filters: Optional dictionary of filter criteria
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Number of entities matching the filters
        """
        if session:
            query = session.query(self.model_class)
            if filters:
                query = filter_and_sort_query(filters, [], query, self.model_class)
            return query.count()
        
        with session_scope() as session:
            query = session.query(self.model_class)
            if filters:
                query = filter_and_sort_query(filters, [], query, self.model_class)
            return query.count()
    
    @handle_errors("Repository")
    def get_by_field(self, field_name: str, field_value: Any, session: Optional[Session] = None) -> Optional[T]:
        """
        Retrieve an entity by a specific field value.
        
        Args:
            field_name: Name of the field to filter by
            field_value: Value to match
            session: Optional database session (if None, creates a new one)
            
        Returns:
            The entity if found, None otherwise
        """
        if session:
            return session.query(self.model_class).filter(getattr(self.model_class, field_name) == field_value).first()
        
        with session_scope() as session:
            return session.query(self.model_class).filter(getattr(self.model_class, field_name) == field_value).first()
    
    @handle_errors("Repository")
    def get_all_by_field(self, field_name: str, field_value: Any, session: Optional[Session] = None) -> List[T]:
        """
        Retrieve all entities matching a specific field value.
        
        Args:
            field_name: Name of the field to filter by
            field_value: Value to match
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of entities matching the field value
        """
        if session:
            return session.query(self.model_class).filter(getattr(self.model_class, field_name) == field_value).all()
        
        with session_scope() as session:
            return session.query(self.model_class).filter(getattr(self.model_class, field_name) == field_value).all()
    
    @handle_errors("Repository")
    def bulk_create(self, entities_data: List[Dict[str, Any]], session: Optional[Session] = None) -> List[T]:
        """
        Create multiple entities in a single operation.
        
        Args:
            entities_data: List of dictionaries containing entity data
            session: Optional database session (if None, creates a new one)
            
        Returns:
            List of created entities
        """
        if session:
            entities = [self.model_class(**data) for data in entities_data]
            session.add_all(entities)
            session.flush()
            return entities
        
        with session_scope() as session:
            entities = [self.model_class(**data) for data in entities_data]
            session.add_all(entities)
            session.flush()
            return entities
    
    @handle_errors("Repository")
    def bulk_update(self, updates: List[Dict[str, Any]], session: Optional[Session] = None) -> int:
        """
        Update multiple entities in a single operation.
        
        Args:
            updates: List of dictionaries containing id and update data
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Number of entities updated
        """
        if session:
            updated_count = 0
            for update_data in updates:
                entity_id = update_data.pop('id')
                entity = session.query(self.model_class).filter_by(id=entity_id).first()
                if entity:
                    for key, value in update_data.items():
                        if hasattr(entity, key):
                            setattr(entity, key, value)
                    updated_count += 1
            session.flush()
            return updated_count
        
        with session_scope() as session:
            return self.bulk_update(updates, session)
    
    @handle_errors("Repository")
    def bulk_delete(self, entity_ids: List[str], session: Optional[Session] = None) -> int:
        """
        Delete multiple entities in a single operation.
        
        Args:
            entity_ids: List of entity IDs to delete
            session: Optional database session (if None, creates a new one)
            
        Returns:
            Number of entities deleted
        """
        if session:
            deleted_count = session.query(self.model_class).filter(self.model_class.id.in_(entity_ids)).delete(synchronize_session=False)
            session.flush()
            return deleted_count
        
        with session_scope() as session:
            deleted_count = session.query(self.model_class).filter(self.model_class.id.in_(entity_ids)).delete(synchronize_session=False)
            session.flush()
            return deleted_count