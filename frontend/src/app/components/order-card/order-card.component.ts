import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MaterialModule } from '../../shared/material.module';
import { Order, OrderStatus } from '../../models/order.model';

@Component({
  selector: 'app-order-card',
  standalone: true,
  imports: [CommonModule, RouterModule, MaterialModule],
  template: `
    <mat-card class="order-card" [class.clickable]="viewDetails.observed" (click)="onViewDetails()">
      <!-- Header -->
      <mat-card-header>
        <mat-card-title>
          <div class="order-header">
            <div class="order-info">
              <span class="order-number">#{{ order.order_number }}</span>
              <span class="order-date">{{ order.order_date | date:'medium' }}</span>
            </div>
            <mat-chip [color]="getStatusColor(order.status)">
              {{ order.status }}
            </mat-chip>
          </div>
        </mat-card-title>
      </mat-card-header>

      <!-- Content -->
      <mat-card-content>
        <!-- Progress Timeline -->
        @if (showTimeline) {
          <div class="status-timeline">
            <div class="timeline-step" [class.active]="isStatusActive('pending')" [class.completed]="isStatusCompleted('pending')">
              <div class="step-marker"></div>
              <span class="step-label">Pending</span>
            </div>
            <div class="timeline-line" [class.completed]="isStatusCompleted('confirmed')"></div>
            <div class="timeline-step" [class.active]="isStatusActive('confirmed')" [class.completed]="isStatusCompleted('confirmed')">
              <div class="step-marker"></div>
              <span class="step-label">Confirmed</span>
            </div>
            <div class="timeline-line" [class.completed]="isStatusCompleted('processing')"></div>
            <div class="timeline-step" [class.active]="isStatusActive('processing')" [class.completed]="isStatusCompleted('processing')">
              <div class="step-marker"></div>
              <span class="step-label">Processing</span>
            </div>
            <div class="timeline-line" [class.completed]="isStatusCompleted('shipped')"></div>
            <div class="timeline-step" [class.active]="isStatusActive('shipped')" [class.completed]="isStatusCompleted('shipped')">
              <div class="step-marker"></div>
              <span class="step-label">Shipped</span>
            </div>
            <div class="timeline-line" [class.completed]="isStatusCompleted('delivered')"></div>
            <div class="timeline-step" [class.active]="isStatusActive('delivered')" [class.completed]="isStatusCompleted('delivered')">
              <div class="step-marker"></div>
              <span class="step-label">Delivered</span>
            </div>
          </div>
        }

        <!-- Order Details -->
        <div class="order-details">
          <div class="detail-item">
            <mat-icon>shopping_bag</mat-icon>
            <div>
              <span class="label">Items</span>
              <span class="value">{{ order.items.length }}</span>
            </div>
          </div>

          <div class="detail-item">
            <mat-icon>attach_money</mat-icon>
            <div>
              <span class="label">Total</span>
              <span class="value">{{ order.total_amount }} {{ order.currency }}</span>
            </div>
          </div>

          <div class="detail-item">
            <mat-icon>payment</mat-icon>
            <div>
              <span class="label">Payment</span>
              <span class="value">{{ order.payment_status }}</span>
            </div>
          </div>

          @if (order.expected_delivery) {
            <div class="detail-item">
              <mat-icon>local_shipping</mat-icon>
              <div>
                <span class="label">Expected</span>
                <span class="value">{{ order.expected_delivery | date:'shortDate' }}</span>
              </div>
            </div>
          }
        </div>

        <!-- Item Preview -->
        @if (order.items.length > 0) {
          <div class="items-preview">
            @for (item of order.items.slice(0, 2); track item.id) {
              <div class="preview-item">
                @if (item.product?.image_url) {
                  <img [src]="item.product.image_url" [alt]="item.product.name">
                } @else {
                  <div class="preview-placeholder">
                    <mat-icon>image</mat-icon>
                  </div>
                }
              </div>
            }
            @if (order.items.length > 2) {
              <div class="more-items">
                +{{ order.items.length - 2 }} more
              </div>
            }
          </div>
        }
      </mat-card-content>

      <!-- Actions -->
      @if (showActions) {
        <mat-card-actions>
          <button mat-button color="primary" (click)="onViewDetails($event)">
            <mat-icon>visibility</mat-icon>
            View Details
          </button>
          
          @if (order.status === 'pending' || order.status === 'confirmed') {
            <button mat-button color="warn" (click)="onCancelOrder($event)">
              <mat-icon>cancel</mat-icon>
              Cancel
            </button>
          }
          
          <button mat-icon-button (click)="onDownloadInvoice($event)" matTooltip="Download Invoice">
            <mat-icon>download</mat-icon>
          </button>
        </mat-card-actions>
      }
    </mat-card>
  `,
  styles: [`
    .order-card {
      transition: box-shadow 0.3s;
      
      &.clickable {
        cursor: pointer;
        
        &:hover {
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
      }
    }

    .order-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      
      .order-info {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        
        .order-number {
          font-size: 1.125rem;
          font-weight: 600;
        }
        
        .order-date {
          font-size: 0.875rem;
          color: #666;
        }
      }
    }

    .status-timeline {
      display: flex;
      align-items: center;
      margin: 1.5rem 0;
      padding: 1rem;
      background: #f9f9f9;
      border-radius: 8px;
      overflow-x: auto;
      
      .timeline-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        position: relative;
        
        .step-marker {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: #e0e0e0;
          border: 3px solid white;
          box-shadow: 0 0 0 2px #e0e0e0;
          transition: all 0.3s;
        }
        
        .step-label {
          font-size: 0.75rem;
          color: #999;
          white-space: nowrap;
          transition: color 0.3s;
        }
        
        &.active {
          .step-marker {
            background: #3f51b5;
            box-shadow: 0 0 0 2px #3f51b5, 0 0 0 4px #e3f2fd;
          }
          
          .step-label {
            color: #3f51b5;
            font-weight: 600;
          }
        }
        
        &.completed {
          .step-marker {
            background: #4caf50;
            box-shadow: 0 0 0 2px #4caf50;
            
            &::after {
              content: '✓';
              position: absolute;
              color: white;
              font-weight: bold;
              font-size: 14px;
              top: 50%;
              left: 50%;
              transform: translate(-50%, -50%);
            }
          }
          
          .step-label {
            color: #4caf50;
          }
        }
      }
      
      .timeline-line {
        height: 2px;
        flex: 1;
        min-width: 30px;
        background: #e0e0e0;
        margin-bottom: 24px;
        transition: background 0.3s;
        
        &.completed {
          background: #4caf50;
        }
      }
    }

    .order-details {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 1rem;
      margin-bottom: 1rem;
      
      .detail-item {
        display: flex;
        gap: 0.75rem;
        
        mat-icon {
          color: #3f51b5;
          flex-shrink: 0;
        }
        
        div {
          display: flex;
          flex-direction: column;
          
          .label {
            font-size: 0.75rem;
            color: #999;
            margin-bottom: 0.25rem;
          }
          
          .value {
            font-weight: 600;
          }
        }
      }
    }

    .items-preview {
      display: flex;
      gap: 0.5rem;
      align-items: center;
      
      .preview-item {
        img {
          width: 60px;
          height: 60px;
          object-fit: cover;
          border-radius: 4px;
        }
        
        .preview-placeholder {
          width: 60px;
          height: 60px;
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
      
      .more-items {
        font-size: 0.875rem;
        color: #3f51b5;
        font-weight: 600;
      }
    }

    mat-card-actions {
      display: flex;
      gap: 0.5rem;
      
      button mat-icon {
        font-size: 18px;
        width: 18px;
        height: 18px;
      }
    }
  `]
})
export class OrderCardComponent {
  @Input() order!: Order;
  @Input() showTimeline: boolean = true;
  @Input() showActions: boolean = true;
  
  @Output() viewDetails = new EventEmitter<Order>();
  @Output() cancelOrder = new EventEmitter<Order>();
  @Output() downloadInvoice = new EventEmitter<Order>();

  private statusOrder: OrderStatus[] = ['pending', 'confirmed', 'processing', 'shipped', 'delivered'];

  onViewDetails(event?: Event): void {
    if (event) {
      event.stopPropagation();
    }
    this.viewDetails.emit(this.order);
  }

  onCancelOrder(event: Event): void {
    event.stopPropagation();
    this.cancelOrder.emit(this.order);
  }

  onDownloadInvoice(event: Event): void {
    event.stopPropagation();
    this.downloadInvoice.emit(this.order);
  }

  isStatusActive(status: OrderStatus): boolean {
    return this.order.status === status;
  }

  isStatusCompleted(status: OrderStatus): boolean {
    const currentIndex = this.statusOrder.indexOf(this.order.status);
    const statusIndex = this.statusOrder.indexOf(status);
    return currentIndex > statusIndex;
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
      case 'shipped':
        return 'primary';
      default:
        return undefined;
    }
  }
}

