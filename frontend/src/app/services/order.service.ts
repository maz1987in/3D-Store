import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../core/services/api.service';
import {
  Order,
  CreateOrderRequest,
  OrderTimeline,
  OrderSummary,
  OrderStatus
} from '../models/order.model';
import { PaginatedResponse } from '../models/common.model';

@Injectable({
  providedIn: 'root'
})
export class OrderService {
  constructor(private api: ApiService) {}

  /**
   * Create new order
   */
  createOrder(orderData: CreateOrderRequest): Observable<Order> {
    return this.api.post<Order>('orders', orderData);
  }

  /**
   * Get user orders
   */
  getUserOrders(params?: {
    page?: number;
    limit?: number;
    status?: OrderStatus;
  }): Observable<PaginatedResponse<Order>> {
    return this.api.getPaginated<Order>('orders', params);
  }

  /**
   * Get order by ID
   */
  getOrder(id: string): Observable<Order> {
    return this.api.get<Order>(`orders/${id}`);
  }

  /**
   * Update order status
   */
  updateOrderStatus(id: string, status: OrderStatus): Observable<Order> {
    return this.api.put<Order>(`orders/${id}/status`, { status });
  }

  /**
   * Cancel order
   */
  cancelOrder(id: string, reason?: string): Observable<Order> {
    return this.api.put<Order>(`orders/${id}/cancel`, { reason });
  }

  /**
   * Get order timeline
   */
  getOrderTimeline(id: string): Observable<OrderTimeline[]> {
    return this.api.get<OrderTimeline[]>(`orders/${id}/timeline`);
  }

  /**
   * Get order summary
   */
  getOrderSummary(items: any[]): Observable<OrderSummary> {
    return this.api.post<OrderSummary>('orders/summary', { items });
  }

  /**
   * Download invoice
   */
  downloadInvoice(id: string): Observable<Blob> {
    return this.api.downloadFile(`orders/${id}/invoice`);
  }

  /**
   * Get order tracking info
   */
  getTrackingInfo(id: string): Observable<any> {
    return this.api.get<any>(`orders/${id}/tracking`);
  }

  /**
   * Get all orders (admin only)
   */
  getAllOrders(params?: {
    page?: number;
    limit?: number;
    status?: OrderStatus;
    customer_id?: string;
  }): Observable<PaginatedResponse<Order>> {
    return this.api.getPaginated<Order>('admin/orders', params);
  }

  /**
   * Update order (admin only)
   */
  updateOrder(id: string, data: Partial<Order>): Observable<Order> {
    return this.api.put<Order>(`admin/orders/${id}`, data);
  }
}

