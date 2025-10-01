"""
Repository Usage Examples

This module demonstrates how to use the repository pattern with filtering,
sorting, and pagination in the 3D Store application.
"""

from app.product.repository import ProductRepository
from app.order.repository import OrderRepository
from app.users.repository import UserRepository
from app.utilities.db_utils import session_scope

def demonstrate_product_filtering():
    """
    Demonstrate how to use ProductRepository with various filtering options.
    """
    product_repo = ProductRepository()
    
    # Example 1: Get products with pagination and filtering
    class FilterObj:
        def __init__(self):
            self.page = 1
            self.per_page = 10
            self.sort = None
            self.sort_order = 'desc'
            self.filters = {}
            self.queries = {}
            self.sorters = []
    
    filter_obj = FilterObj()
    
    # Get paginated products with category information
    result = product_repo.get_products_with_category(filter_obj)
    print("Paginated Products:")
    print(f"Total products: {len(result['products'])}")
    print(f"Pagination info: {result['filters']}")
    
    # Example 2: Get products by type
    service_products = product_repo.get_products_by_type('service')
    print(f"\nService products: {len(service_products)}")
    
    # Example 3: Get featured products
    featured_products = product_repo.get_featured_products(limit=5)
    print(f"Featured products: {len(featured_products)}")
    
    # Example 4: Search products
    search_results = product_repo.search_products("3D printer")
    print(f"Search results for '3D printer': {len(search_results)}")
    
    # Example 5: Get products by price range
    price_range_products = product_repo.get_products_by_price_range(50.0, 200.0)
    print(f"Products in price range $50-$200: {len(price_range_products)}")

def demonstrate_order_filtering():
    """
    Demonstrate how to use OrderRepository with various filtering options.
    """
    order_repo = OrderRepository()
    
    # Example 1: Get orders by status
    from app.common.enum import OrderStatusEnum
    pending_orders = order_repo.get_orders_by_status(OrderStatusEnum.PENDING)
    print(f"Pending orders: {len(pending_orders)}")
    
    # Example 2: Get orders by customer
    customer_orders = order_repo.get_orders_by_customer("customer-uuid-here")
    print(f"Orders for customer: {len(customer_orders)}")
    
    # Example 3: Get orders by priority
    high_priority_orders = order_repo.get_orders_by_priority('high')
    print(f"High priority orders: {len(high_priority_orders)}")
    
    # Example 4: Get orders requiring attention
    urgent_orders = order_repo.get_orders_requiring_attention()
    print(f"Orders requiring attention: {len(urgent_orders)}")
    
    # Example 5: Get order statistics
    stats = order_repo.get_order_statistics()
    print(f"Order statistics: {stats}")

def demonstrate_user_filtering():
    """
    Demonstrate how to use UserRepository with various filtering options.
    """
    user_repo = UserRepository()
    
    # Example 1: Get users by type
    from app.common.enum import UserTypeEnum
    admin_users = user_repo.get_users_by_type(UserTypeEnum.ADMIN)
    print(f"Admin users: {len(admin_users)}")
    
    # Example 2: Get active users
    active_users = user_repo.get_active_users()
    print(f"Active users: {len(active_users)}")
    
    # Example 3: Search users
    search_results = user_repo.search_users("john")
    print(f"Users matching 'john': {len(search_results)}")
    
    # Example 4: Get recent users
    recent_users = user_repo.get_recent_users(limit=10)
    print(f"Recent users: {len(recent_users)}")
    
    # Example 5: Get user statistics
    stats = user_repo.get_user_statistics()
    print(f"User statistics: {stats}")

def demonstrate_advanced_filtering():
    """
    Demonstrate advanced filtering scenarios using repositories.
    """
    product_repo = ProductRepository()
    order_repo = OrderRepository()
    
    # Example 1: Complex product filtering with session management
    with session_scope() as session:
        # Get products with specific filters
        class AdvancedFilter:
            def __init__(self):
                self.page = 1
                self.per_page = 20
                self.sort = 'price'
                self.sort_order = 'asc'
                self.filters = {
                    'category_id': 'electronics-uuid',
                    'is_active': True,
                    'price__gte': 100.0,
                    'price__lte': 500.0
                }
                self.queries = {}
                self.sorters = []
        
        filter_obj = AdvancedFilter()
        result = product_repo.get_products_with_category(filter_obj, session=session)
        print(f"Advanced filtered products: {len(result['products'])}")
    
    # Example 2: Get products by supplier with inventory check
    supplier_products = product_repo.get_products_by_supplier("supplier-uuid")
    in_stock_products = [p for p in supplier_products if p.quantity > 0]
    print(f"Supplier products: {len(supplier_products)}")
    print(f"In stock products: {len(in_stock_products)}")
    
    # Example 3: Get orders with date range filtering
    from datetime import datetime, timezone, timedelta
    start_date = datetime.now(timezone.utc) - timedelta(days=30)
    end_date = datetime.now(timezone.utc)
    
    recent_orders = order_repo.get_orders_by_date_range(start_date, end_date)
    print(f"Orders in last 30 days: {len(recent_orders)}")

def demonstrate_repository_pattern_benefits():
    """
    Demonstrate the benefits of using the repository pattern.
    """
    print("\n=== Repository Pattern Benefits ===")
    
    # 1. Clean separation of concerns
    print("1. Clean separation of concerns:")
    print("   - Service layer focuses on business logic")
    print("   - Repository layer handles data access")
    print("   - No direct SQL queries in service classes")
    
    # 2. Consistent error handling
    print("\n2. Consistent error handling:")
    print("   - All repository methods use @handle_errors decorator")
    print("   - Automatic session management and rollback")
    print("   - Standardized error responses")
    
    # 3. Easy testing
    print("\n3. Easy testing:")
    print("   - Repositories can be easily mocked")
    print("   - Business logic can be tested independently")
    print("   - No database dependency in unit tests")
    
    # 4. Reusability
    print("\n4. Reusability:")
    print("   - Common operations available across all entities")
    print("   - Entity-specific methods can be reused")
    print("   - Consistent interface for all data access")
    
    # 5. Type safety
    print("\n5. Type safety:")
    print("   - Generic type support with BaseRepository[T]")
    print("   - Better IDE support and autocomplete")
    print("   - Compile-time type checking")

if __name__ == "__main__":
    print("=== Repository Pattern Usage Examples ===\n")
    
    try:
        print("1. Product Filtering Examples:")
        demonstrate_product_filtering()
        
        print("\n2. Order Filtering Examples:")
        demonstrate_order_filtering()
        
        print("\n3. User Filtering Examples:")
        demonstrate_user_filtering()
        
        print("\n4. Advanced Filtering Examples:")
        demonstrate_advanced_filtering()
        
        print("\n5. Repository Pattern Benefits:")
        demonstrate_repository_pattern_benefits()
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Note: These examples require a running database connection.")
