#!/usr/bin/env python3
"""
Database Index Application Script

This script safely applies database indexes with monitoring and rollback capabilities.
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import Config


class IndexApplier:
    """Safely applies database indexes with monitoring."""
    
    def __init__(self, database_url: str, dry_run: bool = False):
        """Initialize the index applier."""
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        self.dry_run = dry_run
        self.applied_indexes = []
        self.failed_indexes = []
    
    def check_index_exists(self, table_name: str, index_name: str) -> bool:
        """Check if an index already exists."""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE tablename = :table_name 
                    AND indexname = :index_name
                )
            """), {"table_name": table_name, "index_name": index_name})
            
            return result.scalar()
    
    def get_table_size(self, table_name: str) -> int:
        """Get table size in bytes."""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT pg_total_relation_size(:table_name)
            """), {"table_name": table_name})
            
            return result.scalar()
    
    def estimate_index_size(self, table_name: str, columns: List[str]) -> int:
        """Estimate index size based on table size and columns."""
        table_size = self.get_table_size(table_name)
        
        # Rough estimation: index size is typically 20-30% of table size
        # Multiplied by number of columns
        estimated_size = int(table_size * 0.25 * len(columns))
        
        return estimated_size
    
    def create_index_safely(self, table_name: str, index_name: str, 
                          columns: List[str], index_type: str = 'btree',
                          concurrent: bool = True) -> bool:
        """Create an index safely with error handling."""
        
        if self.check_index_exists(table_name, index_name):
            print(f"  ✓ Index {index_name} already exists on {table_name}")
            return True
        
        # Estimate index size
        estimated_size = self.estimate_index_size(table_name, columns)
        size_mb = estimated_size / (1024 * 1024)
        
        print(f"  Creating index {index_name} on {table_name}({', '.join(columns)})")
        print(f"    Estimated size: {size_mb:.2f} MB")
        
        if self.dry_run:
            print(f"    [DRY RUN] Would create index {index_name}")
            return True
        
        try:
            # Build the CREATE INDEX statement
            columns_str = ', '.join(columns)
            concurrent_clause = 'CONCURRENTLY' if concurrent else ''
            
            create_sql = f"""
                CREATE INDEX {concurrent_clause} {index_name} 
                ON {table_name} USING {index_type} ({columns_str})
            """
            
            # Execute the index creation
            start_time = time.time()
            
            with self.engine.connect() as conn:
                conn.execute(text(create_sql))
                conn.commit()
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"    ✓ Created successfully in {duration:.2f} seconds")
            
            self.applied_indexes.append({
                'table': table_name,
                'index': index_name,
                'columns': columns,
                'type': index_type,
                'duration': duration,
                'estimated_size_mb': size_mb
            })
            
            return True
            
        except Exception as e:
            print(f"    ✗ Failed to create index: {e}")
            
            self.failed_indexes.append({
                'table': table_name,
                'index': index_name,
                'columns': columns,
                'type': index_type,
                'error': str(e)
            })
            
            return False
    
    def apply_indexes_from_migration(self) -> bool:
        """Apply indexes from the migration file."""
        print("Applying indexes from migration file...")
        
        # Define the indexes to create (from the migration file)
        indexes_to_create = [
            # User table indexes
            ('users', 'idx_users_active', ['active']),
            ('users', 'idx_users_user_type', ['user_type']),
            ('users', 'idx_users_language', ['language']),
            ('users', 'idx_users_create_date', ['create_date']),
            ('users', 'idx_users_modified_date', ['modified_date']),
            ('users', 'idx_users_phone_email', ['phone', 'email']),
            ('users', 'idx_users_active_type', ['active', 'user_type']),
            
            # Product table indexes
            ('product', 'idx_product_type', ['product_type']),
            ('product', 'idx_product_category_type', ['category_id', 'product_type']),
            ('product', 'idx_product_price', ['base_price']),
            ('product', 'idx_product_currency', ['currency']),
            ('product', 'idx_product_dynamic_pricing', ['is_dynamic_pricing']),
            ('product', 'idx_product_category_price', ['category_id', 'base_price']),
            ('product', 'idx_product_type_price', ['product_type', 'base_price']),
            ('product', 'idx_product_sku', ['sku']),
            ('product', 'idx_product_subcategory', ['subcategory_id']),
            
            # Category table indexes
            ('category', 'idx_category_parent', ['parent_id']),
            ('category', 'idx_category_active', ['is_active']),
            ('category', 'idx_category_featured', ['is_featured']),
            ('category', 'idx_category_active_featured', ['is_active', 'is_featured']),
            ('category', 'idx_category_slug', ['slug']),
            ('category', 'idx_category_parent_active', ['parent_id', 'is_active']),
            
            # Customer table indexes
            ('customer', 'idx_customer_user_id', ['user_id']),
            ('customer', 'idx_customer_mobile', ['mobile']),
            ('customer', 'idx_customer_phone', ['phone']),
            ('customer', 'idx_customer_city', ['city']),
            ('customer', 'idx_customer_country', ['country']),
            ('customer', 'idx_customer_customer_type', ['customer_type']),
            ('customer', 'idx_customer_status', ['status']),
            ('customer', 'idx_customer_create_date', ['create_date']),
            ('customer', 'idx_customer_modified_date', ['modified_date']),
            ('customer', 'idx_customer_user_status', ['user_id', 'status']),
            
            # Order table indexes
            ('order', 'idx_order_customer', ['customer_id']),
            ('order', 'idx_order_status', ['status']),
            ('order', 'idx_order_type', ['order_type']),
            ('order', 'idx_order_priority', ['priority']),
            ('order', 'idx_order_payment_status', ['payment_status']),
            ('order', 'idx_order_payment_method', ['payment_method']),
            ('order', 'idx_order_expected_delivery', ['expected_delivery']),
            ('order', 'idx_order_estimated_completion', ['estimated_completion']),
            ('order', 'idx_order_currency', ['currency']),
            ('order', 'idx_order_customer_status', ['customer_id', 'status']),
            ('order', 'idx_order_status_date', ['status', 'order_date']),
            ('order', 'idx_order_customer_date', ['customer_id', 'order_date']),
            ('order', 'idx_order_type_status', ['order_type', 'status']),
            ('order', 'idx_order_payment_status_date', ['payment_status', 'order_date']),
            ('order', 'idx_order_total_amount', ['total_amount']),
            ('order', 'idx_order_priority_status', ['priority', 'status']),
            
            # Order Item table indexes
            ('order_item', 'idx_order_item_order', ['order_id']),
            ('order_item', 'idx_order_item_product', ['product_id']),
            ('order_item', 'idx_order_item_order_product', ['order_id', 'product_id']),
            
            # Inventory table indexes
            ('inventory', 'idx_inventory_product_branch', ['product_id', 'branch_id']),
            ('inventory', 'idx_inventory_branch_store', ['branch_id', 'store_id']),
            ('inventory', 'idx_inventory_quantity', ['quantity']),
            ('inventory', 'idx_inventory_quantity_alert', ['quantity_alert']),
            ('inventory', 'idx_inventory_product_quantity', ['product_id', 'quantity']),
            ('inventory', 'idx_inventory_branch_quantity', ['branch_id', 'quantity']),
            ('inventory', 'idx_inventory_store_quantity', ['store_id', 'quantity']),
            ('inventory', 'idx_inventory_create_date', ['create_date']),
            ('inventory', 'idx_inventory_modified_date', ['modified_date']),
            
            # Transaction table indexes
            ('transaction', 'idx_transaction_product', ['product_id']),
            ('transaction', 'idx_transaction_type', ['transaction_type']),
            ('transaction', 'idx_transaction_date', ['transaction_date']),
            ('transaction', 'idx_transaction_financial_year', ['financial_year_id']),
            ('transaction', 'idx_transaction_from_location', ['from_location_id']),
            ('transaction', 'idx_transaction_to_location', ['to_location_id']),
            ('transaction', 'idx_transaction_product_type', ['product_id', 'transaction_type']),
            ('transaction', 'idx_transaction_type_date', ['transaction_type', 'transaction_date']),
            ('transaction', 'idx_transaction_from_to', ['from_location_id', 'to_location_id']),
            ('transaction', 'idx_transaction_create_date', ['create_date']),
            ('transaction', 'idx_transaction_modified_date', ['modified_date']),
        ]
        
        success_count = 0
        total_count = len(indexes_to_create)
        
        for table_name, index_name, columns in indexes_to_create:
            if self.create_index_safely(table_name, index_name, columns):
                success_count += 1
        
        print(f"\nIndex creation completed: {success_count}/{total_count} successful")
        
        return success_count == total_count
    
    def rollback_indexes(self) -> bool:
        """Rollback applied indexes."""
        if not self.applied_indexes:
            print("No indexes to rollback")
            return True
        
        print(f"Rolling back {len(self.applied_indexes)} indexes...")
        
        success_count = 0
        
        for index_info in reversed(self.applied_indexes):  # Reverse order
            table_name = index_info['table']
            index_name = index_info['index']
            
            try:
                if self.dry_run:
                    print(f"  [DRY RUN] Would drop index {index_name}")
                    success_count += 1
                else:
                    with self.engine.connect() as conn:
                        conn.execute(text(f"DROP INDEX IF EXISTS {index_name}"))
                        conn.commit()
                    
                    print(f"  ✓ Dropped index {index_name}")
                    success_count += 1
                    
            except Exception as e:
                print(f"  ✗ Failed to drop index {index_name}: {e}")
        
        print(f"Rollback completed: {success_count}/{len(self.applied_indexes)} successful")
        
        return success_count == len(self.applied_indexes)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a report of the index application process."""
        return {
            'timestamp': datetime.now().isoformat(),
            'dry_run': self.dry_run,
            'applied_indexes': self.applied_indexes,
            'failed_indexes': self.failed_indexes,
            'total_applied': len(self.applied_indexes),
            'total_failed': len(self.failed_indexes)
        }
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save the report to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"index_application_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Report saved to: {filename}")


def main():
    """Main function to run the index application."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Apply database indexes safely')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be done without making changes')
    parser.add_argument('--rollback', action='store_true',
                       help='Rollback previously applied indexes')
    
    args = parser.parse_args()
    
    try:
        # Get database URL from config
        config = Config()
        database_url = config.get_database_url()
        
        if not database_url:
            print("Error: Database URL not configured")
            sys.exit(1)
        
        # Create applier
        applier = IndexApplier(database_url, dry_run=args.dry_run)
        
        if args.rollback:
            print("Rolling back indexes...")
            success = applier.rollback_indexes()
        else:
            print("Applying indexes...")
            success = applier.apply_indexes_from_migration()
        
        # Generate and save report
        report = applier.generate_report()
        applier.save_report(report)
        
        if success:
            print("\nIndex operation completed successfully!")
        else:
            print("\nIndex operation completed with some failures.")
            print("Check the report for details.")
            sys.exit(1)
        
    except Exception as e:
        print(f"Error during index operation: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
