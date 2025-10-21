import { createReducer, on } from '@ngrx/store';
import { Order } from '../../models/order.model';
import { PaginationMeta } from '../../models/common.model';
import * as OrderActions from '../actions/order.actions';

export interface OrderState {
  orders: Order[];
  currentOrder: Order | null;
  pagination: PaginationMeta | null;
  loading: boolean;
  error: string | null;
}

export const initialState: OrderState = {
  orders: [],
  currentOrder: null,
  pagination: null,
  loading: false,
  error: null
};

export const orderReducer = createReducer(
  initialState,
  
  // Load Orders
  on(OrderActions.loadOrders, (state) => ({
    ...state,
    loading: true,
    error: null
  })),
  
  on(OrderActions.loadOrdersSuccess, (state, { response }) => ({
    ...state,
    orders: response.data,
    pagination: response.meta,
    loading: false,
    error: null
  })),
  
  on(OrderActions.loadOrdersFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Load Order
  on(OrderActions.loadOrder, (state) => ({
    ...state,
    loading: true,
    error: null
  })),
  
  on(OrderActions.loadOrderSuccess, (state, { order }) => ({
    ...state,
    currentOrder: order,
    loading: false,
    error: null
  })),
  
  on(OrderActions.loadOrderFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Create Order
  on(OrderActions.createOrder, (state) => ({
    ...state,
    loading: true,
    error: null
  })),
  
  on(OrderActions.createOrderSuccess, (state, { order }) => ({
    ...state,
    currentOrder: order,
    orders: [order, ...state.orders],
    loading: false,
    error: null
  })),
  
  on(OrderActions.createOrderFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Cancel Order
  on(OrderActions.cancelOrder, (state) => ({
    ...state,
    loading: true,
    error: null
  })),
  
  on(OrderActions.cancelOrderSuccess, (state, { order }) => ({
    ...state,
    currentOrder: state.currentOrder?.id === order.id ? order : state.currentOrder,
    orders: state.orders.map(o => o.id === order.id ? order : o),
    loading: false,
    error: null
  })),
  
  on(OrderActions.cancelOrderFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Update Order Status (from WebSocket)
  on(OrderActions.updateOrderStatus, (state, { orderId, status }) => ({
    ...state,
    currentOrder: state.currentOrder?.id === orderId 
      ? { ...state.currentOrder, status } 
      : state.currentOrder,
    orders: state.orders.map(order => 
      order.id === orderId ? { ...order, status } : order
    )
  })),
  
  // Clear Current Order
  on(OrderActions.clearCurrentOrder, (state) => ({
    ...state,
    currentOrder: null
  }))
);

