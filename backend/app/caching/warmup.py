"""
Cache Warmup Functions

Functions to warm up cache with frequently accessed data.
"""

from typing import List, Dict, Any
from flask import current_app

from .cache_service import CacheService
from .cache_managers import (
    UserCacheManager, 
    ProductCacheManager, 
    OrderCacheManager,
    InventoryCacheManager,
    FinancialCacheManager
)


def get_cache_service() -> CacheService:
    """Get cache service instance."""
    try:
        from extensions import cache
        cache_service = CacheService(cache)
        return cache_service if cache_service.enabled else None
    except Exception:
        return None


def warmup_user_cache() -> Dict[str, Any]:
    """Warm up user-related cache."""
    cache_service = get_cache_service()
    if not cache_service:
        return {'status': 'error', 'message': 'Cache service not available'}
    
    user_manager = UserCacheManager(cache_service)
    results = {'warmed': 0, 'errors': []}
    
    try:
        # Import here to avoid circular imports
        from app.users.service import UserService
        user_service = UserService()
        
        # Warm up active users
        # This would need to be implemented based on your user service
        # For example:
        # active_users = user_service.get_active_users()
        # for user in active_users:
        #     user_manager.set_user(user.id, user.to_dict())
        #     results['warmed'] += 1
        
        current_app.logger.info(f"User cache warmup completed: {results['warmed']} items")
        
    except Exception as e:
        error_msg = f"User cache warmup error: {str(e)}"
        results['errors'].append(error_msg)
        current_app.logger.error(error_msg)
    
    return results


def warmup_product_cache() -> Dict[str, Any]:
    """Warm up product-related cache."""
    cache_service = get_cache_service()
    if not cache_service:
        return {'status': 'error', 'message': 'Cache service not available'}
    
    product_manager = ProductCacheManager(cache_service)
    results = {'warmed': 0, 'errors': []}
    
    try:
        # Import here to avoid circular imports
        from app.product.service import ProductService
        product_service = ProductService()
        
        # Warm up popular products
        # This would need to be implemented based on your product service
        # For example:
        # popular_products = product_service.get_popular_products()
        # for product in popular_products:
        #     product_manager.set_product(product.id, product.to_dict())
        #     results['warmed'] += 1
        
        # Warm up categories
        # categories = product_service.get_all_categories()
        # for category in categories:
        #     products = product_service.get_products_by_category(category.id)
        #     product_manager.set_products_by_category(category.id, products)
        #     results['warmed'] += 1
        
        current_app.logger.info(f"Product cache warmup completed: {results['warmed']} items")
        
    except Exception as e:
        error_msg = f"Product cache warmup error: {str(e)}"
        results['errors'].append(error_msg)
        current_app.logger.error(error_msg)
    
    return results


def warmup_category_cache() -> Dict[str, Any]:
    """Warm up category-related cache."""
    cache_service = get_cache_service()
    if not cache_service:
        return {'status': 'error', 'message': 'Cache service not available'}
    
    results = {'warmed': 0, 'errors': []}
    
    try:
        # Import here to avoid circular imports
        from app.category.service import CategoryService
        category_service = CategoryService()
        
        # Warm up all categories
        # This would need to be implemented based on your category service
        # For example:
        # categories = category_service.get_all_categories()
        # for category in categories:
        #     cache_service.set(f"category:{category.id}", category.to_dict(), 3600)
        #     results['warmed'] += 1
        
        current_app.logger.info(f"Category cache warmup completed: {results['warmed']} items")
        
    except Exception as e:
        error_msg = f"Category cache warmup error: {str(e)}"
        results['errors'].append(error_msg)
        current_app.logger.error(error_msg)
    
    return results


