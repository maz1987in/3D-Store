import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MaterialModule } from '../../shared/material.module';
import { LoadingComponent } from '../../shared/components/loading/loading.component';
import { ErrorComponent } from '../../shared/components/error/error.component';
import { PaginationComponent } from '../../shared/components/pagination/pagination.component';
import { Router } from '@angular/router';
import { OrderService } from '../../services/order.service';
import { Order, OrderStatus } from '../../models/order.model';

@Component({
  selector: 'app-orders',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MaterialModule,
    LoadingComponent,
    ErrorComponent,
    PaginationComponent
  ],
  template: `
    <div class="orders-container">
      <div class="page-header">
        <h1>My Orders</h1>
        <p>View and track your order history</p>
      </div>

      <!-- Status Filter -->
      <div class="filters-section">
        <mat-chip-set aria-label="Status filter">
          <mat-chip 
            [highlighted]="!selectedStatus"
            (click)="filterByStatus(undefined)">
            All Orders
          </mat-chip>
          <mat-chip 
            [highlighted]="selectedStatus === 'pending'"
            (click)="filterByStatus('pending')">
            Pending
          </mat-chip>
          <mat-chip 
            [highlighted]="selectedStatus === 'processing'"
            (click)="filterByStatus('processing')">
            Processing
          </mat-chip>
          <mat-chip 
            [highlighted]="selectedStatus === 'completed'"
            (click)="filterByStatus('completed')">
            Completed
          </mat-chip>
          <mat-chip 
            [highlighted]="selectedStatus === 'cancelled'"
            (click)="filterByStatus('cancelled')">
            Cancelled
          </mat-chip>
        </mat-chip-set>
      </div>

      <!-- Loading State -->
      @if (loading) {
        <app-loading type="skeleton"></app-loading>
      }

      <!-- Error State -->
      @else if (error) {
        <app-error [message]="error" (retry)="loadOrders()"></app-error>
      }

      <!-- Empty State -->
      @else if (orders.length === 0) {
        <div class="empty-state">
          <mat-icon>receipt_long</mat-icon>
          <h2>No orders found</h2>
          <p>You haven't placed any orders yet</p>
          <button mat-raised-button color="primary" routerLink="/products">
            <mat-icon>shopping_bag</mat-icon>
            Start Shopping
          </button>
        </div>
      }

      <!-- Orders List -->
      @else {
        <div class="orders-list">
          @for (order of orders; track order.id) {
            <mat-card class="order-card" [routerLink]="['/orders', order.id]">
              <mat-card-header>
                <mat-card-title>
                  <div class="order-header">
                    <span class="order-number">Order #{{ order.order_number }}</span>
                    <mat-chip [color]="getStatusColor(order.status)">
                      {{ order.status }}
                    </mat-chip>
                  </div>
                </mat-card-title>
                <mat-card-subtitle>
                  Placed on {{ order.order_date | date:'medium' }}
                </mat-card-subtitle>
              </mat-card-header>

              <mat-card-content>
                <div class="order-info">
                  <div class="info-item">
                    <mat-icon>shopping_bag</mat-icon>
                    <div>
                      <strong>Items</strong>
                      <p>{{ order.items.length }} item(s)</p>
                    </div>
                  </div>

                  <div class="info-item">
                    <mat-icon>attach_money</mat-icon>
                    <div>
                      <strong>Total</strong>
                      <p>{{ order.total_amount }} {{ order.currency }}</p>
                    </div>
                  </div>

                  <div class="info-item">
                    <mat-icon>payment</mat-icon>
                    <div>
                      <strong>Payment</strong>
                      <p>{{ order.payment_status }}</p>
                    </div>
                  </div>

                  @if (order.expected_delivery) {
                    <div class="info-item">
                      <mat-icon>local_shipping</mat-icon>
                      <div>
                        <strong>Expected Delivery</strong>
                        <p>{{ order.expected_delivery | date:'mediumDate' }}</p>
                      </div>
                    </div>
                  }
                </div>

                <!-- Order Items Preview -->
                <div class="items-preview">
                  @for (item of order.items.slice(0, 3); track item.id) {
                    <span class="item-name">{{ item.product?.name }}</span>
                  }
                  @if (order.items.length > 3) {
                    <span class="more-items">+{{ order.items.length - 3 }} more</span>
                  }
                </div>
              </mat-card-content>

              <mat-card-actions>
                <button mat-button color="primary">
                  <mat-icon>visibility</mat-icon>
                  View Details
                </button>
                
                @if (order.status === 'pending' || order.status === 'confirmed') {
                  <button mat-button color="warn" (click)="cancelOrder(order, $event)">
                    <mat-icon>cancel</mat-icon>
                    Cancel Order
                  </button>
                }
              </mat-card-actions>
            </mat-card>
          }
        </div>

        <!-- Pagination -->
        <app-pagination
          [totalItems]="totalOrders"
          [currentPage]="currentPage"
          [pageSize]="pageSize"
          (pageChange)="onPageChange($event)"
          (pageSizeChange)="onPageSizeChange($event)">
        </app-pagination>
      }
    </div>
  `,
  styles: [`
    .orders-container {
      max-width: 1000px;
      margin: 0 auto;
      padding: 2rem 1rem;
    }

    .page-header {
      margin-bottom: 2rem;
      
      h1 {
        margin: 0 0 0.5rem;
        font-size: 2rem;
      }
      
      p {
        color: #666;
        margin: 0;
      }
    }

    .filters-section {
      margin-bottom: 2rem;
    }

    .empty-state {
      text-align: center;
      padding: 4rem 2rem;
      
      mat-icon {
        font-size: 80px;
        width: 80px;
        height: 80px;
        color: #ccc;
        margin-bottom: 1rem;
      }
      
      h2 {
        margin: 0 0 0.5rem;
        color: #666;
      }
      
      p {
        color: #999;
        margin-bottom: 2rem;
      }
      
      button mat-icon {
        margin-right: 0.5rem;
      }
    }

    .orders-list {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .order-card {
      cursor: pointer;
      transition: box-shadow 0.2s;
      
      &:hover {
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
      }
      
      .order-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        
        .order-number {
          font-size: 1.125rem;
          font-weight: 600;
        }
      }
      
      .order-info {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin-bottom: 1rem;
        
        .info-item {
          display: flex;
          gap: 0.75rem;
          
          mat-icon {
            color: #3f51b5;
          }
          
          div {
            strong {
              display: block;
              font-size: 0.875rem;
              margin-bottom: 0.25rem;
            }
            
            p {
              margin: 0;
              color: #666;
              font-size: 0.875rem;
            }
          }
        }
      }
      
      .items-preview {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 1rem;
        
        .item-name {
          font-size: 0.875rem;
          color: #666;
          padding: 0.25rem 0.75rem;
          background: #f5f5f5;
          border-radius: 4px;
        }
        
        .more-items {
          font-size: 0.875rem;
          color: #3f51b5;
          font-weight: 600;
        }
      }
    }

    mat-card-actions {
      display: flex;
      gap: 0.5rem;
      
      button mat-icon {
        margin-right: 0.25rem;
        font-size: 18px;
        width: 18px;
        height: 18px;
      }
    }
  `]
})
export class OrdersComponent implements OnInit {
  orders: Order[] = [];
  loading = false;
  error: string | null = null;
  
