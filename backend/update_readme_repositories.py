#!/usr/bin/env python3
"""
Script to update all business logic README files with repository pattern information.
"""

import os
import re
from pathlib import Path

# Modules that have repositories
MODULES_WITH_REPOSITORIES = [
    'category', 'customers', 'expense', 'quotation', 'rating', 
    'transaction', 'company', 'branch', 'store'
]

# Repository information template
REPOSITORY_SECTION_TEMPLATE = """

## Repository Layer

The `{RepositoryName}Repository` class provides data access operations for the {ModuleName} module using the Repository pattern.

### Key Features
- **Base Repository**: Extends `BaseRepository[{ModelName}]` for common CRUD operations
- **Advanced Filtering**: Complex filtering, sorting, and pagination
- **Relationship Loading**: Eager loading of related entities
- **Type Safety**: Generic type support for better IDE support
- **Error Handling**: Consistent error handling across all operations

### Repository Methods

#### Basic CRUD Operations
- `get_by_id(entity_id)` - Get entity by ID
- `create(entity_data)` - Create new entity
- `update(entity_id, entity_data)` - Update existing entity
- `delete(entity_id)` - Delete entity
- `get_all(limit, offset)` - Get all entities with pagination

#### Advanced Query Methods
{AdvancedMethods}

#### Statistics and Analytics
- `get_{module_name}_statistics()` - Statistics for dashboard/reporting

### Usage Example

```python
from app.{module_name}.repository import {RepositoryName}Repository

# Initialize repository
{module_name}_repo = {RepositoryName}Repository()

# Get entity by ID
entity = {module_name}_repo.get_by_id("entity-uuid")

# Get entities with filtering
filter_obj = FilterObj()
result = {module_name}_repo.get_paginated(filter_obj)

# Create new entity
new_entity = {module_name}_repo.create(entity_data)

# Update entity
{module_name}_repo.update("entity-uuid", update_data)

# Get statistics
stats = {module_name}_repo.get_{module_name}_statistics()
```

"""

# Module-specific repository methods
REPOSITORY_METHODS = {
    'category': [
        '- `get_categories_with_children()` - Categories with subcategories',
        '- `get_category_with_details(category_id)` - Category with all related details',
        '- `get_root_categories()` - Root categories only',
        '- `get_subcategories(parent_id)` - Subcategories of parent',
        '- `get_categories_by_type(category_type)` - Categories by type',
        '- `get_active_categories()` - Active categories only',
        '- `get_featured_categories()` - Featured categories',
        '- `get_category_by_slug(slug)` - Category by URL slug',
        '- `get_category_by_code(code)` - Category by code',
        '- `get_categories_with_products()` - Categories that have products',
        '- `get_category_hierarchy()` - Complete category hierarchy',
        '- `get_categories_by_commission_rate(min_rate, max_rate)` - Categories by commission rate'
    ],
    'customers': [
        '- `get_customer_by_user_id(user_id)` - Customer by associated user',
        '- `get_customer_by_email(email)` - Customer by email address',
        '- `get_customer_by_mobile(mobile)` - Customer by mobile number',
        '- `get_customer_by_code(customer_code)` - Customer by code',
        '- `get_customers_by_type(customer_type)` - Customers by type',
        '- `get_active_customers()` - Active customers only',
        '- `get_verified_customers()` - Verified customers',
        '- `get_customers_by_city(city)` - Customers by city',
        '- `get_customers_by_country(country)` - Customers by country',
        '- `get_business_customers()` - Business customers only',
        '- `search_customers(search_term)` - Search customers',
        '- `get_customers_by_registration_date(start_date, end_date)` - Customers by registration date',
        '- `get_recent_customers(limit)` - Recent customers',
        '- `verify_customer(customer_id)` - Verify customer account',
        '- `update_customer_status(customer_id, status)` - Update customer status'
    ],
    'expense': [
        '- `get_expenses_with_category(filter_obj)` - Expenses with category information',
        '- `get_expenses_by_category(category_id)` - Expenses by category',
        '- `get_expenses_by_status(status)` - Expenses by status',
        '- `get_expenses_by_date_range(start_date, end_date)` - Expenses by date range',
        '- `get_expenses_by_amount_range(min_amount, max_amount)` - Expenses by amount range',
        '- `get_expenses_by_fiscal_year(fiscal_year_id)` - Expenses by fiscal year',
        '- `get_pending_expenses()` - Pending expenses',
        '- `get_approved_expenses()` - Approved expenses',
        '- `get_rejected_expenses()` - Rejected expenses',
        '- `update_expense_status(expense_id, new_status)` - Update expense status',
        '- `get_expenses_by_category_summary()` - Expense summary by category'
    ],
    'quotation': [
        '- `get_quotations_with_details(filter_obj)` - Quotations with details',
        '- `get_quotation_by_number(number)` - Quotation by number',
        '- `get_quotations_by_customer(customer_id)` - Quotations by customer',
        '- `get_quotations_by_status(status)` - Quotations by status',
        '- `get_quotations_by_branch(branch_id)` - Quotations by branch',
        '- `get_quotations_by_user(user_id)` - Quotations by user',
        '- `get_quotations_by_date_range(start_date, end_date)` - Quotations by date range',
        '- `get_quotations_by_amount_range(min_amount, max_amount)` - Quotations by amount range',
        '- `get_pending_quotations()` - Pending quotations',
        '- `get_approved_quotations()` - Approved quotations',
        '- `get_rejected_quotations()` - Rejected quotations',
        '- `update_quotation_status(quotation_id, new_status)` - Update quotation status'
    ],
    'rating': [
        '- `get_ratings_with_details(rating_id)` - Rating with all related details',
        '- `get_ratings_by_product(product_id)` - Ratings by product',
        '- `get_ratings_by_user(user_id)` - Ratings by user',
        '- `get_ratings_by_score(score)` - Ratings by score',
        '- `get_ratings_by_score_range(min_score, max_score)` - Ratings by score range',
        '- `get_high_ratings(min_score)` - High ratings',
        '- `get_low_ratings(max_score)` - Low ratings',
        '- `get_average_rating_by_product(product_id)` - Average rating for product',
        '- `get_rating_count_by_product(product_id)` - Rating count for product',
        '- `get_rating_distribution_by_product(product_id)` - Rating distribution',
        '- `get_recent_ratings(limit)` - Recent ratings',
        '- `get_top_rated_products(limit, min_ratings)` - Top rated products',
        '- `get_user_rating_for_product(user_id, product_id)` - User rating for product',
        '- `update_rating(rating_id, new_score, new_comment)` - Update rating'
    ],
    'transaction': [
        '- `get_transactions_with_details(transaction_id)` - Transaction with all related details',
        '- `get_transactions_by_product(product_id)` - Transactions by product',
        '- `get_transactions_by_type(transaction_type)` - Transactions by type',
        '- `get_transactions_by_location(location_id, location_type)` - Transactions by location',
        '- `get_transactions_by_fiscal_year(fiscal_year_id)` - Transactions by fiscal year',
        '- `get_transactions_by_date_range(start_date, end_date)` - Transactions by date range',
        '- `get_transactions_by_quantity_range(min_quantity, max_quantity)` - Transactions by quantity range',
        '- `get_recent_transactions(limit)` - Recent transactions',
        '- `get_product_movement_summary(product_id)` - Product movement summary',
        '- `get_location_movement_summary(location_id, location_type)` - Location movement summary'
    ],
    'company': [
        '- `get_company_by_name(name)` - Company by name',
        '- `get_company_by_code(code)` - Company by code',
        '- `get_active_companies()` - Active companies only',
        '- `search_companies(search_term)` - Search companies'
    ],
    'branch': [
        '- `get_branch_by_location(location)` - Branch by location',
        '- `get_branch_by_manager(manager)` - Branch by manager',
        '- `search_branches(search_term)` - Search branches'
    ],
    'store': [
        '- `get_store_by_location(location)` - Store by location',
        '- `get_store_by_manager(manager)` - Store by manager',
        '- `search_stores(search_term)` - Search stores'
    ]
}

