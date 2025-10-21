import { createAction, props } from '@ngrx/store';
import { Order, CreateOrderRequest, OrderStatus } from '../../models/order.model';
import { PaginatedResponse } from '../../models/common.model';

// Load Orders Actions
export const loadOrders = createAction(
  '[Order] Load Orders',
  props<{ page?: number; limit?: number; status?: OrderStatus }>()
);

export const loadOrdersSuccess = createAction(
  '[Order] Load Orders Success',
  props<{ response: PaginatedResponse<Order> }>()
);

export const loadOrdersFailure = createAction(
  '[Order] Load Orders Failure',
  props<{ error: string }>()
);

// Load Order Details Actions
export const loadOrder = createAction(
  '[Order] Load Order',
  props<{ id: string }>()
);

export const loadOrderSuccess = createAction(
  '[Order] Load Order Success',
  props<{ order: Order }>()
);

export const loadOrderFailure = createAction(
  '[Order] Load Order Failure',
  props<{ error: string }>()
);

// Create Order Actions
export const createOrder = createAction(
  '[Order] Create Order',
  props<{ orderData: CreateOrderRequest }>()
);

export const createOrderSuccess = createAction(
  '[Order] Create Order Success',
  props<{ order: Order }>()
);

export const createOrderFailure = createAction(
  '[Order] Create Order Failure',
  props<{ error: string }>()
);

// Cancel Order Actions
export const cancelOrder = createAction(
  '[Order] Cancel Order',
  props<{ orderId: string; reason?: string }>()
);

export const cancelOrderSuccess = createAction(
  '[Order] Cancel Order Success',
  props<{ order: Order }>()
);

export const cancelOrderFailure = createAction(
  '[Order] Cancel Order Failure',
  props<{ error: string }>()
);

// Update Order Status (WebSocket)
export const updateOrderStatus = createAction(
  '[Order] Update Order Status',
  props<{ orderId: string; status: OrderStatus }>()
);

// Clear Current Order
export const clearCurrentOrder = createAction('[Order] Clear Current Order');

