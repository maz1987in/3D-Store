import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MaterialModule } from '../../shared/material.module';
import { LoadingComponent } from '../../shared/components/loading/loading.component';
import { AuthService } from '../../core/services/auth.service';
import { OrderService } from '../../services/order.service';
import { PrintJobService } from '../../services/print-job.service';
import { User } from '../../models/user.model';
import { Order } from '../../models/order.model';
import { PrintJob } from '../../models/print-job.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MaterialModule,
    LoadingComponent
  ],
  template: `
    <div class="dashboard-container">
      <div class="page-header">
        <h1>Dashboard</h1>
        @if (user) {
          <p>Welcome back, {{ user.first_name }}!</p>
        }
      </div>

      <!-- Stats Cards -->
      <div class="stats-grid">
        <mat-card class="stat-card">
          <mat-card-content>
            <div class="stat-icon">
              <mat-icon color="primary">shopping_bag</mat-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">Total Orders</p>
              <p class="stat-value">{{ totalOrders }}</p>
            </div>
          </mat-card-content>
        </mat-card>

        <mat-card class="stat-card">
          <mat-card-content>
            <div class="stat-icon">
              <mat-icon color="accent">print</mat-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">Print Jobs</p>
              <p class="stat-value">{{ totalPrintJobs }}</p>
            </div>
          </mat-card-content>
        </mat-card>

        <mat-card class="stat-card">
          <mat-card-content>
            <div class="stat-icon">
              <mat-icon color="warn">hourglass_empty</mat-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">Pending Orders</p>
              <p class="stat-value">{{ pendingOrders }}</p>
            </div>
          </mat-card-content>
        </mat-card>

        <mat-card class="stat-card">
          <mat-card-content>
            <div class="stat-icon">
              <mat-icon style="color: #4caf50;">check_circle</mat-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">Completed</p>
              <p class="stat-value">{{ completedOrders }}</p>
            </div>
          </mat-card-content>
        </mat-card>
      </div>

      <div class="dashboard-content">
        <!-- Recent Orders -->
        <div class="dashboard-section">
          <mat-card>
            <mat-card-header>
              <mat-card-title>Recent Orders</mat-card-title>
              <button mat-button routerLink="/orders">View All</button>
            </mat-card-header>
            
            <mat-card-content>
              @if (loadingOrders) {
                <app-loading type="spinner"></app-loading>
              } @else if (recentOrders.length > 0) {
                <div class="orders-list">
                  @for (order of recentOrders; track order.id) {
                    <div class="order-item" [routerLink]="['/orders', order.id]">
                      <div class="order-info">
                        <p class="order-number">#{{ order.order_number }}</p>
                        <p class="order-date">{{ order.order_date | date:'short' }}</p>
                      </div>
                      <div class="order-status">
                        <mat-chip [color]="getStatusColor(order.status)">
                          {{ order.status }}
                        </mat-chip>
                      </div>
                      <div class="order-total">
                        <p>{{ order.total_amount }} {{ order.currency }}</p>
                      </div>
                    </div>
                  }
                </div>
              } @else {
                <div class="empty-message">
                  <p>No orders yet</p>
                  <button mat-raised-button color="primary" routerLink="/products">
                    Start Shopping
                  </button>
                </div>
              }
            </mat-card-content>
          </mat-card>
        </div>

        <!-- Active Print Jobs -->
        <div class="dashboard-section">
          <mat-card>
            <mat-card-header>
              <mat-card-title>Active Print Jobs</mat-card-title>
              <button mat-button routerLink="/print-jobs">View All</button>
            </mat-card-header>
            
            <mat-card-content>
              @if (loadingPrintJobs) {
                <app-loading type="spinner"></app-loading>
              } @else if (activePrintJobs.length > 0) {
                <div class="print-jobs-list">
                  @for (job of activePrintJobs; track job.id) {
                    <div class="print-job-item">
                      <div class="job-info">
                        <p class="job-material">{{ job.material_name }}</p>
                        <p class="job-quality">{{ job.quality }} quality</p>
                      </div>
                      <div class="job-progress">
                        <mat-progress-bar 
                          mode="determinate" 
                          [value]="job.progress">
                        </mat-progress-bar>
                        <p class="progress-text">{{ job.progress }}%</p>
                      </div>
                      <div class="job-status">
                        <mat-chip>{{ job.status }}</mat-chip>
                      </div>
                    </div>
                  }
                </div>
              } @else {
                <div class="empty-message">
                  <p>No active print jobs</p>
                  <button mat-raised-button color="primary" routerLink="/print-jobs">
                    Upload Model
                  </button>
                </div>
              }
            </mat-card-content>
          </mat-card>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions">
        <h2>Quick Actions</h2>
        <div class="actions-grid">
          <button mat-raised-button color="primary" routerLink="/products">
            <mat-icon>shopping_bag</mat-icon>
            Browse Products
          </button>
          
          <button mat-raised-button color="accent" routerLink="/print-jobs">
            <mat-icon>upload</mat-icon>
            Upload 3D Model
          </button>
          
          <button mat-raised-button routerLink="/profile">
            <mat-icon>person</mat-icon>
            Edit Profile
          </button>
          
          <button mat-raised-button routerLink="/orders">
            <mat-icon>receipt_long</mat-icon>
            View Orders
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-container {
      max-width: 1200px;
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

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
    }

    .stat-card {
      mat-card-content {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        padding: 1.5rem;
        
        .stat-icon {
          mat-icon {
            font-size: 48px;
            width: 48px;
            height: 48px;
          }
        }
        
        .stat-info {
          .stat-label {
            margin: 0 0 0.5rem;
            color: #666;
            font-size: 0.875rem;
          }
          
          .stat-value {
            margin: 0;
            font-size: 2rem;
            font-weight: 600;
          }
        }
      }
    }

    .dashboard-content {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 2rem;
      margin-bottom: 2rem;
      
      @media (max-width: 968px) {
        grid-template-columns: 1fr;
      }
    }

    .dashboard-section {
      mat-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
      }
      
      .orders-list,
      .print-jobs-list {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
      }
      
      .order-item {
        display: grid;
        grid-template-columns: 1fr auto auto;
        gap: 1rem;
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        cursor: pointer;
        transition: background 0.2s;
        
        &:hover {
          background: #f5f5f5;
        }
        
        .order-info {
          .order-number {
            margin: 0 0 0.25rem;
            font-weight: 600;
          }
          
          .order-date {
            margin: 0;
            color: #666;
            font-size: 0.875rem;
          }
        }
        
        .order-total {
          p {
            margin: 0;
            font-weight: 600;
            color: #3f51b5;
          }
        }
      }
      
      .print-job-item {
        display: grid;
        grid-template-columns: 1fr 2fr auto;
        gap: 1rem;
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        align-items: center;
        
        .job-info {
          .job-material {
            margin: 0 0 0.25rem;
            font-weight: 600;
          }
          
          .job-quality {
            margin: 0;
            font-size: 0.875rem;
            color: #666;
          }
        }
        
        .job-progress {
          .progress-text {
            margin: 0.5rem 0 0;
            font-size: 0.75rem;
            text-align: right;
            color: #666;
          }
        }
      }
      
      .empty-message {
        text-align: center;
        padding: 2rem;
        
        p {
          color: #666;
          margin-bottom: 1rem;
        }
      }
    }

    .quick-actions {
      h2 {
        margin-bottom: 1rem;
      }
      
      .actions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        
        button {
          height: 60px;
          
          mat-icon {
            margin-right: 0.5rem;
          }
        }
      }
    }
  `]
})
export class DashboardComponent implements OnInit {
  user: User | null = null;
  recentOrders: Order[] = [];
  activePrintJobs: PrintJob[] = [];
  