def warmup_financial_cache() -> Dict[str, Any]:
    """Warm up financial-related cache."""
    cache_service = get_cache_service()
    if not cache_service:
        return {'status': 'error', 'message': 'Cache service not available'}
    
    financial_manager = FinancialCacheManager(cache_service)
    results = {'warmed': 0, 'errors': []}
    
    try:
        # Import here to avoid circular imports
        from app.financial.service import FinancialService
        financial_service = FinancialService()
        
        # Warm up dashboard statistics
        # This would need to be implemented based on your financial service
        # For example:
        # dashboard_stats = financial_service.get_dashboard_stats()
        # financial_manager.set_dashboard_stats('global', dashboard_stats)
        # results['warmed'] += 1
        
        current_app.logger.info(f"Financial cache warmup completed: {results['warmed']} items")
        
    except Exception as e:
        error_msg = f"Financial cache warmup error: {str(e)}"
        results['errors'].append(error_msg)
        current_app.logger.error(error_msg)
    
    return results


def warmup_inventory_cache() -> Dict[str, Any]:
    """Warm up inventory-related cache."""
    cache_service = get_cache_service()
    if not cache_service:
        return {'status': 'error', 'message': 'Cache service not available'}
    
    inventory_manager = InventoryCacheManager(cache_service)
    results = {'warmed': 0, 'errors': []}
    
    try:
        # Import here to avoid circular imports
        from app.inventory.service import InventoryService
        inventory_service = InventoryService()
        
        # Warm up inventory data
        # This would need to be implemented based on your inventory service
        # For example:
        # inventory_items = inventory_service.get_all_inventory()
        # for item in inventory_items:
        #     inventory_manager.set_inventory(item.product_id, item.branch_id, item.to_dict())
        #     results['warmed'] += 1
        
        current_app.logger.info(f"Inventory cache warmup completed: {results['warmed']} items")
        
    except Exception as e:
        error_msg = f"Inventory cache warmup error: {str(e)}"
        results['errors'].append(error_msg)
        current_app.logger.error(error_msg)
    
    return results


def warmup_all_cache() -> Dict[str, Any]:
    """Warm up all cache systems."""
    results = {
        'total_warmed': 0,
        'total_errors': 0,
        'results': {}
    }
    
    warmup_functions = [
        ('user', warmup_user_cache),
        ('product', warmup_product_cache),
        ('category', warmup_category_cache),
        ('financial', warmup_financial_cache),
        ('inventory', warmup_inventory_cache)
    ]
    
    for name, func in warmup_functions:
        try:
            result = func()
            results['results'][name] = result
            results['total_warmed'] += result.get('warmed', 0)
            results['total_errors'] += len(result.get('errors', []))
        except Exception as e:
            error_msg = f"Warmup function {name} failed: {str(e)}"
            results['results'][name] = {'status': 'error', 'message': error_msg}
            results['total_errors'] += 1
            current_app.logger.error(error_msg)
    
    current_app.logger.info(f"Cache warmup completed: {results['total_warmed']} items, {results['total_errors']} errors")
    
    return results


def schedule_cache_warmup():
    """Schedule cache warmup tasks."""
    try:
        from extensions import scheduler
        
        # Schedule warmup every hour
        scheduler.add_job(
            id='cache_warmup',
            func=warmup_all_cache,
            trigger='interval',
            hours=1,
            replace_existing=True
        )
        
        current_app.logger.info("Cache warmup scheduled")
        
    except Exception as e:
        current_app.logger.error(f"Failed to schedule cache warmup: {str(e)}")


def get_warmup_status() -> Dict[str, Any]:
    """Get cache warmup status."""
    cache_service = get_cache_service()
    if not cache_service:
        return {'status': 'error', 'message': 'Cache service not available'}
    
    stats = cache_service.get_stats()
    
    return {
        'status': 'healthy',
        'cache_stats': stats,
        'warmup_functions': [
            'warmup_user_cache',
            'warmup_product_cache', 
            'warmup_category_cache',
            'warmup_financial_cache',
            'warmup_inventory_cache'
        ]
    }
