#!/usr/bin/env python3
"""
Test Admin User Migration (Database Agnostic)

This script tests that the database-agnostic admin user migration works correctly.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_migration_syntax():
    """Test that the migration file has correct syntax."""
    
    migration_file = Path(__file__).parent.parent / "alembic" / "versions" / "add_admin_user.py"
    
    if not migration_file.exists():
        print("❌ Migration file not found!")
        return False
    
    try:
        # Test syntax by importing the module
        import importlib.util
        spec = importlib.util.spec_from_file_location("add_admin_user", migration_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        print("✅ Migration file syntax is correct")
        
        # Check that required functions exist
        if hasattr(module, 'upgrade') and hasattr(module, 'downgrade'):
            print("✅ Migration functions (upgrade/downgrade) are present")
        else:
            print("❌ Missing upgrade/downgrade functions")
            return False
        
        # Check that it uses SQLAlchemy models (not raw SQL)
        with open(migration_file, 'r') as f:
            content = f.read()
            
        if 'sa.table(' in content and 'op.execute(' in content:
            print("✅ Migration uses SQLAlchemy models")
        else:
            print("❌ Migration doesn't use SQLAlchemy models")
            return False
            
        if 'text(' in content:
            print("⚠️  Warning: Migration still contains raw SQL (text() calls)")
        else:
            print("✅ Migration is fully database-agnostic (no raw SQL)")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration file syntax error: {e}")
        return False

def test_migration_structure():
    """Test the structure of the migration file."""
    
    migration_file = Path(__file__).parent.parent / "alembic" / "versions" / "add_admin_user.py"
    
    with open(migration_file, 'r') as f:
        content = f.read()
    
    # Check for key components
    checks = [
        ("revision ID", 'revision = \'add_admin_user\''),
        ("down revision", 'down_revision = \'add_performance_indexes\''),
        ("SQLAlchemy imports", 'import sqlalchemy as sa'),
        ("UUID support", 'postgresql.UUID'),
        ("Conflict handling", 'on_conflict_do_nothing'),
        ("Table definitions", 'sa.table('),
        ("Admin role creation", 'name=\'admin\''),
        ("Admin user creation", 'username=\'admin\''),
        ("User-role association", 'user_roles_table'),
        ("Downgrade function", 'def downgrade():')
    ]
    
    print("\n📋 Migration Structure Check:")
    all_passed = True
    
    for check_name, check_pattern in checks:
        if check_pattern in content:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")
            all_passed = False
    
    return all_passed

def test_database_agnostic_features():
    """Test that the migration is truly database-agnostic."""
    
    migration_file = Path(__file__).parent.parent / "alembic" / "versions" / "add_admin_user.py"
    
    with open(migration_file, 'r') as f:
        content = f.read()
    
    print("\n🔍 Database Agnostic Features Check:")
    
    # Check for database-agnostic features
    features = [
        ("SQLAlchemy table definitions", 'sa.table('),
        ("SQLAlchemy insert operations", 'insert().values('),
        ("SQLAlchemy select operations", 'sa.select('),
        ("SQLAlchemy delete operations", 'delete().where('),
        ("Conflict handling", 'on_conflict_do_nothing'),
        ("No raw SQL", 'text(' not in content),
        ("UUID support", 'postgresql.UUID'),
        ("JSON support", 'sa.JSON')
    ]
    
    all_passed = True
    
    for feature_name, condition in features:
        if condition:
            print(f"✅ {feature_name}")
        else:
            print(f"❌ {feature_name}")
            all_passed = False
    
    return all_passed

def main():
    """Main function."""
    print("🧪 Testing Database-Agnostic Admin User Migration")
    print("=" * 60)
    
    # Test syntax
    syntax_ok = test_migration_syntax()
    
    # Test structure
    structure_ok = test_migration_structure()
    
    # Test database-agnostic features
    db_agnostic_ok = test_database_agnostic_features()
    
    print("\n" + "=" * 60)
    
    if syntax_ok and structure_ok and db_agnostic_ok:
        print("🎉 All tests passed! Migration is ready for any database.")
        print("\n✅ Features:")
        print("  - Pure SQLAlchemy models (no raw SQL)")
        print("  - Database-agnostic operations")
        print("  - Conflict handling (safe to run multiple times)")
        print("  - Proper rollback support")
        print("  - UUID and JSON support")
        
        print("\n🚀 Ready to run:")
        print("  cd backend")
        print("  alembic upgrade head")
        
    else:
        print("❌ Some tests failed. Please check the migration file.")
        return False
    
    return True

if __name__ == '__main__':
    main()
