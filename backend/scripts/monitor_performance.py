#!/usr/bin/env python3
"""
Database Performance Monitoring Script

This script monitors database performance metrics including query execution times,
index usage, and resource utilization.
"""

import os
import sys
import time
import json
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import Config


class PerformanceMonitor:
    """Monitors database performance metrics."""
    
    def __init__(self, database_url: str):
        """Initialize the performance monitor."""
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query execution statistics."""
        with self.engine.connect() as conn:
            # Get query statistics
            result = conn.execute(text("""
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows,
                    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
                FROM pg_stat_statements
                ORDER BY mean_time DESC
                LIMIT 20
            """))
            
            slow_queries = []
            for row in result:
                slow_queries.append({
                    'query': row[0][:200] + '...' if len(row[0]) > 200 else row[0],
                    'calls': row[1],
                    'total_time': float(row[2]),
                    'mean_time': float(row[3]),
                    'rows': row[4],
                    'hit_percent': float(row[5]) if row[5] else 0.0
                })
            
            # Get overall query stats
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_queries,
                    SUM(calls) as total_calls,
                    AVG(mean_time) as avg_execution_time,
                    MAX(mean_time) as max_execution_time
                FROM pg_stat_statements
            """))
            
            overall_stats = result.fetchone()
            
            return {
                'slow_queries': slow_queries,
                'total_queries': overall_stats[0],
                'total_calls': overall_stats[1],
                'avg_execution_time': float(overall_stats[2]) if overall_stats[2] else 0.0,
                'max_execution_time': float(overall_stats[3]) if overall_stats[3] else 0.0
            }
    
    def get_index_usage_stats(self) -> Dict[str, Any]:
        """Get index usage statistics."""
        with self.engine.connect() as conn:
            # Get index usage statistics
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
            
            index_stats = []
            for row in result:
                index_stats.append({
                    'table': row[1],
                    'index': row[2],
                    'scans': row[3],
                    'tuples_read': row[4],
                    'tuples_fetched': row[5],
                    'efficiency': float(row[6]) if row[6] else 0.0
                })
            
            # Get unused indexes
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
            
            unused_indexes = []
            for row in result:
                unused_indexes.append({
                    'table': row[1],
                    'index': row[2],
                    'scans': row[3],
                    'size': row[4]
                })
            
            return {
                'index_stats': index_stats,
                'unused_indexes': unused_indexes,
                'total_indexes': len(index_stats),
                'unused_count': len(unused_indexes)
            }
    
    def get_table_stats(self) -> Dict[str, Any]:
        """Get table statistics."""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    n_live_tup as live_tuples,
                    n_dead_tup as dead_tuples,
                    last_vacuum,
                    last_autovacuum,
                    last_analyze,
                    last_autoanalyze
                FROM pg_stat_user_tables
                ORDER BY n_live_tup DESC
            """))
            
            table_stats = []
            for row in result:
                table_stats.append({
                    'table': row[1],
                    'inserts': row[2],
                    'updates': row[3],
                    'deletes': row[4],
                    'live_tuples': row[5],
                    'dead_tuples': row[6],
                    'last_vacuum': row[7].isoformat() if row[7] else None,
                    'last_autovacuum': row[8].isoformat() if row[8] else None,
                    'last_analyze': row[9].isoformat() if row[9] else None,
                    'last_autoanalyze': row[10].isoformat() if row[10] else None
                })
            
            return {
                'table_stats': table_stats,
                'total_tables': len(table_stats)
            }
    
    def get_database_size(self) -> Dict[str, Any]:
        """Get database size information."""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    pg_database_size(current_database()) as database_size,
                    pg_size_pretty(pg_database_size(current_database())) as database_size_pretty
            """))
            
            size_info = result.fetchone()
            
            # Get table sizes
            result = conn.execute(text("""
                SELECT 
                    tablename,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size_pretty
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                LIMIT 20
            """))
            
            table_sizes = []
            for row in result:
                table_sizes.append({
                    'table': row[0],
                    'size_bytes': row[1],
                    'size_pretty': row[2]
                })
            
            return {
                'database_size_bytes': size_info[0],
                'database_size_pretty': size_info[1],
                'table_sizes': table_sizes
            }
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get database connection statistics."""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    numbackends as active_connections,
                    xact_commit as committed_transactions,
                    xact_rollback as rolled_back_transactions,
                    blks_read as blocks_read,
                    blks_hit as blocks_hit,
                    tup_returned as tuples_returned,
                    tup_fetched as tuples_fetched,
                    tup_inserted as tuples_inserted,
                    tup_updated as tuples_updated,
                    tup_deleted as tuples_deleted
                FROM pg_stat_database
                WHERE datname = current_database()
            """))
            
            stats = result.fetchone()
            
            # Calculate hit ratio
            blocks_read = stats[3]
            blocks_hit = stats[4]
            total_blocks = blocks_read + blocks_hit
            hit_ratio = (blocks_hit / total_blocks * 100) if total_blocks > 0 else 0
            
            return {
                'active_connections': stats[0],
                'committed_transactions': stats[1],
                'rolled_back_transactions': stats[2],
                'blocks_read': blocks_read,
                'blocks_hit': blocks_hit,
                'hit_ratio': hit_ratio,
                'tuples_returned': stats[5],
                'tuples_fetched': stats[6],
                'tuples_inserted': stats[7],
                'tuples_updated': stats[8],
                'tuples_deleted': stats[9]
            }
    
    def get_system_resources(self) -> Dict[str, Any]:
        """Get system resource utilization."""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_available_gb': psutil.virtual_memory().available / (1024**3),
            'disk_usage_percent': psutil.disk_usage('/').percent,
            'disk_free_gb': psutil.disk_usage('/').free / (1024**3)
        }
    
    def get_locks_info(self) -> Dict[str, Any]:
        """Get database lock information."""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    mode,
                    COUNT(*) as count
                FROM pg_locks
                GROUP BY mode
                ORDER BY count DESC
            """))
            
            locks = []
            for row in result:
                locks.append({
                    'mode': row[0],
                    'count': row[1]
                })
            
            # Get blocked queries
            result = conn.execute(text("""
                SELECT 
                    blocked_locks.pid AS blocked_pid,
                    blocked_activity.usename AS blocked_user,
                    blocking_locks.pid AS blocking_pid,
                    blocking_activity.usename AS blocking_user,
                    blocked_activity.query AS blocked_statement,
                    blocking_activity.query AS current_statement_in_blocking_process
                FROM pg_catalog.pg_locks blocked_locks
                JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
                JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
                    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
                    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
                    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
                    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
                    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
                    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
                    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
                    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
                    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
                    AND blocking_locks.pid != blocked_locks.pid
                JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
                WHERE NOT blocked_locks.granted
            """))
            
            blocked_queries = []
            for row in result:
                blocked_queries.append({
                    'blocked_pid': row[0],
                    'blocked_user': row[1],
                    'blocking_pid': row[2],
                    'blocking_user': row[3],
                    'blocked_statement': row[4][:200] + '...' if len(row[4]) > 200 else row[4],
                    'blocking_statement': row[5][:200] + '...' if len(row[5]) > 200 else row[5]
                })
            
            return {
                'locks': locks,
                'blocked_queries': blocked_queries,
                'total_locks': sum(lock['count'] for lock in locks),
                'blocked_count': len(blocked_queries)
            }
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        print("Generating performance report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'query_stats': self.get_query_stats(),
            'index_usage': self.get_index_usage_stats(),
            'table_stats': self.get_table_stats(),
            'database_size': self.get_database_size(),
            'connection_stats': self.get_connection_stats(),
            'system_resources': self.get_system_resources(),
            'locks_info': self.get_locks_info()
        }
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """Print a summary of the performance report."""
        print("\n" + "="*60)
        print("DATABASE PERFORMANCE SUMMARY")
        print("="*60)
        
        # Query performance
        query_stats = report['query_stats']
        print(f"\nQuery Performance:")
        print(f"  Total queries: {query_stats['total_queries']}")
        print(f"  Total calls: {query_stats['total_calls']:,}")
        print(f"  Average execution time: {query_stats['avg_execution_time']:.2f}ms")
        print(f"  Max execution time: {query_stats['max_execution_time']:.2f}ms")
        
        # Slow queries
        slow_queries = query_stats['slow_queries']
        if slow_queries:
            print(f"\nTop 5 slow queries:")
            for i, query in enumerate(slow_queries[:5], 1):
                print(f"  {i}. {query['mean_time']:.2f}ms - {query['calls']} calls")
                print(f"     {query['query']}")
        
        # Index usage
        index_usage = report['index_usage']
        print(f"\nIndex Usage:")
        print(f"  Total indexes: {index_usage['total_indexes']}")
        print(f"  Unused indexes: {index_usage['unused_count']}")
        
        if index_usage['unused_indexes']:
            print(f"\nUnused indexes (consider removing):")
            for idx in index_usage['unused_indexes'][:5]:
                print(f"  - {idx['table']}.{idx['index']} ({idx['size']})")
        
        # Database size
        db_size = report['database_size']
        print(f"\nDatabase Size:")
        print(f"  Total size: {db_size['database_size_pretty']}")
        
        if db_size['table_sizes']:
            print(f"\nLargest tables:")
            for table in db_size['table_sizes'][:5]:
                print(f"  - {table['table']}: {table['size_pretty']}")
        
        # Connection stats
        conn_stats = report['connection_stats']
        print(f"\nConnection Statistics:")
        print(f"  Active connections: {conn_stats['active_connections']}")
        print(f"  Cache hit ratio: {conn_stats['hit_ratio']:.2f}%")
        print(f"  Committed transactions: {conn_stats['committed_transactions']:,}")
        print(f"  Rolled back transactions: {conn_stats['rolled_back_transactions']:,}")
        
        # System resources
        sys_resources = report['system_resources']
        print(f"\nSystem Resources:")
        print(f"  CPU usage: {sys_resources['cpu_percent']:.1f}%")
        print(f"  Memory usage: {sys_resources['memory_percent']:.1f}%")
        print(f"  Memory available: {sys_resources['memory_available_gb']:.1f} GB")
        print(f"  Disk usage: {sys_resources['disk_usage_percent']:.1f}%")
        print(f"  Disk free: {sys_resources['disk_free_gb']:.1f} GB")
        
        # Locks
        locks_info = report['locks_info']
        print(f"\nLock Information:")
        print(f"  Total locks: {locks_info['total_locks']}")
        print(f"  Blocked queries: {locks_info['blocked_count']}")
        
        if locks_info['blocked_queries']:
            print(f"\nBlocked queries:")
            for blocked in locks_info['blocked_queries'][:3]:
                print(f"  - PID {blocked['blocked_pid']} blocked by PID {blocked['blocking_pid']}")
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save the performance report to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\nDetailed report saved to: {filename}")
    
    def monitor_continuously(self, interval: int = 60, duration: int = 3600):
        """Monitor performance continuously for a specified duration."""
        print(f"Starting continuous monitoring for {duration} seconds...")
        print(f"Sampling every {interval} seconds")
        
        start_time = time.time()
        reports = []
        
        try:
            while time.time() - start_time < duration:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Collecting metrics...")
                
                report = self.generate_performance_report()
                reports.append(report)
                
                # Print brief summary
                query_stats = report['query_stats']
                conn_stats = report['connection_stats']
                sys_resources = report['system_resources']
                
                print(f"  Queries: {query_stats['total_queries']}, "
                      f"Avg time: {query_stats['avg_execution_time']:.2f}ms, "
                      f"Connections: {conn_stats['active_connections']}, "
                      f"CPU: {sys_resources['cpu_percent']:.1f}%, "
                      f"Memory: {sys_resources['memory_percent']:.1f}%")
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        
        # Save all reports
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"continuous_monitoring_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(reports, f, indent=2, default=str)
        
        print(f"\nContinuous monitoring data saved to: {filename}")
        print(f"Collected {len(reports)} samples")


def main():
    """Main function to run the performance monitoring."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor database performance')
    parser.add_argument('--continuous', action='store_true',
                       help='Run continuous monitoring')
    parser.add_argument('--interval', type=int, default=60,
                       help='Sampling interval in seconds (default: 60)')
    parser.add_argument('--duration', type=int, default=3600,
                       help='Monitoring duration in seconds (default: 3600)')
    
    args = parser.parse_args()
    
    try:
        # Get database URL from config
        config = Config()
        database_url = config.get_database_url()
        
        if not database_url:
            print("Error: Database URL not configured")
            sys.exit(1)
        
        # Create monitor
        monitor = PerformanceMonitor(database_url)
        
        if args.continuous:
            monitor.monitor_continuously(args.interval, args.duration)
        else:
            # Generate single report
            report = monitor.generate_performance_report()
            monitor.print_summary(report)
            monitor.save_report(report)
        
    except Exception as e:
        print(f"Error during monitoring: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