  totalOrders = 0;
  currentPage = 1;
  pageSize = 10;
  selectedStatus: OrderStatus | undefined;

  constructor(
    private orderService: OrderService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadOrders();
  }

  loadOrders(): void {
    this.loading = true;
    this.error = null;

    this.orderService.getUserOrders({
      page: this.currentPage,
      limit: this.pageSize,
      status: this.selectedStatus
    }).subscribe({
      next: (response) => {
        this.orders = response.data;
        this.totalOrders = response.meta.total;
        this.loading = false;
      },
      error: (error) => {
        this.error = error.message;
        this.loading = false;
      }
    });
  }

  filterByStatus(status: OrderStatus | undefined): void {
    this.selectedStatus = status;
    this.currentPage = 1;
    this.loadOrders();
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadOrders();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  onPageSizeChange(size: number): void {
    this.pageSize = size;
    this.currentPage = 1;
    this.loadOrders();
  }

  cancelOrder(order: Order, event: Event): void {
    event.stopPropagation();
    
    // Would open confirmation dialog here
    console.log('Cancel order:', order.id);
  }

  getStatusColor(status: OrderStatus): 'primary' | 'accent' | 'warn' | undefined {
    switch (status) {
      case 'completed':
      case 'delivered':
        return 'accent';
      case 'cancelled':
        return 'warn';
      case 'processing':
      case 'printing':
        return 'primary';
      default:
        return undefined;
    }
  }
}

