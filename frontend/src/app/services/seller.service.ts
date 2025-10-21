import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../core/services/api.service';
import {
  Seller,
  SellerCommission,
  SellerPerformance,
  SellerPayment,
  SellerDashboard
} from '../models/seller.model';
import { PaginatedResponse } from '../models/common.model';

@Injectable({
  providedIn: 'root'
})
export class SellerService {
  constructor(private api: ApiService) {}

  /**
   * Get seller dashboard
   */
  getSellerDashboard(): Observable<SellerDashboard> {
    return this.api.get<SellerDashboard>('seller/dashboard');
  }

  /**
   * Get seller profile
   */
  getSellerProfile(): Observable<Seller> {
    return this.api.get<Seller>('seller/profile');
  }

  /**
   * Update seller profile
   */
  updateSellerProfile(data: Partial<Seller>): Observable<Seller> {
    return this.api.put<Seller>('seller/profile', data);
  }

  /**
   * Get seller commissions
   */
  getCommissions(params?: {
    page?: number;
    limit?: number;
    status?: string;
  }): Observable<PaginatedResponse<SellerCommission>> {
    return this.api.getPaginated<SellerCommission>('seller/commissions', params);
  }

  /**
   * Get commission summary
   */
  getCommissionSummary(period?: string): Observable<any> {
    return this.api.get<any>('seller/commissions/summary', { period });
  }

  /**
   * Get seller performance
   */
  getPerformance(period?: string): Observable<SellerPerformance> {
    return this.api.get<SellerPerformance>('seller/performance', { period });
  }

  /**
   * Get payment history
   */
  getPaymentHistory(params?: {
    page?: number;
    limit?: number;
  }): Observable<PaginatedResponse<SellerPayment>> {
    return this.api.getPaginated<SellerPayment>('seller/payments', params);
  }

  /**
   * Request payment/settlement
   */
  requestPayment(): Observable<any> {
    return this.api.post<any>('seller/payments/request', {});
  }

  /**
   * Get seller orders
   */
  getSellerOrders(params?: {
    page?: number;
    limit?: number;
    status?: string;
  }): Observable<PaginatedResponse<any>> {
    return this.api.getPaginated<any>('seller/orders', params);
  }

  /**
   * Get seller customers
   */
  getCustomers(params?: {
    page?: number;
    limit?: number;
  }): Observable<PaginatedResponse<any>> {
    return this.api.getPaginated<any>('seller/customers', params);
  }

  /**
   * Get all sellers (admin only)
   */
  getAllSellers(params?: {
    page?: number;
    limit?: number;
    status?: string;
  }): Observable<PaginatedResponse<Seller>> {
    return this.api.getPaginated<Seller>('admin/sellers', params);
  }

  /**
   * Approve seller (admin only)
   */
  approveSeller(id: string): Observable<Seller> {
    return this.api.put<Seller>(`admin/sellers/${id}/approve`, {});
  }

  /**
   * Suspend seller (admin only)
   */
  suspendSeller(id: string, reason: string): Observable<Seller> {
    return this.api.put<Seller>(`admin/sellers/${id}/suspend`, { reason });
  }

  /**
   * Process seller payment (admin only)
   */
  processPayment(paymentId: string, data: any): Observable<SellerPayment> {
    return this.api.put<SellerPayment>(`admin/seller-payments/${paymentId}/process`, data);
  }
}

