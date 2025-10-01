# Expense Module

The Expense module manages business expense tracking, approval workflows, and expense analytics in the 3D Store application, providing comprehensive expense management capabilities.

## Overview

This module handles:
- Expense creation and tracking
- Approval workflow management
- Expense categorization and classification
- Budget monitoring and alerts
- Receipt management and storage
- Expense reporting and analytics
- Reimbursement processing

## Module Structure

```
expense/
├── __init__.py          # Module initialization
├── model.py            # SQLAlchemy models
├── routes.py           # Flask API endpoints
├── service.py          # Business logic layer
├── repository.py       # Data access layer (Repository pattern)
├── schemas.py          # Input validation schemas
├── swagger.yaml        # API documentation
└── README.md           # This documentation
```

## Models

### Expense
Main expense entity with the following key attributes:
- **Basic Info**: `expense_id`, `amount`, `currency`, `date`, `description`
- **Category**: `expense_category`, `subcategory`, `expense_type`
- **Vendor**: `vendor_name`, `vendor_contact`, `vendor_address`
- **Payment**: `payment_method`, `payment_reference`, `receipt_url`
- **Status**: `status`, `is_recurring`, `recurrence_pattern`
- **Approval**: `approved_by`, `approved_at`, `rejection_reason`
- **Metadata**: `created_at`, `updated_at`, `created_by`

### ExpenseCategory
Expense categorization system:
- **Category Info**: `name`, `description`, `parent_id`, `is_active`
- **Budget**: `budget_allocation`, `warning_threshold`, `critical_threshold`
- **Rules**: `approval_required`, `max_amount`, `min_amount`
- **Metadata**: `created_at`, `updated_at`, `sort_order`

### ExpenseApproval
Expense approval workflow:
- **Approval Info**: `expense_id`, `approver_id`, `approval_level`
- **Status**: `status`, `approved_at`, `rejected_at`
- **Comments**: `approval_comments`, `rejection_reason`
- **Timestamps**: `created_at`, `updated_at`, `due_date`

### ExpenseBudget
Budget management for expenses:
- **Budget Info**: `budget_id`, `name`, `period`, `start_date`, `end_date`
- **Amounts**: `total_budget`, `allocated_amount`, `spent_amount`
- **Categories**: `budget_categories` (relationship)
- **Status**: `status`, `is_active`, `variance_threshold`
- **Metadata**: `created_at`, `updated_at`, `created_by`

### ExpenseReceipt
Receipt management and storage:
- **Receipt Info**: `expense_id`, `receipt_url`, `file_name`, `file_size`
- **OCR Data**: `extracted_text`, `merchant_name`, `amount`, `date`
- **Validation**: `is_validated`, `validation_notes`
- **Metadata**: `created_at`, `updated_at`

### ExpenseReimbursement
Employee reimbursement processing:
- **Reimbursement Info**: `employee_id`, `expense_id`, `amount`, `currency`
- **Status**: `status`, `processed_at`, `payment_date`
- **Payment**: `payment_method`, `payment_reference`
- **Metadata**: `created_at`, `updated_at`, `processed_by`

## Repository Layer

The `ExpenseRepository` class provides data access operations for the Expense module using the Repository pattern.

### Key Features
- **Base Repository**: Extends `BaseRepository[Expense]` for common CRUD operations
- **Advanced Filtering**: Complex filtering, sorting, and pagination
- **Relationship Loading**: Eager loading of related entities (category, approver)
- **Type Safety**: Generic type support for better IDE support
- **Error Handling**: Consistent error handling across all operations

### Repository Methods

#### Basic CRUD Operations
- `get_by_id(expense_id)` - Get expense by ID
- `create(expense_data)` - Create new expense
- `update(expense_id, expense_data)` - Update existing expense
- `delete(expense_id)` - Delete expense
- `get_all(limit, offset)` - Get all expenses with pagination

