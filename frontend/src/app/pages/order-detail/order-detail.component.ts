import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute } from '@angular/router';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { MaterialModule } from '../../shared/material.module';
import { LoadingComponent } from '../../shared/components/loading/loading.component';
import { ErrorComponent } from '../../shared/components/error/error.component';
import { OrderService } from '../../services/order.service';
import { WebSocketService } from '../../services/websocket.service';
import { Order, OrderTimeline } from '../../models/order.model';

@Component({
  selector: 'app-order-detail',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MaterialModule,
    LoadingComponent,
    ErrorComponent
  ],
  template: `
    <div class="order-detail-container">
      @if (loading) {
        <app-loading type="skeleton"></app-loading>
      } @else if (error) {
        <app-error [message]="error" (retry)="loadOrder()"></app-error>
      } @else if (order) {
        <!-- Header -->
        <div class="order-header">
          <div>
            <h1>Order #{{ order.order_number }}</h1>
            <p class="order-date">Placed on {{ order.order_date | date:'medium' }}</p>
          </div>
          
          <mat-chip [color]="getStatusColor(order.status)">
            {{ order.status }}
          </mat-chip>
        </div>

        <div class="order-content">
          <!-- Left Column -->
          <div class="main-content">
            <!-- Order Items -->
            <mat-card class="section-card">
              <mat-card-header>
                <mat-card-title>Order Items</mat-card-title>
              </mat-card-header>
              <mat-card-content>
                @for (item of order.items; track item.id) {
                  <div class="order-item">
                    <div class="item-image">
                      @if (item.product?.image_url) {
                        <img [src]="item.product.image_url" [alt]="item.product.name">
                      } @else {
                        <div class="placeholder">
                          <mat-icon>inventory_2</mat-icon>
                        </div>
                      }
                    </div>
                    
                    <div class="item-info">
                      <h4>{{ item.product?.name }}</h4>
                      <p class="item-details">Quantity: {{ item.quantity }}</p>
                      <p class="item-price">{{ item.unit_price }} {{ order.currency }} each</p>
                    </div>
                    
                    <div class="item-total">
                      <p class="total-price">{{ item.total_price }} {{ order.currency }}</p>
                    </div>
                  </div>
                }
              </mat-card-content>
            </mat-card>

            <!-- Order Timeline -->
            @if (timeline.length > 0) {
              <mat-card class="section-card">
                <mat-card-header>
                  <mat-card-title>Order Timeline</mat-card-title>
                </mat-card-header>
                <mat-card-content>
                  <div class="timeline">
                    @for (event of timeline; track event.timestamp) {
                      <div class="timeline-item">
                        <div class="timeline-marker"></div>
                        <div class="timeline-content">
                          <h4>{{ event.status }}</h4>
                          <p class="timeline-message">{{ event.message }}</p>
                          <p class="timeline-date">{{ event.timestamp | date:'medium' }}</p>
                        </div>
                      </div>
                    }
                  </div>
                </mat-card-content>
              </mat-card>
            }

            <!-- Shipping Address -->
            @if (order.shipping_address) {
              <mat-card class="section-card">
                <mat-card-header>
                  <mat-card-title>Shipping Address</mat-card-title>
                </mat-card-header>
                <mat-card-content>
                  <div class="address-content">
                    <mat-icon>location_on</mat-icon>
                    <div>
                      <p>{{ order.shipping_address.street }}</p>
                      <p>{{ order.shipping_address.city }}, {{ order.shipping_address.state }} {{ order.shipping_address.postal_code }}</p>
                      <p>{{ order.shipping_address.country }}</p>
                    </div>
                  </div>
                </mat-card-content>
              </mat-card>
            }
          </div>

          <!-- Right Column - Summary -->
          <div class="sidebar">
            <mat-card class="summary-card">
              <mat-card-header>
                <mat-card-title>Order Summary</mat-card-title>
              </mat-card-header>
              <mat-card-content>
                <div class="summary-row">
                  <span>Subtotal</span>
                  <span>{{ calculateSubtotal() }} {{ order.currency }}</span>
                </div>
                
                @if (hasPackaging()) {
                  <div class="summary-row">
                    <span>Packaging</span>
                    <span>{{ calculatePackaging() }} {{ order.currency }}</span>
                  </div>
                }
                
                <div class="summary-row">
                  <span>Shipping</span>
                  <span>0.00 {{ order.currency }}</span>
                </div>
                
                <mat-divider></mat-divider>
                
                <div class="summary-row total">
                  <span>Total</span>
                  <span>{{ order.total_amount }} {{ order.currency }}</span>
                </div>
              </mat-card-content>
            </mat-card>

            <!-- Payment Information -->
            <mat-card class="info-card">
              <mat-card-header>
                <mat-card-title>Payment Information</mat-card-title>
              </mat-card-header>
              <mat-card-content>
                <div class="info-row">
                  <mat-icon>payment</mat-icon>
                  <div>
                    <p class="label">Payment Method</p>
                    <p class="value">{{ order.payment_method || 'Not specified' }}</p>
                  </div>
                </div>
                
                <div class="info-row">
                  <mat-icon>receipt</mat-icon>
                  <div>
                    <p class="label">Payment Status</p>
                    <p class="value">{{ order.payment_status }}</p>
                  </div>
                </div>
              </mat-card-content>
            </mat-card>

            <!-- Actions -->
            <div class="action-buttons">
              <button mat-raised-button class="action-btn" (click)="downloadInvoice()">
                <mat-icon>download</mat-icon>
                Download Invoice
              </button>
              
              @if (order.status === 'pending' || order.status === 'confirmed') {
                <button mat-raised-button color="warn" class="action-btn" (click)="cancelOrder()">
                  <mat-icon>cancel</mat-icon>
                  Cancel Order
                </button>
              }
              
              <button mat-button routerLink="/orders" class="action-btn">
                <mat-icon>arrow_back</mat-icon>
                Back to Orders
              </button>
            </div>
          </div>
        </div>
      }
    </div>
  `,
  styles: [`
    .order-detail-container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem 1rem;
    }

    .order-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 2rem;
      
      h1 {
        margin: 0 0 0.5rem;
        font-size: 2rem;
      }
      
      .order-date {
        color: #666;
        margin: 0;
      }
    }

    .order-content {
      display: grid;
      grid-template-columns: 1fr 400px;
      gap: 2rem;
      
      @media (max-width: 968px) {
        grid-template-columns: 1fr;
      }
    }

    .main-content,
    .sidebar {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .section-card {
      .order-item {
        display: grid;
        grid-template-columns: 80px 1fr auto;
        gap: 1rem;
        padding: 1rem 0;
        border-bottom: 1px solid #f0f0f0;
        
        &:last-child {
          border-bottom: none;
        }
        
        .item-image {
          img {
            width: 80px;
            height: 80px;
            object-fit: cover;
            border-radius: 4px;
          }
          
          .placeholder {
            width: 80px;
            height: 80px;
            background: #f5f5f5;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            
            mat-icon {
              color: #999;
            }
          }
        }
        
        .item-info {
          h4 {
            margin: 0 0 0.5rem;
          }
          
          .item-details {
            color: #666;
            font-size: 0.875rem;
            margin: 0 0 0.25rem;
          }
          
          .item-price {
            color: #3f51b5;
            margin: 0;
          }
        }
        
        .item-total {
          text-align: right;
          
          .total-price {
            font-size: 1.125rem;
            font-weight: 600;
            color: #3f51b5;
            margin: 0;
          }
        }
      }
    }

    .timeline {
      position: relative;
      padding-left: 2rem;
      
      &::before {
        content: '';
        position: absolute;
        left: 8px;
        top: 8px;
        bottom: 8px;
        width: 2px;
        background: #e0e0e0;
      }
      
      .timeline-item {
        position: relative;
        padding-bottom: 1.5rem;
        
        &:last-child {
          padding-bottom: 0;
        }
        
        .timeline-marker {
          position: absolute;
          left: -2rem;
          width: 18px;
          height: 18px;
          border-radius: 50%;
          background: #3f51b5;
          border: 3px solid white;
          box-shadow: 0 0 0 2px #e0e0e0;
        }
        
        .timeline-content {
          h4 {
            margin: 0 0 0.25rem;
            text-transform: capitalize;
          }
          
          .timeline-message {
            color: #666;
            font-size: 0.875rem;
            margin: 0 0 0.25rem;
          }
          
          .timeline-date {
            color: #999;
            font-size: 0.75rem;
            margin: 0;
          }
        }
      }
    }

    .address-content {
      display: flex;
      gap: 1rem;
      
      mat-icon {
        color: #3f51b5;
        flex-shrink: 0;
      }
      
      p {
        margin: 0.25rem 0;
        color: #666;
      }
    }

    .summary-card {
      .summary-row {
        display: flex;
        justify-content: space-between;
        padding: 0.75rem 0;
        
        &.total {
          font-size: 1.25rem;
          font-weight: 600;
          margin-top: 0.5rem;
          
          span:last-child {
            color: #3f51b5;
          }
        }
      }
      
      mat-divider {
        margin: 1rem 0;
      }
    }

    .info-card {
      .info-row {
        display: flex;
        gap: 1rem;
        padding: 0.75rem 0;
        
        mat-icon {
          color: #3f51b5;
          flex-shrink: 0;
        }
        
        .label {
          font-size: 0.875rem;
          color: #999;
          margin: 0 0 0.25rem;
        }
        
        .value {
          margin: 0;
          font-weight: 600;
        }
      }
    }

    .action-buttons {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      
      .action-btn {
        width: 100%;
        
        mat-icon {
          margin-right: 0.5rem;
        }
      }
    }
  `]
})
export class OrderDetailComponent implements OnInit, OnDestroy {
  order: Order | null = null;
  timeline: OrderTimeline[] = [];
  