  totalOrders = 0;
  totalPrintJobs = 0;
  pendingOrders = 0;
  completedOrders = 0;
  
  loadingOrders = false;
  loadingPrintJobs = false;

  constructor(
    private authService: AuthService,
    private orderService: OrderService,
    private printJobService: PrintJobService
  ) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      this.user = user;
    });
    
    this.loadRecentOrders();
    this.loadActivePrintJobs();
    this.loadStatistics();
  }

  loadRecentOrders(): void {
    this.loadingOrders = true;
    
    this.orderService.getUserOrders({ page: 1, limit: 5 }).subscribe({
      next: (response) => {
        this.recentOrders = response.data;
        this.loadingOrders = false;
      },
      error: () => {
        this.loadingOrders = false;
      }
    });
  }

  loadActivePrintJobs(): void {
    this.loadingPrintJobs = true;
    
    this.printJobService.getUserPrintJobs({ page: 1, limit: 5, status: 'printing' }).subscribe({
      next: (response) => {
        this.activePrintJobs = response.data;
        this.loadingPrintJobs = false;
      },
      error: () => {
        this.loadingPrintJobs = false;
      }
    });
  }

  loadStatistics(): void {
    // Load order statistics
    this.orderService.getUserOrders({ page: 1, limit: 1 }).subscribe({
      next: (response) => {
        this.totalOrders = response.meta.total;
      }
    });

    this.orderService.getUserOrders({ page: 1, limit: 1, status: 'pending' }).subscribe({
      next: (response) => {
        this.pendingOrders = response.meta.total;
      }
    });

    this.orderService.getUserOrders({ page: 1, limit: 1, status: 'completed' }).subscribe({
      next: (response) => {
        this.completedOrders = response.meta.total;
      }
    });

    this.printJobService.getUserPrintJobs({ page: 1, limit: 1 }).subscribe({
      next: (response) => {
        this.totalPrintJobs = response.meta.total;
      }
    });
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

