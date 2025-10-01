#For read logs of the application 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, g, make_response, Response
from app.common.queries import create_filters

from app.security import roles, permissions
from app.common import filters
from pygtail import Pygtail
from app.utilities.common_utils import get_owner_id

__uri__ = 'dashboards'
__blueprint__ = 'dashboards'

dashboards = Blueprint(__uri__, __name__)

@dashboards.route('/users', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['dashboards.users','dashboards.all'])
@roles.token_required
def get_users(self):
    from app.users.service import UserService
    user_statistics, status = UserService().get_users_statistics()
    return jsonify({'user_statistics': user_statistics}) , status

@dashboards.route('/invoices', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['dashboards.invoices','dashboards.all'])
@roles.token_required
@filters.filters
def get_invoices(filters,self):
    from app.invoices.service import InvoiceService
    invoices_statistics, status = InvoiceService().get_invoices_statistics(filters)
    return jsonify({'invoices_statistics': invoices_statistics}) , status

@dashboards.route('/invoices/total', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['dashboards.invoices','dashboards.all'])
@roles.token_required
@filters.filters
def get_invoices_count(filters,self):
    from app.invoices.service import InvoiceService
    invoices_count, status = InvoiceService().get_invoices_total_amount(filters)
    return jsonify({'invoices_count': invoices_count}) , status

@dashboards.route('/invoices/count', methods=['GET'])
#@permissions.has_permission(['invoices.view', 'invoices.all'])
@roles.token_required
@filters.filters
def get_total_invoices_count(filters, self):
    from app.invoices.service import InvoiceService
    result, status = InvoiceService().get_total_invoices_count(filters)
    return jsonify(result), status

@dashboards.route('/payment_transactions', methods=['GET'])
#@cross_origin()
#@permissions.has_permission(['dashboards.payment_transactions','dashboards.all'])
@roles.token_required
def get_payment_transactions(self):
    from app.payment_transaction.service import PaymentTransactionsService
    payment_transactions_statistics, status = PaymentTransactionsService().get_payment_transactions_statistics()
    return jsonify({'payment_transactions_statistics': payment_transactions_statistics}) , status

@dashboards.route('/customers/total', methods=['GET'])
#@permissions.has_permission(['customers.view', 'customers.all'])
@roles.token_required
def get_total_customers(self):
    from app.customers.service import CustomerService
    result, status = CustomerService().get_total_customers()
    return jsonify(result), status

@dashboards.route('/payments/total', methods=['GET'])
#@permissions.has_permission(['payments.view', 'payments.all'])
@roles.token_required
@filters.filters
def get_total_payments_amount(filter,self):
    from app.payment.service import PaymentService
    result, status = PaymentService().get_total_payments_amount(filter=filter)
    return jsonify(result), status

@dashboards.route('/expenses/total', methods=['GET'])
#@permissions.has_permission(['expenses.view', 'expenses.all'])
@roles.token_required
@filters.filters
def get_total_expenses_amount(filter,self):
    from app.expense.service import ExpenseService
    result, status = ExpenseService().get_total_expenses_amount(filter=filter)
    return jsonify(result), status

@dashboards.route('/inventory/total_quantity', methods=['GET'])
#@permissions.has_permission(['inventory.view', 'inventory.all'])
@roles.token_required
@filters.filters
def get_total_products_quantity(filter, self):
    from app.inventory.service import InventoryService
    result, status = InventoryService().get_total_products_quantity(filter=filter)
    return jsonify(result), status

@dashboards.route('/transactions/total', methods=['GET'])
#@permissions.has_permission(['transactions.view', 'transactions.all'])
@roles.token_required
@filters.filters
def get_total_transactions(filter, self):
    from app.transaction.service import TransactionService
    result, status = TransactionService().get_total_transactions(filter=filter)
    return jsonify(result), status

@dashboards.route('/orders/count', methods=['GET'])
@roles.token_required
@filters.filters
def get_total_orders_count(filter, self):
    from app.order.service import OrderService
    result, status = OrderService().get_total_orders_count(filter=filter)
    return jsonify(result), status

@dashboards.route('/orders/total_amount', methods=['GET'])
@roles.token_required
@filters.filters
def get_total_orders_amount(filter, self):
    from app.order.service import OrderService
    result, status = OrderService().get_total_orders_amount(filter=filter)
    return jsonify(result), status