  loading = false;
  error: string | null = null;
  
  private destroy$ = new Subject<void>();

  constructor(
    private route: ActivatedRoute,
    private orderService: OrderService,
    private wsService: WebSocketService
  ) {}

  ngOnInit(): void {
    this.route.params.pipe(takeUntil(this.destroy$)).subscribe(params => {
      const orderId = params['id'];
      if (orderId) {
        this.loadOrder(orderId);
        this.loadTimeline(orderId);
        this.subscribeToOrderUpdates(orderId);
      }
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadOrder(id?: string): void {
    const orderId = id || this.route.snapshot.params['id'];
    this.loading = true;
    this.error = null;

    this.orderService.getOrder(orderId).subscribe({
      next: (order) => {
        this.order = order;
        this.loading = false;
      },
      error: (error) => {
        this.error = error.message;
        this.loading = false;
      }
    });
  }

  loadTimeline(orderId: string): void {
    this.orderService.getOrderTimeline(orderId).subscribe({
      next: (timeline) => {
        this.timeline = timeline;
      },
      error: (error) => {
        console.error('Failed to load timeline:', error);
      }
    });
  }

  subscribeToOrderUpdates(orderId: string): void {
    this.wsService.subscribeToOrderUpdates(orderId)
      .pipe(takeUntil(this.destroy$))
      .subscribe(update => {
        if (this.order) {
          this.order.status = update.status;
          // Reload timeline to get latest events
          this.loadTimeline(orderId);
        }
      });
  }

  calculateSubtotal(): number {
    if (!this.order) return 0;
    return this.order.items.reduce((sum, item) => sum + item.total_price, 0);
  }

  calculatePackaging(): number {
    // Calculate packaging cost from items
    return 0; // Would be calculated based on items with packaging
  }

  downloadInvoice(): void {
    if (!this.order) return;

    this.orderService.downloadInvoice(this.order.id).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `invoice_${this.order!.order_number}.pdf`;
        link.click();
        window.URL.revokeObjectURL(url);
      },
      error: (error) => {
        console.error('Failed to download invoice:', error);
      }
    });
  }

  cancelOrder(): void {
    if (!this.order) return;

    this.orderService.cancelOrder(this.order.id).subscribe({
      next: (order) => {
        this.order = order;
      },
      error: (error) => {
        console.error('Failed to cancel order:', error);
      }
    });
  }

  hasPackaging(): boolean {
    return this.order?.items.some(i => i.packaging_id) || false;
  }

  getStatusColor(status: string): 'primary' | 'accent' | 'warn' | undefined {
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

