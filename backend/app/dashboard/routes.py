#For read logs of the application 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, g, make_response, Response
from app.common.queries import create_filters

from app.security import roles, permissions
from app.common import filters
from app.utils.response import APIResponse
from pygtail import Pygtail
from app.utilities.common_utils import get_owner_id

__uri__ = 'dashboards'
__blueprint__ = 'dashboards'

dashboards = Blueprint(__uri__, __name__)

@dashboards.route('/users', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['dashboards.users','dashboards.all'])
def get_users(self):
    from app.users.service import UserService
    user_statistics, status = UserService().get_users_statistics()
    if status == 200:
        return APIResponse.success({'user_statistics': user_statistics}, "User statistics retrieved successfully")
    return APIResponse.error("Failed to retrieve user statistics", status_code=status)

@dashboards.route('/invoices', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['dashboards.invoices','dashboards.all'])
@filters.filters
def get_invoices(self, filters):
    from app.invoices.service import InvoiceService
    invoices_statistics, status = InvoiceService().get_invoices_statistics(filters)
    if status == 200:
        return APIResponse.success({'invoices_statistics': invoices_statistics}, "Invoice statistics retrieved successfully")
    return APIResponse.error("Failed to retrieve invoice statistics", status_code=status)

@dashboards.route('/invoices/total', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['dashboards.invoices','dashboards.all'])
@filters.filters
def get_invoices_count(self, filters):
    from app.invoices.service import InvoiceService
    invoices_count, status = InvoiceService().get_invoices_total_amount(filters)
    if status == 200:
        return APIResponse.success({'invoices_count': invoices_count}, "Invoice total retrieved successfully")
    return APIResponse.error("Failed to retrieve invoice total", status_code=status)

@dashboards.route('/invoices/count', methods=['GET'])
@permissions.has_permission(['invoices.view', 'invoices.all'])
@filters.filters
def get_total_invoices_count(self, filters):
    from app.invoices.service import InvoiceService
    result, status = InvoiceService().get_total_invoices_count(filters)
    if status == 200:
        return APIResponse.success(result, "Invoice count retrieved successfully")
    return APIResponse.error("Failed to retrieve invoice count", status_code=status)

@dashboards.route('/payment_transactions', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['dashboards.payment_transactions','dashboards.all'])
def get_payment_transactions(self):
    from app.payment_transaction.service import PaymentTransactionsService
    payment_transactions_statistics, status = PaymentTransactionsService().get_payment_transactions_statistics()
    if status == 200:
        return APIResponse.success({'payment_transactions_statistics': payment_transactions_statistics}, "Payment transaction statistics retrieved successfully")
    return APIResponse.error("Failed to retrieve payment transaction statistics", status_code=status)

@dashboards.route('/customers/total', methods=['GET'])
@permissions.has_permission(['customers.view', 'customers.all'])
def get_total_customers(self):
    from app.customers.service import CustomerService
    result, status = CustomerService().get_total_customers()
    if status == 200:
        return APIResponse.success(result, "Customer total retrieved successfully")
    return APIResponse.error("Failed to retrieve customer total", status_code=status)

@dashboards.route('/payments/total', methods=['GET'])
@permissions.has_permission(['payments.view', 'payments.all'])
@filters.filters
def get_total_payments_amount(self, filter):
    from app.payment.service import PaymentService
    result, status = PaymentService().get_total_payments_amount(filter=filter)
    if status == 200:
        return APIResponse.success(result, "Payment total retrieved successfully")
    return APIResponse.error("Failed to retrieve payment total", status_code=status)

@dashboards.route('/expenses/total', methods=['GET'])
@permissions.has_permission(['expenses.view', 'expenses.all'])
@filters.filters
def get_total_expenses_amount(self, filter):
    from app.expense.service import ExpenseService
    result, status = ExpenseService().get_total_expenses_amount(filter=filter)
    if status == 200:
        return APIResponse.success(result, "Expense total retrieved successfully")
    return APIResponse.error("Failed to retrieve expense total", status_code=status)

@dashboards.route('/inventory/total_quantity', methods=['GET'])
@permissions.has_permission(['inventory.view', 'inventory.all'])
@filters.filters
def get_total_products_quantity(self, filter):
    from app.inventory.service import InventoryService
    result, status = InventoryService().get_total_products_quantity(filter=filter)
    if status == 200:
        return APIResponse.success(result, "Inventory quantity retrieved successfully")
    return APIResponse.error("Failed to retrieve inventory quantity", status_code=status)

@dashboards.route('/transactions/total', methods=['GET'])
@permissions.has_permission(['transactions.view', 'transactions.all'])
@filters.filters
def get_total_transactions(self, filter):
    from app.transaction.service import TransactionService
    result, status = TransactionService().get_total_transactions(filter=filter)
    if status == 200:
        return APIResponse.success(result, "Transaction total retrieved successfully")
    return APIResponse.error("Failed to retrieve transaction total", status_code=status)

@dashboards.route('/orders/count', methods=['GET'])
@roles.token_required
@filters.filters
def get_total_orders_count(self, filter):
    from app.order.service import OrderService
    result, status = OrderService().get_total_orders_count(filter=filter)
    if status == 200:
        return APIResponse.success(result, "Order count retrieved successfully")
    return APIResponse.error("Failed to retrieve order count", status_code=status)

@dashboards.route('/orders/total_amount', methods=['GET'])
@roles.token_required
@filters.filters
def get_total_orders_amount(self, filter):
    from app.order.service import OrderService
    result, status = OrderService().get_total_orders_amount(filter=filter)
    if status == 200:
        return APIResponse.success(result, "Order total amount retrieved successfully")
    return APIResponse.error("Failed to retrieve order total amount", status_code=status)