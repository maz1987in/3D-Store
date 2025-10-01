#!/usr/bin/env python3
"""
Database Index Analysis Script

This script analyzes the current database indexes and suggests additional
indexes for performance optimization.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from config import Config


class IndexAnalyzer:
    """Analyzes database indexes and suggests optimizations."""
    
    def __init__(self, database_url: str):
        """Initialize the analyzer with database connection."""
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        self.inspector = inspect(self.engine)
    
    def get_existing_indexes(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all existing indexes from the database."""
        indexes = {}
        
        for table_name in self.inspector.get_table_names():
            table_indexes = self.inspector.get_indexes(table_name)
            indexes[table_name] = table_indexes
        
        return indexes
    
    def get_table_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get table statistics including row counts and sizes."""
        stats = {}
        
        with self.engine.connect() as conn:
            for table_name in self.inspector.get_table_names():
                # Get row count
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                row_count = result.scalar()
                
                # Get table size
                result = conn.execute(text(f"""
                    SELECT pg_size_pretty(pg_total_relation_size('{table_name}')) as size,
                           pg_total_relation_size('{table_name}') as size_bytes
                """))
                size_info = result.fetchone()
                
                stats[table_name] = {
                    'row_count': row_count,
                    'size': size_info[0] if size_info else 'Unknown',
                    'size_bytes': size_info[1] if size_info else 0
                }
        
        return stats
    
    def get_index_usage_stats(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get index usage statistics."""
        usage_stats = {}
        
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch,
                    idx_scan::float / NULLIF(idx_tup_read, 0) as efficiency
                FROM pg_stat_user_indexes
                ORDER BY idx_scan DESC
            """))
            
            for row in result:
                table_name = row[1]
                if table_name not in usage_stats:
                    usage_stats[table_name] = []
                
                usage_stats[table_name].append({
                    'index_name': row[2],
                    'scans': row[3],
                    'tuples_read': row[4],
                    'tuples_fetched': row[5],
                    'efficiency': float(row[6]) if row[6] else 0.0
                })
        
        return usage_stats
    
    def get_slow_queries(self) -> List[Dict[str, Any]]:
        """Get slow query information (if pg_stat_statements is available)."""
        slow_queries = []
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        query,
                        calls,
                        total_time,
                        mean_time,
                        rows,
                        100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
                    FROM pg_stat_statements
                    WHERE mean_time > 100  -- Queries taking more than 100ms on average
                    ORDER BY mean_time DESC
                    LIMIT 20
                """))
                
                for row in result:
                    slow_queries.append({
                        'query': row[0][:200] + '...' if len(row[0]) > 200 else row[0],
                        'calls': row[1],
                        'total_time': row[2],
                        'mean_time': row[3],
                        'rows': row[4],
                        'hit_percent': row[5]
                    })
        except Exception as e:
            print(f"Warning: Could not get slow queries: {e}")
        
        return slow_queries
    
    def suggest_indexes(self) -> Dict[str, List[Dict[str, Any]]]:
        """Suggest additional indexes based on common patterns."""
        suggestions = {}
        
        # Common index suggestions based on query patterns
        suggestions['users'] = [
            {
                'columns': ['active', 'user_type'],
                'type': 'btree',
                'reason': 'Filter active users by type',
                'priority': 'high'
            },
            {
                'columns': ['create_date'],
                'type': 'btree',
                'reason': 'Sort by registration date',
                'priority': 'medium'
            },
            {
                'columns': ['phone', 'email'],
                'type': 'btree',
                'reason': 'Lookup by contact information',
                'priority': 'high'
            }
        ]
        
        suggestions['product'] = [
            {
                'columns': ['category_id', 'product_type'],
                'type': 'btree',
                'reason': 'Filter products by category and type',
                'priority': 'high'
            },
            {
                'columns': ['base_price'],
                'type': 'btree',
                'reason': 'Sort by price',
                'priority': 'medium'
            },
            {
                'columns': ['category_id', 'base_price'],
                'type': 'btree',
                'reason': 'Filter by category and sort by price',
                'priority': 'high'
            },
            {
                'columns': ['is_dynamic_pricing'],
                'type': 'btree',
                'reason': 'Filter dynamic pricing products',
                'priority': 'low'
            }
        ]
        
        suggestions['order'] = [
            {
                'columns': ['customer_id', 'status'],
                'type': 'btree',
                'reason': 'Filter orders by customer and status',
                'priority': 'high'
            },
            {
                'columns': ['status', 'order_date'],
                'type': 'btree',
                'reason': 'Filter by status and sort by date',
                'priority': 'high'
            },
            {
                'columns': ['payment_status', 'order_date'],
                'type': 'btree',
                'reason': 'Filter by payment status and sort by date',
                'priority': 'high'
            },
            {
                'columns': ['total_amount'],
                'type': 'btree',
                'reason': 'Sort by total amount',
                'priority': 'medium'
            }
        ]
        
        suggestions['inventory'] = [
            {
                'columns': ['product_id', 'branch_id'],
                'type': 'btree',
                'reason': 'Filter inventory by product and branch',
                'priority': 'high'
            },
            {
                'columns': ['quantity'],
                'type': 'btree',
                'reason': 'Filter by quantity (low stock alerts)',
                'priority': 'medium'
            },
            {
                'columns': ['branch_id', 'quantity'],
                'type': 'btree',
                'reason': 'Filter by branch and quantity',
                'priority': 'medium'
            }
        ]
        
        suggestions['transaction'] = [
            {
                'columns': ['product_id', 'transaction_type'],
                'type': 'btree',
                'reason': 'Filter transactions by product and type',
                'priority': 'high'
            },
            {
                'columns': ['transaction_type', 'transaction_date'],
                'type': 'btree',
                'reason': 'Filter by type and sort by date',
                'priority': 'high'
            },
            {
                'columns': ['from_location_id', 'to_location_id'],
                'type': 'btree',
                'reason': 'Track movement between locations',
                'priority': 'medium'
            }
        ]
        
        suggestions['payment_transaction'] = [
            {
                'columns': ['payment_status'],
                'type': 'btree',
                'reason': 'Filter by payment status',
                'priority': 'high'
            },
            {
                'columns': ['payment_gateway', 'create_date'],
                'type': 'btree',
                'reason': 'Filter by gateway and sort by date',
                'priority': 'medium'
            },
            {
                'columns': ['amount'],
                'type': 'btree',
                'reason': 'Sort by amount',
                'priority': 'medium'
            }
        ]
        
        suggestions['customer'] = [
            {
                'columns': ['user_id', 'status'],
                'type': 'btree',
                'reason': 'Filter customers by user and status',
                'priority': 'high'
            },
            {
                'columns': ['city', 'country'],
                'type': 'btree',
                'reason': 'Filter by location',
                'priority': 'medium'
            },
            {
                'columns': ['create_date'],
                'type': 'btree',
                'reason': 'Sort by registration date',
                'priority': 'medium'
            }
        ]
        
        return suggestions
    
    def analyze_unused_indexes(self) -> List[Dict[str, Any]]:
        """Identify potentially unused indexes."""
        unused_indexes = []
        
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    pg_size_pretty(pg_relation_size(indexrelid)) as size
                FROM pg_stat_user_indexes
                WHERE idx_scan = 0
                ORDER BY pg_relation_size(indexrelid) DESC
            """))
            
            for row in result:
                unused_indexes.append({
                    'table': row[1],
                    'index': row[2],
                    'scans': row[3],
                    'size': row[4]
                })
        
        return unused_indexes
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive analysis report."""
        print("Analyzing database indexes...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'existing_indexes': self.get_existing_indexes(),
            'table_statistics': self.get_table_statistics(),
            'index_usage_stats': self.get_index_usage_stats(),
            'slow_queries': self.get_slow_queries(),
            'suggested_indexes': self.suggest_indexes(),
            'unused_indexes': self.analyze_unused_indexes()
        }
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """Print a summary of the analysis."""
        print("\n" + "="*60)
        print("DATABASE INDEX ANALYSIS SUMMARY")
        print("="*60)
        
        # Table statistics
        print(f"\nTables analyzed: {len(report['table_statistics'])}")
        
        total_rows = sum(stats['row_count'] for stats in report['table_statistics'].values())
        print(f"Total rows: {total_rows:,}")
        
        # Index statistics
        total_indexes = sum(len(indexes) for indexes in report['existing_indexes'].values())
        print(f"Total indexes: {total_indexes}")
        
        # Unused indexes
        unused_count = len(report['unused_indexes'])
        print(f"Unused indexes: {unused_count}")
        
        if unused_count > 0:
            print("\nUnused indexes (consider removing):")
            for idx in report['unused_indexes'][:10]:  # Show top 10
                print(f"  - {idx['table']}.{idx['index']} ({idx['size']})")
        
        # Suggested indexes
        suggested_count = sum(len(suggestions) for suggestions in report['suggested_indexes'].values())
        print(f"\nSuggested indexes: {suggested_count}")
        
        # High priority suggestions
        high_priority = []
        for table, suggestions in report['suggested_indexes'].items():
            for suggestion in suggestions:
                if suggestion['priority'] == 'high':
                    high_priority.append(f"{table}({', '.join(suggestion['columns'])})")
        
        if high_priority:
            print("\nHigh priority index suggestions:")
            for suggestion in high_priority[:10]:  # Show top 10
                print(f"  - {suggestion}")
        
        # Slow queries
        slow_query_count = len(report['slow_queries'])
        print(f"\nSlow queries identified: {slow_query_count}")
        
        if slow_query_count > 0:
            print("\nTop slow queries:")
            for i, query in enumerate(report['slow_queries'][:5], 1):
                print(f"  {i}. {query['mean_time']:.2f}ms - {query['query']}")
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save the analysis report to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"index_analysis_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\nDetailed report saved to: {filename}")


def main():
    """Main function to run the index analysis."""
    try:
        # Get database URL from config
        config = Config()
        database_url = config.get_database_url()
        
        if not database_url:
            print("Error: Database URL not configured")
            sys.exit(1)
        
        # Create analyzer
        analyzer = IndexAnalyzer(database_url)
        
        # Generate report
        report = analyzer.generate_report()
        
        # Print summary
        analyzer.print_summary(report)
        
        # Save detailed report
        analyzer.save_report(report)
        
        print("\nIndex analysis completed successfully!")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