def update_readme_file(module_name, readme_path):
    """Update a single README file with repository information."""
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if repository section already exists
        if '## Repository Layer' in content:
            print(f"  ✓ {module_name}/README.md already has repository section")
            return
        
        # Find the module structure section and update it
        structure_pattern = r'```\n([^`]+)\n├── __init__\.py.*\n├── model\.py.*\n├── routes\.py.*\n├── service\.py.*\n├── schemas\.py.*\n├── swagger\.yaml.*\n└── README\.md.*\n```'
        
        def update_structure(match):
            structure = match.group(1)
            if 'repository.py' not in structure:
                # Add repository.py line after service.py
                structure = structure.replace(
                    '├── service.py          # Business logic layer\n├── schemas.py',
                    '├── service.py          # Business logic layer\n├── repository.py       # Data access layer (Repository pattern)\n├── schemas.py'
                )
            return f'```\n{structure}```'
        
        content = re.sub(structure_pattern, update_structure, content, flags=re.MULTILINE | re.DOTALL)
        
        # Find where to insert the repository section (after models, before API endpoints)
        api_endpoints_pattern = r'## API Endpoints'
        if api_endpoints_pattern in content:
            # Insert repository section before API endpoints
            repository_name = f"{module_name.title()}Repository"
            model_name = module_name.title()
            advanced_methods = '\n'.join(REPOSITORY_METHODS.get(module_name, []))
            
            repository_section = REPOSITORY_SECTION_TEMPLATE.format(
                RepositoryName=repository_name,
                ModuleName=module_name.title(),
                ModelName=model_name,
                module_name=module_name,
                AdvancedMethods=advanced_methods
            )
            
            content = content.replace(api_endpoints_pattern, repository_section + '\n' + api_endpoints_pattern)
            
            # Write the updated content
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✓ Updated {module_name}/README.md with repository information")
        else:
            print(f"  ⚠ {module_name}/README.md doesn't have API Endpoints section, skipping")
            
    except Exception as e:
        print(f"  ✗ Error updating {module_name}/README.md: {e}")

def main():
    """Update all README files with repository information."""
    base_path = Path('/Users/mazin/Documents/GitHub/3D-Store/backend/app')
    
    print("Updating business logic README files with repository information...")
    print()
    
    for module_name in MODULES_WITH_REPOSITORIES:
        readme_path = base_path / module_name / 'README.md'
        
        if readme_path.exists():
            print(f"Processing {module_name}...")
            update_readme_file(module_name, readme_path)
        else:
            print(f"  ⚠ {module_name}/README.md not found, skipping")
        print()
    
    print("Repository documentation update completed!")

if __name__ == "__main__":
    main()