#### Advanced Query Methods
- `get_expenses_with_category(filter_obj)` - Expenses with category information
- `get_expenses_by_category(category_id)` - Expenses by category
- `get_expenses_by_status(status)` - Expenses by status
- `get_expenses_by_date_range(start_date, end_date)` - Expenses by date range
- `get_expenses_by_amount_range(min_amount, max_amount)` - Expenses by amount range
- `get_expenses_by_fiscal_year(fiscal_year_id)` - Expenses by fiscal year
- `get_pending_expenses()` - Pending expenses
- `get_approved_expenses()` - Approved expenses
- `get_rejected_expenses()` - Rejected expenses
- `update_expense_status(expense_id, new_status)` - Update expense status
- `get_expenses_by_category_summary()` - Expense summary by category

#### Statistics and Analytics
- `get_expense_statistics()` - Statistics for dashboard/reporting

### Usage Example

```python
from app.expense.repository import ExpenseRepository

# Initialize repository
expense_repo = ExpenseRepository()

# Get expenses with filtering and pagination
filter_obj = FilterObj()
result = expense_repo.get_expenses_with_category(filter_obj)

# Get expenses by category
category_expenses = expense_repo.get_expenses_by_category("category-uuid")

# Get pending expenses
pending = expense_repo.get_pending_expenses()

# Update expense status
expense_repo.update_expense_status("expense-uuid", ExpenseStatusEnum.APPROVED)

# Get expense statistics
stats = expense_repo.get_expense_statistics()
```

## API Endpoints

### Expense Management
- `GET /expenses` - List expenses with filtering
- `GET /expenses/{id}` - Get expense details
- `POST /expenses` - Create new expense
- `PUT /expenses/{id}` - Update expense
- `DELETE /expenses/{id}` - Delete expense
- `POST /expenses/{id}/submit` - Submit expense for approval
- `POST /expenses/{id}/cancel` - Cancel expense

### Expense Categories
- `GET /expenses/categories` - List expense categories
- `GET /expenses/categories/{id}` - Get category details
- `POST /expenses/categories` - Create new category
- `PUT /expenses/categories/{id}` - Update category
- `DELETE /expenses/categories/{id}` - Delete category

### Approval Workflow
- `GET /expenses/approvals` - List pending approvals
- `GET /expenses/approvals/{id}` - Get approval details
- `POST /expenses/approvals/{id}/approve` - Approve expense
- `POST /expenses/approvals/{id}/reject` - Reject expense
- `GET /expenses/approvals/history` - Get approval history

### Budget Management
- `GET /expenses/budgets` - List expense budgets
- `GET /expenses/budgets/{id}` - Get budget details
- `POST /expenses/budgets` - Create new budget
- `PUT /expenses/budgets/{id}` - Update budget
- `DELETE /expenses/budgets/{id}` - Delete budget
- `GET /expenses/budgets/{id}/performance` - Get budget performance

### Receipt Management
- `POST /expenses/{id}/receipt` - Upload receipt
- `GET /expenses/{id}/receipt` - Get receipt
- `DELETE /expenses/{id}/receipt` - Delete receipt
- `POST /expenses/{id}/receipt/ocr` - Process receipt with OCR

### Reimbursement
- `GET /expenses/reimbursements` - List reimbursements
- `GET /expenses/reimbursements/{id}` - Get reimbursement details
- `POST /expenses/reimbursements` - Create reimbursement
- `POST /expenses/reimbursements/{id}/process` - Process reimbursement
- `GET /expenses/reimbursements/employee/{id}` - Get employee reimbursements

### Reports and Analytics
- `GET /expenses/reports/summary` - Get expense summary
- `GET /expenses/reports/category` - Get category-wise expenses
- `GET /expenses/reports/trends` - Get expense trends
- `GET /expenses/reports/budget-variance` - Get budget variance report
- `GET /expenses/reports/approval-performance` - Get approval performance

## Business Logic

### Expense Creation
1. **Data Validation**: Validate expense data and required fields
2. **Category Assignment**: Assign appropriate expense category
3. **Amount Validation**: Check against budget limits and rules
4. **Receipt Processing**: Handle receipt upload and OCR processing
5. **Approval Routing**: Route to appropriate approver based on amount
6. **Notification**: Send notifications to relevant stakeholders

