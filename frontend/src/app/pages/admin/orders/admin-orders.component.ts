import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MaterialModule } from '../../../shared/material.module';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';
import { PaginationComponent } from '../../../shared/components/pagination/pagination.component';
import { SearchComponent } from '../../../shared/components/search/search.component';
import { OrderService } from '../../../services/order.service';
import { Order } from '../../../models/order.model';

@Component({
  selector: 'app-admin-orders',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MaterialModule,
    LoadingComponent,
    PaginationComponent,
    SearchComponent
  ],
  template: `
    <div class="admin-orders">
      <h1>Order Management</h1>

      <app-search
        placeholder="Search orders..."
        (search)="onSearch($event)">
      </app-search>

      @if (loading) {
        <app-loading type="skeleton"></app-loading>
      } @else {
        <div class="table-container">
          <table mat-table [dataSource]="orders" class="orders-table">
            <ng-container matColumnDef="order_number">
              <th mat-header-cell *matHeaderCellDef>Order #</th>
              <td mat-cell *matCellDef="let order">
                <a [routerLink]="['/orders', order.id]">{{ order.order_number }}</a>
              </td>
            </ng-container>

            <ng-container matColumnDef="customer">
              <th mat-header-cell *matHeaderCellDef>Customer</th>
              <td mat-cell *matCellDef="let order">{{ order.customer_id }}</td>
            </ng-container>

            <ng-container matColumnDef="date">
              <th mat-header-cell *matHeaderCellDef>Date</th>
              <td mat-cell *matCellDef="let order">{{ order.order_date | date:'short' }}</td>
            </ng-container>

            <ng-container matColumnDef="total">
              <th mat-header-cell *matHeaderCellDef>Total</th>
              <td mat-cell *matCellDef="let order">
                {{ order.total_amount }} {{ order.currency }}
              </td>
            </ng-container>

            <ng-container matColumnDef="payment_status">
              <th mat-header-cell *matHeaderCellDef>Payment</th>
              <td mat-cell *matCellDef="let order">
                <mat-chip>{{ order.payment_status }}</mat-chip>
              </td>
            </ng-container>

            <ng-container matColumnDef="status">
              <th mat-header-cell *matHeaderCellDef>Status</th>
              <td mat-cell *matCellDef="let order">
                <mat-chip [color]="getStatusColor(order.status)">
                  {{ order.status }}
                </mat-chip>
              </td>
            </ng-container>

            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef>Actions</th>
              <td mat-cell *matCellDef="let order">
                <button mat-icon-button [matMenuTriggerFor]="menu">
                  <mat-icon>more_vert</mat-icon>
                </button>
                <mat-menu #menu="matMenu">
                  <button mat-menu-item [routerLink]="['/orders', order.id]">
                    <mat-icon>visibility</mat-icon>
                    View Details
                  </button>
                  <button mat-menu-item>
                    <mat-icon>edit</mat-icon>
                    Update Status
                  </button>
                  <button mat-menu-item>
                    <mat-icon>download</mat-icon>
                    Download Invoice
                  </button>
                </mat-menu>
              </td>
            </ng-container>

            <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
            <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
          </table>
        </div>

        <app-pagination
          [totalItems]="totalOrders"
          [currentPage]="currentPage"
          [pageSize]="pageSize"
          (pageChange)="onPageChange($event)">
        </app-pagination>
      }
    </div>
  `,
  styles: [`
    .admin-orders {
      h1 {
        margin: 0 0 2rem;
      }
    }

    .table-container {
      background: white;
      border-radius: 8px;
      margin: 2rem 0;
      overflow: auto;
    }

    .orders-table {
      width: 100%;
      
      a {
        color: #3f51b5;
        text-decoration: none;
        font-weight: 600;
        
        &:hover {
          text-decoration: underline;
        }
      }
    }
  `]
})
export class AdminOrdersComponent implements OnInit {
  orders: Order[] = [];
  loading = false;
  totalOrders = 0;
  currentPage = 1;
  pageSize = 20;
  
  displayedColumns = ['order_number', 'customer', 'date', 'total', 'payment_status', 'status', 'actions'];

  constructor(private orderService: OrderService) {}

  ngOnInit(): void {
    this.loadOrders();
  }

  loadOrders(): void {
    this.loading = true;
    
    this.orderService.getAllOrders({ page: this.currentPage, limit: this.pageSize }).subscribe({
      next: (response) => {
        this.orders = response.data;
        this.totalOrders = response.meta.total;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  onSearch(query: string): void {
    // Implement search
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadOrders();
  }

  getStatusColor(status: string): 'primary' | 'accent' | 'warn' | undefined {
    switch (status) {
      case 'completed':
      case 'delivered':
        return 'accent';
      case 'cancelled':
        return 'warn';
      default:
        return 'primary';
    }
  }
}

