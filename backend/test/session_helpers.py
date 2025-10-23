"""
Session Management Helpers for Tests

These helpers solve the DetachedInstanceError problem where service calls
create objects in their own session context, causing test fixtures to become
detached.

Usage:
    from test.session_helpers import refresh_object, get_fresh_object
    
    # After service call, refresh the object
    product = refresh_object(db_session, product)
    
    # Or get a fresh copy
    product = get_fresh_object(db_session, Product, product.id)
"""

def refresh_object(session, obj):
    """
    Refresh an object that may have become detached from its session.
    
    Args:
        session: The active database session
        obj: The object to refresh
        
    Returns:
        The refreshed object, or a freshly queried copy if refresh fails
    """
    try:
        session.refresh(obj)
        return obj
    except Exception:
        # Object is detached, query a fresh copy
        obj_class = type(obj)
        obj_id = obj.id
        return session.query(obj_class).filter_by(id=obj_id).first()


def get_fresh_object(session, model_class, object_id):
    """
    Get a fresh copy of an object from the database.
    
    Args:
        session: The active database session
        model_class: The SQLAlchemy model class
        object_id: The ID of the object to retrieve
        
    Returns:
        Fresh instance of the object from the database
    """
    return session.query(model_class).filter_by(id=object_id).first()


def get_fresh_objects(session, model_class, **filters):
    """
    Get fresh copies of multiple objects from the database.
    
    Args:
        session: The active database session
        model_class: The SQLAlchemy model class
        **filters: Filter conditions (e.g., user_id=user.id)
        
    Returns:
        List of fresh instances from the database
    """
    return session.query(model_class).filter_by(**filters).all()