### Approval Workflow
1. **Approval Routing**: Determine approval hierarchy and routing
2. **Notification**: Notify approvers of pending approvals
3. **Approval Processing**: Handle approval or rejection
4. **Escalation**: Escalate overdue approvals
5. **Status Updates**: Update expense status throughout workflow
6. **Audit Trail**: Maintain complete approval audit trail

### Budget Management
1. **Budget Creation**: Create annual and monthly budgets
2. **Category Allocation**: Allocate budget across expense categories
3. **Spending Tracking**: Track actual spending against budget
4. **Variance Analysis**: Analyze budget variances and trends
5. **Alert Generation**: Generate alerts for budget overruns
6. **Forecasting**: Predict future spending patterns

### Receipt Processing
1. **Upload Handling**: Secure receipt file upload
2. **OCR Processing**: Extract data from receipt images
3. **Data Validation**: Validate extracted data against expense
4. **Storage Management**: Store receipts securely
5. **Access Control**: Control access to receipt files
6. **Retention Policy**: Manage receipt retention periods

### Reimbursement Processing
1. **Eligibility Check**: Verify expense eligibility for reimbursement
2. **Amount Calculation**: Calculate reimbursement amount
3. **Approval Workflow**: Route through approval process
4. **Payment Processing**: Process reimbursement payment
5. **Tax Handling**: Handle tax implications of reimbursements
6. **Reporting**: Generate reimbursement reports

## Validation Schemas

### ExpenseCreateSchema
```python
{
    "amount": "decimal (required, min 0.01)",
    "currency": "string (required, enum: OMR|USD|EUR)",
    "date": "date (required)",
    "expense_category": "string (required, max 100 chars)",
    "subcategory": "string (optional, max 100 chars)",
    "expense_type": "string (required, enum: operating|capital|travel|meals|office)",
    "vendor_name": "string (optional, max 255 chars)",
    "vendor_contact": "string (optional, max 255 chars)",
    "description": "string (required, max 500 chars)",
    "payment_method": "string (optional, max 100 chars)",
    "payment_reference": "string (optional, max 100 chars)",
    "is_recurring": "boolean (optional, default false)",
    "recurrence_pattern": "string (optional, enum: daily|weekly|monthly|yearly)",
    "receipt_url": "string (optional, valid URL)"
}
```

### ExpenseUpdateSchema
```python
{
    "amount": "decimal (optional, min 0.01)",
    "date": "date (optional)",
    "expense_category": "string (optional, max 100 chars)",
    "subcategory": "string (optional, max 100 chars)",
    "vendor_name": "string (optional, max 255 chars)",
    "description": "string (optional, max 500 chars)",
    "payment_method": "string (optional, max 100 chars)",
    "payment_reference": "string (optional, max 100 chars)",
    "receipt_url": "string (optional, valid URL)"
}
```

### ExpenseApprovalSchema
```python
{
    "expense_id": "uuid (required)",
    "approver_id": "uuid (required)",
    "approval_level": "integer (required, min 1)",
    "approval_comments": "string (optional, max 1000 chars)",
    "due_date": "date (optional)"
}
```

### ExpenseBudgetSchema
```python
{
    "name": "string (required, max 255 chars)",
    "period": "string (required, enum: monthly|quarterly|yearly)",
    "start_date": "date (required)",
    "end_date": "date (required)",
    "total_budget": "decimal (required, min 0.01)",
    "categories": [
        {
            "category": "string (required, max 100 chars)",
            "allocated_amount": "decimal (required, min 0.01)",
            "warning_threshold": "decimal (optional, min 0, max 1)",
            "critical_threshold": "decimal (optional, min 0, max 1)"
        }
    ],
    "variance_threshold": "decimal (optional, min 0, max 1)"
}
```

## Error Handling

The module uses comprehensive error handling:
- **ValidationException**: For input validation errors
- **BusinessLogicException**: For business rule violations
- **ResourceNotFoundException**: When expense not found
- **ApprovalException**: For approval workflow errors
- **BudgetException**: For budget-related errors

