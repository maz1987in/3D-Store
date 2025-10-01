"""Add performance indexes

Revision ID: add_performance_indexes
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_performance_indexes'
down_revision = '2dea99c6ac9d'  # Update this to the latest revision
branch_labels = None
depends_on = None


def upgrade():
    """Add performance indexes for database optimization."""
    
    # User table indexes
    op.create_index('idx_users_active', 'users', ['active'])
    op.create_index('idx_users_user_type', 'users', ['user_type'])
    op.create_index('idx_users_language', 'users', ['language'])
    op.create_index('idx_users_create_date', 'users', ['create_date'])
    op.create_index('idx_users_modified_date', 'users', ['modified_date'])
    op.create_index('idx_users_phone_email', 'users', ['phone', 'email'])
    op.create_index('idx_users_active_type', 'users', ['active', 'user_type'])
    
    # Product table indexes
    op.create_index('idx_product_type', 'product', ['product_type'])
    op.create_index('idx_product_category_type', 'product', ['category_id', 'product_type'])
    op.create_index('idx_product_price', 'product', ['base_price'])
    op.create_index('idx_product_currency', 'product', ['currency'])
    op.create_index('idx_product_dynamic_pricing', 'product', ['is_dynamic_pricing'])
    op.create_index('idx_product_category_price', 'product', ['category_id', 'base_price'])
    op.create_index('idx_product_type_price', 'product', ['product_type', 'base_price'])
    op.create_index('idx_product_sku', 'product', ['sku'])
    op.create_index('idx_product_subcategory', 'product', ['subcategory_id'])
    
    # Category table indexes
    op.create_index('idx_category_parent', 'category', ['parent_id'])
    op.create_index('idx_category_active', 'category', ['is_active'])
    op.create_index('idx_category_featured', 'category', ['is_featured'])
    op.create_index('idx_category_active_featured', 'category', ['is_active', 'is_featured'])
    op.create_index('idx_category_slug', 'category', ['slug'])
    op.create_index('idx_category_parent_active', 'category', ['parent_id', 'is_active'])
    
    # Customer table indexes
    op.create_index('idx_customer_user_id', 'customer', ['user_id'])
    op.create_index('idx_customer_mobile', 'customer', ['mobile'])
    op.create_index('idx_customer_phone', 'customer', ['phone'])
    op.create_index('idx_customer_city', 'customer', ['city'])
    op.create_index('idx_customer_country', 'customer', ['country'])
    op.create_index('idx_customer_customer_type', 'customer', ['customer_type'])
    op.create_index('idx_customer_status', 'customer', ['status'])
    op.create_index('idx_customer_create_date', 'customer', ['create_date'])
    op.create_index('idx_customer_modified_date', 'customer', ['modified_date'])
    op.create_index('idx_customer_user_status', 'customer', ['user_id', 'status'])
    
    # Order table indexes
    op.create_index('idx_order_customer', 'order', ['customer_id'])
    op.create_index('idx_order_status', 'order', ['status'])
    op.create_index('idx_order_type', 'order', ['order_type'])
    op.create_index('idx_order_priority', 'order', ['priority'])
    op.create_index('idx_order_payment_status', 'order', ['payment_status'])
    op.create_index('idx_order_payment_method', 'order', ['payment_method'])
    op.create_index('idx_order_expected_delivery', 'order', ['expected_delivery'])
    op.create_index('idx_order_estimated_completion', 'order', ['estimated_completion'])
    op.create_index('idx_order_currency', 'order', ['currency'])
    op.create_index('idx_order_customer_status', 'order', ['customer_id', 'status'])
    op.create_index('idx_order_status_date', 'order', ['status', 'order_date'])
    op.create_index('idx_order_customer_date', 'order', ['customer_id', 'order_date'])
    op.create_index('idx_order_type_status', 'order', ['order_type', 'status'])
    op.create_index('idx_order_payment_status_date', 'order', ['payment_status', 'order_date'])
    op.create_index('idx_order_total_amount', 'order', ['total_amount'])
    op.create_index('idx_order_priority_status', 'order', ['priority', 'status'])
    
    # Order Item table indexes
    op.create_index('idx_order_item_order', 'order_item', ['order_id'])
    op.create_index('idx_order_item_product', 'order_item', ['product_id'])
    op.create_index('idx_order_item_order_product', 'order_item', ['order_id', 'product_id'])
    
    # Inventory table indexes
    op.create_index('idx_inventory_product_branch', 'inventory', ['product_id', 'branch_id'])
    op.create_index('idx_inventory_branch_store', 'inventory', ['branch_id', 'store_id'])
    op.create_index('idx_inventory_quantity', 'inventory', ['quantity'])
    op.create_index('idx_inventory_quantity_alert', 'inventory', ['quantity_alert'])
    op.create_index('idx_inventory_product_quantity', 'inventory', ['product_id', 'quantity'])
    op.create_index('idx_inventory_branch_quantity', 'inventory', ['branch_id', 'quantity'])
    op.create_index('idx_inventory_store_quantity', 'inventory', ['store_id', 'quantity'])
    op.create_index('idx_inventory_create_date', 'inventory', ['create_date'])
    op.create_index('idx_inventory_modified_date', 'inventory', ['modified_date'])
    
    # Transaction table indexes
    op.create_index('idx_transaction_product', 'transaction', ['product_id'])
    op.create_index('idx_transaction_type', 'transaction', ['transaction_type'])
    op.create_index('idx_transaction_date', 'transaction', ['transaction_date'])
    op.create_index('idx_transaction_financial_year', 'transaction', ['financial_year_id'])
    op.create_index('idx_transaction_from_location', 'transaction', ['from_location_id'])
    op.create_index('idx_transaction_to_location', 'transaction', ['to_location_id'])
    op.create_index('idx_transaction_product_type', 'transaction', ['product_id', 'transaction_type'])
    op.create_index('idx_transaction_type_date', 'transaction', ['transaction_type', 'transaction_date'])
    op.create_index('idx_transaction_from_to', 'transaction', ['from_location_id', 'to_location_id'])
    op.create_index('idx_transaction_create_date', 'transaction', ['create_date'])
    op.create_index('idx_transaction_modified_date', 'transaction', ['modified_date'])
    
    # Payment Transaction table indexes
    op.create_index('idx_payment_transaction_reference', 'payment_transaction', ['reference_id'])
    op.create_index('idx_payment_transaction_status', 'payment_transaction', ['payment_status'])
    op.create_index('idx_payment_transaction_gateway', 'payment_transaction', ['gateway_transaction_id'])
    op.create_index('idx_payment_transaction_gateway_status', 'payment_transaction', ['gateway_status'])
    op.create_index('idx_payment_transaction_amount', 'payment_transaction', ['amount'])
    op.create_index('idx_payment_transaction_model', 'payment_transaction', ['model_type', 'model_id'])
    op.create_index('idx_payment_transaction_requester', 'payment_transaction', ['requester'])
    op.create_index('idx_payment_transaction_payment_gateway', 'payment_transaction', ['payment_gateway'])
    op.create_index('idx_payment_transaction_payment_type', 'payment_transaction', ['payment_type'])
    op.create_index('idx_payment_transaction_create_date', 'payment_transaction', ['create_date'])
    op.create_index('idx_payment_transaction_last_modified', 'payment_transaction', ['last_modified'])
    op.create_index('idx_payment_transaction_retry', 'payment_transaction', ['retry'])
    op.create_index('idx_payment_transaction_is_online', 'payment_transaction', ['is_online'])
    
    # Quotation table indexes
    op.create_index('idx_quotation_customer', 'quotation', ['customer_id'])
    op.create_index('idx_quotation_status', 'quotation', ['status'])
    op.create_index('idx_quotation_valid_until', 'quotation', ['valid_until'])
    op.create_index('idx_quotation_create_date', 'quotation', ['create_date'])
    op.create_index('idx_quotation_modified_date', 'quotation', ['modified_date'])
    op.create_index('idx_quotation_customer_status', 'quotation', ['customer_id', 'status'])
    op.create_index('idx_quotation_status_date', 'quotation', ['status', 'create_date'])
    op.create_index('idx_quotation_total_amount', 'quotation', ['total_amount'])
    op.create_index('idx_quotation_currency', 'quotation', ['currency'])
    
    # Invoice table indexes
    op.create_index('idx_invoice_customer', 'invoice', ['customer_id'])
    op.create_index('idx_invoice_order', 'invoice', ['order_id'])
    op.create_index('idx_invoice_status', 'invoice', ['status'])
    op.create_index('idx_invoice_due_date', 'invoice', ['due_date'])
    op.create_index('idx_invoice_create_date', 'invoice', ['create_date'])
    op.create_index('idx_invoice_modified_date', 'invoice', ['modified_date'])
    op.create_index('idx_invoice_customer_status', 'invoice', ['customer_id', 'status'])
    op.create_index('idx_invoice_status_date', 'invoice', ['status', 'create_date'])
    op.create_index('idx_invoice_total_amount', 'invoice', ['total_amount'])
    op.create_index('idx_invoice_currency', 'invoice', ['currency'])
    op.create_index('idx_invoice_invoice_number', 'invoice', ['invoice_number'])
    
    # Branch table indexes
    op.create_index('idx_branch_company', 'branch', ['company_id'])
    op.create_index('idx_branch_active', 'branch', ['is_active'])
    op.create_index('idx_branch_city', 'branch', ['city'])
    op.create_index('idx_branch_country', 'branch', ['country'])
    op.create_index('idx_branch_company_active', 'branch', ['company_id', 'is_active'])
    op.create_index('idx_branch_create_date', 'branch', ['create_date'])
    op.create_index('idx_branch_modified_date', 'branch', ['modified_date'])
    
    # Store table indexes
    op.create_index('idx_store_branch', 'store', ['branch_id'])
    op.create_index('idx_store_active', 'store', ['is_active'])
    op.create_index('idx_store_city', 'store', ['city'])
    op.create_index('idx_store_country', 'store', ['country'])
    op.create_index('idx_store_branch_active', 'store', ['branch_id', 'is_active'])
    op.create_index('idx_store_create_date', 'store', ['create_date'])
    op.create_index('idx_store_modified_date', 'store', ['modified_date'])
    
    # Company table indexes
    op.create_index('idx_company_active', 'company', ['is_active'])
    op.create_index('idx_company_country', 'company', ['country'])
    op.create_index('idx_company_create_date', 'company', ['create_date'])
    op.create_index('idx_company_modified_date', 'company', ['modified_date'])
    
    # Expense table indexes
    op.create_index('idx_expense_category', 'expense', ['category_id'])
    op.create_index('idx_expense_branch', 'expense', ['branch_id'])
    op.create_index('idx_expense_status', 'expense', ['status'])
    op.create_index('idx_expense_approver', 'expense', ['approved_by'])
    op.create_index('idx_expense_create_date', 'expense', ['create_date'])
    op.create_index('idx_expense_modified_date', 'expense', ['modified_date'])
    op.create_index('idx_expense_category_status', 'expense', ['category_id', 'status'])
    op.create_index('idx_expense_branch_status', 'expense', ['branch_id', 'status'])
    op.create_index('idx_expense_amount', 'expense', ['amount'])
    op.create_index('idx_expense_currency', 'expense', ['currency'])
    op.create_index('idx_expense_expense_date', 'expense', ['expense_date'])
    
    # Expense Category table indexes
    op.create_index('idx_expense_category_active', 'expense_category', ['is_active'])
    op.create_index('idx_expense_category_parent', 'expense_category', ['parent_id'])
    op.create_index('idx_expense_category_parent_active', 'expense_category', ['parent_id', 'is_active'])
    op.create_index('idx_expense_category_create_date', 'expense_category', ['create_date'])
    op.create_index('idx_expense_category_modified_date', 'expense_category', ['modified_date'])
    
    # Financial Year table indexes
    op.create_index('idx_fiscal_year_active', 'fiscal_year', ['is_active'])
    op.create_index('idx_fiscal_year_start_date', 'fiscal_year', ['start_date'])
    op.create_index('idx_fiscal_year_end_date', 'fiscal_year', ['end_date'])
    op.create_index('idx_fiscal_year_create_date', 'fiscal_year', ['create_date'])
    op.create_index('idx_fiscal_year_modified_date', 'fiscal_year', ['modified_date'])
    
    # Fiscal Period table indexes
    op.create_index('idx_fiscal_period_year', 'fiscal_period', ['fiscal_year_id'])
    op.create_index('idx_fiscal_period_start_date', 'fiscal_period', ['start_date'])
    op.create_index('idx_fiscal_period_end_date', 'fiscal_period', ['end_date'])
    op.create_index('idx_fiscal_period_create_date', 'fiscal_period', ['create_date'])
    op.create_index('idx_fiscal_period_modified_date', 'fiscal_period', ['modified_date'])
    op.create_index('idx_fiscal_period_year_start', 'fiscal_period', ['fiscal_year_id', 'start_date'])
    
    # Rating table indexes
    op.create_index('idx_rating_user', 'rating', ['user_id'])
    op.create_index('idx_rating_product', 'rating', ['product_id'])
    op.create_index('idx_rating_order', 'rating', ['order_id'])
    op.create_index('idx_rating_rating', 'rating', ['rating'])
    op.create_index('idx_rating_create_date', 'rating', ['create_date'])
    op.create_index('idx_rating_modified_date', 'rating', ['modified_date'])
    op.create_index('idx_rating_user_product', 'rating', ['user_id', 'product_id'])
    op.create_index('idx_rating_product_rating', 'rating', ['product_id', 'rating'])
    
    # Media table indexes
    op.create_index('idx_media_model_type', 'media', ['model_type'])
    op.create_index('idx_media_model_id', 'media', ['model_id'])
    op.create_index('idx_media_model', 'media', ['model_type', 'model_id'])
    op.create_index('idx_media_create_date', 'media', ['create_date'])
    op.create_index('idx_media_modified_date', 'media', ['modified_date'])
    op.create_index('idx_media_last_modified', 'media', ['last_modified'])
    
    # Shipping Address table indexes
    op.create_index('idx_shipping_address_customer', 'shipping_address', ['customer_id'])
    op.create_index('idx_shipping_address_city', 'shipping_address', ['city'])
    op.create_index('idx_shipping_address_country', 'shipping_address', ['country'])
    op.create_index('idx_shipping_address_postal_code', 'shipping_address', ['postal_code'])
    op.create_index('idx_shipping_address_is_default', 'shipping_address', ['is_default'])
    op.create_index('idx_shipping_address_customer_default', 'shipping_address', ['customer_id', 'is_default'])
    op.create_index('idx_shipping_address_create_date', 'shipping_address', ['create_date'])
    op.create_index('idx_shipping_address_modified_date', 'shipping_address', ['modified_date'])
    
    # Staff table indexes
    op.create_index('idx_staff_user', 'staff', ['user_id'])
    op.create_index('idx_staff_branch', 'staff', ['branch_id'])
    op.create_index('idx_staff_department', 'staff', ['department'])
    op.create_index('idx_staff_position', 'staff', ['position'])
    op.create_index('idx_staff_active', 'staff', ['is_active'])
    op.create_index('idx_staff_branch_active', 'staff', ['branch_id', 'is_active'])
    op.create_index('idx_staff_create_date', 'staff', ['create_date'])
    op.create_index('idx_staff_modified_date', 'staff', ['modified_date'])
    
    # Role table indexes
    op.create_index('idx_role_active', 'role', ['is_active'])
    op.create_index('idx_role_create_date', 'role', ['create_date'])
    op.create_index('idx_role_modified_date', 'role', ['modified_date'])
    
    # Permission table indexes
    op.create_index('idx_permission_resource', 'permission', ['resource'])
    op.create_index('idx_permission_action', 'permission', ['action'])
    op.create_index('idx_permission_resource_action', 'permission', ['resource', 'action'])
    op.create_index('idx_permission_create_date', 'permission', ['create_date'])
    op.create_index('idx_permission_modified_date', 'permission', ['modified_date'])
    
    # User Roles table indexes
    op.create_index('idx_user_roles_user', 'user_roles', ['user_id'])
    op.create_index('idx_user_roles_role', 'user_roles', ['role_id'])
    op.create_index('idx_user_roles_user_role', 'user_roles', ['user_id', 'role_id'])
    
    # Role Permissions table indexes
    op.create_index('idx_role_permissions_role', 'role_permissions', ['role_id'])
    op.create_index('idx_role_permissions_permission', 'role_permissions', ['permission_id'])
    op.create_index('idx_role_permissions_role_permission', 'role_permissions', ['role_id', 'permission_id'])
    
    # Tracking table indexes
    op.create_index('idx_tracking_user', 'tracking', ['user_id'])
    op.create_index('idx_tracking_action', 'tracking', ['action'])
    op.create_index('idx_tracking_model_type', 'tracking', ['model_type'])
    op.create_index('idx_tracking_model_id', 'tracking', ['model_id'])
    op.create_index('idx_tracking_model', 'tracking', ['model_type', 'model_id'])
    op.create_index('idx_tracking_create_date', 'tracking', ['create_date'])
    op.create_index('idx_tracking_user_action', 'tracking', ['user_id', 'action'])
    op.create_index('idx_tracking_action_date', 'tracking', ['action', 'create_date'])
    
    # Print Job table indexes (if exists)
    try:
        op.create_index('idx_print_job_order', 'print_job', ['order_id'])
        op.create_index('idx_print_job_status', 'print_job', ['status'])
        op.create_index('idx_print_job_priority', 'print_job', ['priority'])
        op.create_index('idx_print_job_create_date', 'print_job', ['create_date'])
        op.create_index('idx_print_job_modified_date', 'print_job', ['modified_date'])
        op.create_index('idx_print_job_status_priority', 'print_job', ['status', 'priority'])
        op.create_index('idx_print_job_order_status', 'print_job', ['order_id', 'status'])
    except Exception:
        # Print job table might not exist yet
        pass
    
    # Supplier table indexes (if exists)
    try:
        op.create_index('idx_supplier_active', 'supplier', ['is_active'])
        op.create_index('idx_supplier_country', 'supplier', ['country'])
        op.create_index('idx_supplier_city', 'supplier', ['city'])
        op.create_index('idx_supplier_create_date', 'supplier', ['create_date'])
        op.create_index('idx_supplier_modified_date', 'supplier', ['modified_date'])
    except Exception:
        # Supplier table might not exist yet
        pass


def downgrade():
    """Remove performance indexes."""
    
    # User table indexes
    op.drop_index('idx_users_active', 'users')
    op.drop_index('idx_users_user_type', 'users')
    op.drop_index('idx_users_language', 'users')
    op.drop_index('idx_users_create_date', 'users')
    op.drop_index('idx_users_modified_date', 'users')
    op.drop_index('idx_users_phone_email', 'users')
    op.drop_index('idx_users_active_type', 'users')
    
    # Product table indexes
    op.drop_index('idx_product_type', 'product')
    op.drop_index('idx_product_category_type', 'product')
    op.drop_index('idx_product_price', 'product')
    op.drop_index('idx_product_currency', 'product')
    op.drop_index('idx_product_dynamic_pricing', 'product')
    op.drop_index('idx_product_category_price', 'product')
    op.drop_index('idx_product_type_price', 'product')
    op.drop_index('idx_product_sku', 'product')
    op.drop_index('idx_product_subcategory', 'product')
    
    # Category table indexes
    op.drop_index('idx_category_parent', 'category')
    op.drop_index('idx_category_active', 'category')
    op.drop_index('idx_category_featured', 'category')
    op.drop_index('idx_category_active_featured', 'category')
    op.drop_index('idx_category_slug', 'category')
    op.drop_index('idx_category_parent_active', 'category')
    
    # Customer table indexes
    op.drop_index('idx_customer_user_id', 'customer')
    op.drop_index('idx_customer_mobile', 'customer')
    op.drop_index('idx_customer_phone', 'customer')
    op.drop_index('idx_customer_city', 'customer')
    op.drop_index('idx_customer_country', 'customer')
    op.drop_index('idx_customer_customer_type', 'customer')
    op.drop_index('idx_customer_status', 'customer')
    op.drop_index('idx_customer_create_date', 'customer')
    op.drop_index('idx_customer_modified_date', 'customer')
    op.drop_index('idx_customer_user_status', 'customer')
    
    # Order table indexes
    op.drop_index('idx_order_customer', 'order')
    op.drop_index('idx_order_status', 'order')
    op.drop_index('idx_order_type', 'order')
    op.drop_index('idx_order_priority', 'order')
    op.drop_index('idx_order_payment_status', 'order')
    op.drop_index('idx_order_payment_method', 'order')
    op.drop_index('idx_order_expected_delivery', 'order')
    op.drop_index('idx_order_estimated_completion', 'order')
    op.drop_index('idx_order_currency', 'order')
    op.drop_index('idx_order_customer_status', 'order')
    op.drop_index('idx_order_status_date', 'order')
    op.drop_index('idx_order_customer_date', 'order')
    op.drop_index('idx_order_type_status', 'order')
    op.drop_index('idx_order_payment_status_date', 'order')
    op.drop_index('idx_order_total_amount', 'order')
    op.drop_index('idx_order_priority_status', 'order')
    
    # Order Item table indexes
    op.drop_index('idx_order_item_order', 'order_item')
    op.drop_index('idx_order_item_product', 'order_item')
    op.drop_index('idx_order_item_order_product', 'order_item')
    
    # Inventory table indexes
    op.drop_index('idx_inventory_product_branch', 'inventory')
    op.drop_index('idx_inventory_branch_store', 'inventory')
    op.drop_index('idx_inventory_quantity', 'inventory')
    op.drop_index('idx_inventory_quantity_alert', 'inventory')
    op.drop_index('idx_inventory_product_quantity', 'inventory')
    op.drop_index('idx_inventory_branch_quantity', 'inventory')
    op.drop_index('idx_inventory_store_quantity', 'inventory')
    op.drop_index('idx_inventory_create_date', 'inventory')
    op.drop_index('idx_inventory_modified_date', 'inventory')
    
    # Transaction table indexes
    op.drop_index('idx_transaction_product', 'transaction')
    op.drop_index('idx_transaction_type', 'transaction')
    op.drop_index('idx_transaction_date', 'transaction')
    op.drop_index('idx_transaction_financial_year', 'transaction')
    op.drop_index('idx_transaction_from_location', 'transaction')
    op.drop_index('idx_transaction_to_location', 'transaction')
    op.drop_index('idx_transaction_product_type', 'transaction')
    op.drop_index('idx_transaction_type_date', 'transaction')
    op.drop_index('idx_transaction_from_to', 'transaction')
    op.drop_index('idx_transaction_create_date', 'transaction')
    op.drop_index('idx_transaction_modified_date', 'transaction')
    
    # Payment Transaction table indexes
    op.drop_index('idx_payment_transaction_reference', 'payment_transaction')
    op.drop_index('idx_payment_transaction_status', 'payment_transaction')
    op.drop_index('idx_payment_transaction_gateway', 'payment_transaction')
    op.drop_index('idx_payment_transaction_gateway_status', 'payment_transaction')
    op.drop_index('idx_payment_transaction_amount', 'payment_transaction')
    op.drop_index('idx_payment_transaction_model', 'payment_transaction')
    op.drop_index('idx_payment_transaction_requester', 'payment_transaction')
    op.drop_index('idx_payment_transaction_payment_gateway', 'payment_transaction')
    op.drop_index('idx_payment_transaction_payment_type', 'payment_transaction')
    op.drop_index('idx_payment_transaction_create_date', 'payment_transaction')
    op.drop_index('idx_payment_transaction_last_modified', 'payment_transaction')
    op.drop_index('idx_payment_transaction_retry', 'payment_transaction')
    op.drop_index('idx_payment_transaction_is_online', 'payment_transaction')
    
    # Quotation table indexes
    op.drop_index('idx_quotation_customer', 'quotation')
    op.drop_index('idx_quotation_status', 'quotation')
    op.drop_index('idx_quotation_valid_until', 'quotation')
    op.drop_index('idx_quotation_create_date', 'quotation')
    op.drop_index('idx_quotation_modified_date', 'quotation')
    op.drop_index('idx_quotation_customer_status', 'quotation')
    op.drop_index('idx_quotation_status_date', 'quotation')
    op.drop_index('idx_quotation_total_amount', 'quotation')
    op.drop_index('idx_quotation_currency', 'quotation')
    
    # Invoice table indexes
    op.drop_index('idx_invoice_customer', 'invoice')
    op.drop_index('idx_invoice_order', 'invoice')
    op.drop_index('idx_invoice_status', 'invoice')
    op.drop_index('idx_invoice_due_date', 'invoice')
    op.drop_index('idx_invoice_create_date', 'invoice')
    op.drop_index('idx_invoice_modified_date', 'invoice')
    op.drop_index('idx_invoice_customer_status', 'invoice')
    op.drop_index('idx_invoice_status_date', 'invoice')
    op.drop_index('idx_invoice_total_amount', 'invoice')
    op.drop_index('idx_invoice_currency', 'invoice')
    op.drop_index('idx_invoice_invoice_number', 'invoice')
    
    # Branch table indexes
    op.drop_index('idx_branch_company', 'branch')
    op.drop_index('idx_branch_active', 'branch')
    op.drop_index('idx_branch_city', 'branch')
    op.drop_index('idx_branch_country', 'branch')
    op.drop_index('idx_branch_company_active', 'branch')
    op.drop_index('idx_branch_create_date', 'branch')
    op.drop_index('idx_branch_modified_date', 'branch')
    
    # Store table indexes
    op.drop_index('idx_store_branch', 'store')
    op.drop_index('idx_store_active', 'store')
    op.drop_index('idx_store_city', 'store')
    op.drop_index('idx_store_country', 'store')
    op.drop_index('idx_store_branch_active', 'store')
    op.drop_index('idx_store_create_date', 'store')
    op.drop_index('idx_store_modified_date', 'store')
    
    # Company table indexes
    op.drop_index('idx_company_active', 'company')
    op.drop_index('idx_company_country', 'company')
    op.drop_index('idx_company_create_date', 'company')
    op.drop_index('idx_company_modified_date', 'company')
    
    # Expense table indexes
    op.drop_index('idx_expense_category', 'expense')
    op.drop_index('idx_expense_branch', 'expense')
    op.drop_index('idx_expense_status', 'expense')
    op.drop_index('idx_expense_approver', 'expense')
    op.drop_index('idx_expense_create_date', 'expense')
    op.drop_index('idx_expense_modified_date', 'expense')
    op.drop_index('idx_expense_category_status', 'expense')
    op.drop_index('idx_expense_branch_status', 'expense')
    op.drop_index('idx_expense_amount', 'expense')
    op.drop_index('idx_expense_currency', 'expense')
    op.drop_index('idx_expense_expense_date', 'expense')
    
    # Expense Category table indexes
    op.drop_index('idx_expense_category_active', 'expense_category')
    op.drop_index('idx_expense_category_parent', 'expense_category')
    op.drop_index('idx_expense_category_parent_active', 'expense_category')
    op.drop_index('idx_expense_category_create_date', 'expense_category')
    op.drop_index('idx_expense_category_modified_date', 'expense_category')
    
    # Financial Year table indexes
    op.drop_index('idx_fiscal_year_active', 'fiscal_year')
    op.drop_index('idx_fiscal_year_start_date', 'fiscal_year')
    op.drop_index('idx_fiscal_year_end_date', 'fiscal_year')
    op.drop_index('idx_fiscal_year_create_date', 'fiscal_year')
    op.drop_index('idx_fiscal_year_modified_date', 'fiscal_year')
    
    # Fiscal Period table indexes
    op.drop_index('idx_fiscal_period_year', 'fiscal_period')
    op.drop_index('idx_fiscal_period_start_date', 'fiscal_period')
    op.drop_index('idx_fiscal_period_end_date', 'fiscal_period')
    op.drop_index('idx_fiscal_period_create_date', 'fiscal_period')
    op.drop_index('idx_fiscal_period_modified_date', 'fiscal_period')
    op.drop_index('idx_fiscal_period_year_start', 'fiscal_period')
    
    # Rating table indexes
    op.drop_index('idx_rating_user', 'rating')
    op.drop_index('idx_rating_product', 'rating')
    op.drop_index('idx_rating_order', 'rating')
    op.drop_index('idx_rating_rating', 'rating')
    op.drop_index('idx_rating_create_date', 'rating')
    op.drop_index('idx_rating_modified_date', 'rating')
    op.drop_index('idx_rating_user_product', 'rating')
    op.drop_index('idx_rating_product_rating', 'rating')
    
    # Media table indexes
    op.drop_index('idx_media_model_type', 'media')
    op.drop_index('idx_media_model_id', 'media')
    op.drop_index('idx_media_model', 'media')
    op.drop_index('idx_media_create_date', 'media')
    op.drop_index('idx_media_modified_date', 'media')
    op.drop_index('idx_media_last_modified', 'media')
    
    # Shipping Address table indexes
    op.drop_index('idx_shipping_address_customer', 'shipping_address')
    op.drop_index('idx_shipping_address_city', 'shipping_address')
    op.drop_index('idx_shipping_address_country', 'shipping_address')
    op.drop_index('idx_shipping_address_postal_code', 'shipping_address')
    op.drop_index('idx_shipping_address_is_default', 'shipping_address')
    op.drop_index('idx_shipping_address_customer_default', 'shipping_address')
    op.drop_index('idx_shipping_address_create_date', 'shipping_address')
    op.drop_index('idx_shipping_address_modified_date', 'shipping_address')
    
    # Staff table indexes
    op.drop_index('idx_staff_user', 'staff')
    op.drop_index('idx_staff_branch', 'staff')
    op.drop_index('idx_staff_department', 'staff')
    op.drop_index('idx_staff_position', 'staff')
    op.drop_index('idx_staff_active', 'staff')
    op.drop_index('idx_staff_branch_active', 'staff')
    op.drop_index('idx_staff_create_date', 'staff')
    op.drop_index('idx_staff_modified_date', 'staff')
    
    # Role table indexes
    op.drop_index('idx_role_active', 'role')
    op.drop_index('idx_role_create_date', 'role')
    op.drop_index('idx_role_modified_date', 'role')
    
    # Permission table indexes
    op.drop_index('idx_permission_resource', 'permission')
    op.drop_index('idx_permission_action', 'permission')
    op.drop_index('idx_permission_resource_action', 'permission')
    op.drop_index('idx_permission_create_date', 'permission')
    op.drop_index('idx_permission_modified_date', 'permission')
    
    # User Roles table indexes
    op.drop_index('idx_user_roles_user', 'user_roles')
    op.drop_index('idx_user_roles_role', 'user_roles')
    op.drop_index('idx_user_roles_user_role', 'user_roles')
    
    # Role Permissions table indexes
    op.drop_index('idx_role_permissions_role', 'role_permissions')
    op.drop_index('idx_role_permissions_permission', 'role_permissions')
    op.drop_index('idx_role_permissions_role_permission', 'role_permissions')
    
    # Tracking table indexes
    op.drop_index('idx_tracking_user', 'tracking')
    op.drop_index('idx_tracking_action', 'tracking')
    op.drop_index('idx_tracking_model_type', 'tracking')
    op.drop_index('idx_tracking_model_id', 'tracking')
    op.drop_index('idx_tracking_model', 'tracking')
    op.drop_index('idx_tracking_create_date', 'tracking')
    op.drop_index('idx_tracking_user_action', 'tracking')
    op.drop_index('idx_tracking_action_date', 'tracking')
    
    # Print Job table indexes (if exists)
    try:
        op.drop_index('idx_print_job_order', 'print_job')
        op.drop_index('idx_print_job_status', 'print_job')
        op.drop_index('idx_print_job_priority', 'print_job')
        op.drop_index('idx_print_job_create_date', 'print_job')
        op.drop_index('idx_print_job_modified_date', 'print_job')
        op.drop_index('idx_print_job_status_priority', 'print_job')
        op.drop_index('idx_print_job_order_status', 'print_job')
    except Exception:
        pass
    
    # Supplier table indexes (if exists)
    try:
        op.drop_index('idx_supplier_active', 'supplier')
        op.drop_index('idx_supplier_country', 'supplier')
        op.drop_index('idx_supplier_city', 'supplier')
        op.drop_index('idx_supplier_create_date', 'supplier')
        op.drop_index('idx_supplier_modified_date', 'supplier')
    except Exception:
        pass