## Dependencies

- **User Module**: For user authentication and approval
- **Financial Module**: For financial transaction recording
- **File Storage**: For receipt storage and management
- **Notification Module**: For approval notifications
- **OCR Service**: For receipt text extraction
- **Payment Module**: For reimbursement processing

## Usage Examples

### Creating an Expense
```python
from app.expense.service import ExpenseService
from app.expense.schemas import ExpenseCreateSchema

service = ExpenseService()
expense_data = {
    "amount": 150.00,
    "currency": "OMR",
    "date": "2024-01-15",
    "expense_category": "Materials",
    "subcategory": "3D Printing Filament",
    "expense_type": "operating",
    "vendor_name": "Material Supplier Co.",
    "description": "PLA filament purchase for production",
    "payment_method": "bank_transfer",
    "payment_reference": "TXN123456",
    "is_recurring": False
}

expense = service.create_expense(expense_data)
```

### Managing Approvals
```python
# Submit expense for approval
service.submit_expense_for_approval(expense_id)

# Approve expense
approval_data = {
    "expense_id": expense_id,
    "approver_id": approver_id,
    "approval_level": 1,
    "approval_comments": "Approved for business use"
}

service.approve_expense(approval_data)

# Reject expense
rejection_data = {
    "expense_id": expense_id,
    "approver_id": approver_id,
    "rejection_reason": "Insufficient documentation"
}

service.reject_expense(rejection_data)
```

### Budget Management
```python
# Create expense budget
budget_data = {
    "name": "Q1 2024 Expense Budget",
    "period": "quarterly",
    "start_date": "2024-01-01",
    "end_date": "2024-03-31",
    "total_budget": 10000.00,
    "categories": [
        {
            "category": "Materials",
            "allocated_amount": 4000.00,
            "warning_threshold": 0.8,
            "critical_threshold": 0.95
        },
        {
            "category": "Travel",
            "allocated_amount": 2000.00,
            "warning_threshold": 0.8,
            "critical_threshold": 0.95
        }
    ]
}

budget = service.create_budget(budget_data)

# Get budget performance
performance = service.get_budget_performance(budget_id)
```

### Receipt Processing
```python
# Upload receipt
receipt_url = service.upload_receipt(expense_id, receipt_file)

# Process receipt with OCR
ocr_data = service.process_receipt_ocr(expense_id)

# Get receipt data
receipt = service.get_receipt(expense_id)
```

### Reimbursement Processing
```python
# Create reimbursement
reimbursement_data = {
    "employee_id": "employee-uuid",
    "expense_id": "expense-uuid",
    "amount": 150.00,
    "currency": "OMR"
}

reimbursement = service.create_reimbursement(reimbursement_data)

# Process reimbursement
service.process_reimbursement(reimbursement_id)
```

## Performance Considerations

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Frequently accessed expense data cached
- **File Storage**: Efficient receipt storage and retrieval
- **OCR Processing**: Asynchronous OCR processing
- **Report Caching**: Pre-generated reports cached

## Security

- **Access Control**: Role-based permissions for expense management
- **Receipt Security**: Secure storage and access control for receipts
- **Audit Logging**: All expense changes logged
- **Data Encryption**: Sensitive expense data encrypted
- **Approval Security**: Secure approval workflow

## Integration Points

- **Financial Systems**: Integration with accounting software
- **OCR Services**: Receipt text extraction services
- **Payment Systems**: Reimbursement payment processing
- **Email Service**: Approval notifications
- **File Storage**: Receipt and document storage
- **Analytics**: Expense analytics and reporting

## Future Enhancements

- **AI-Powered Categorization**: Automatic expense categorization
- **Mobile App**: Mobile expense management application
- **Receipt OCR**: Advanced receipt data extraction
- **Expense Policies**: Automated policy enforcement
- **Advanced Analytics**: Machine learning expense insights
- **Integration APIs**: Third-party expense management integration
