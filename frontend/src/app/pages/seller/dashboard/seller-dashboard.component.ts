import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../../../shared/material.module';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';
import { SellerService } from '../../../services/seller.service';
import { SellerDashboard } from '../../../models/seller.model';

@Component({
  selector: 'app-seller-dashboard',
  standalone: true,
  imports: [CommonModule, MaterialModule, LoadingComponent],
  template: `
    <div class="seller-dashboard">
      <h1>Seller Dashboard</h1>

      @if (loading) {
        <app-loading type="skeleton"></app-loading>
      } @else if (dashboard) {
        <!-- Stats Cards -->
        <div class="stats-grid">
          <mat-card class="stat-card">
            <mat-card-content>
              <div class="stat-icon">
                <mat-icon color="primary">trending_up</mat-icon>
              </div>
              <div class="stat-info">
                <p class="stat-label">Current Period Sales</p>
                <p class="stat-value">{{ dashboard.current_period_sales }} OMR</p>
              </div>
            </mat-card-content>
          </mat-card>

          <mat-card class="stat-card">
            <mat-card-content>
              <div class="stat-icon">
                <mat-icon color="accent">attach_money</mat-icon>
              </div>
              <div class="stat-info">
                <p class="stat-label">Current Commission</p>
                <p class="stat-value">{{ dashboard.current_period_commission }} OMR</p>
              </div>
            </mat-card-content>
          </mat-card>

          <mat-card class="stat-card">
            <mat-card-content>
              <div class="stat-icon">
                <mat-icon color="warn">hourglass_empty</mat-icon>
              </div>
              <div class="stat-info">
                <p class="stat-label">Pending Commission</p>
                <p class="stat-value">{{ dashboard.pending_commission }} OMR</p>
              </div>
            </mat-card-content>
          </mat-card>

          <mat-card class="stat-card">
            <mat-card-content>
              <div class="stat-icon">
                <mat-icon style="color: #4caf50;">event</mat-icon>
              </div>
              <div class="stat-info">
                <p class="stat-label">Next Settlement</p>
                <p class="stat-value">{{ dashboard.next_settlement_date | date:'shortDate' }}</p>
              </div>
            </mat-card-content>
          </mat-card>
        </div>

        <!-- Performance Chart -->
        <mat-card class="chart-card">
          <mat-card-header>
            <mat-card-title>Performance Overview</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="chart-placeholder">
              <mat-icon>show_chart</mat-icon>
              <p>Performance chart will be displayed here</p>
            </div>
          </mat-card-content>
        </mat-card>

        <!-- Recent Orders -->
        <mat-card>
          <mat-card-header>
            <mat-card-title>Recent Orders</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            @if (dashboard.recent_orders.length > 0) {
              <mat-list>
                @for (order of dashboard.recent_orders; track order.id) {
                  <mat-list-item>
                    <mat-icon matListItemIcon>shopping_cart</mat-icon>
                    <div matListItemTitle>Order #{{ order.order_number }}</div>
                    <div matListItemLine>{{ order.total_amount }} OMR</div>
                  </mat-list-item>
                }
              </mat-list>
            } @else {
              <p class="empty-message">No recent orders</p>
            }
          </mat-card-content>
        </mat-card>
      }
    </div>
  `,
  styles: [`
    .seller-dashboard {
      h1 {
        margin: 0 0 2rem;
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
        
        .stat-icon mat-icon {
          font-size: 48px;
          width: 48px;
          height: 48px;
        }
        
        .stat-info {
          .stat-label {
            margin: 0 0 0.5rem;
            color: #666;
            font-size: 0.875rem;
          }
          
          .stat-value {
            margin: 0;
            font-size: 1.75rem;
            font-weight: 600;
          }
        }
      }
    }

    .chart-card {
      margin-bottom: 2rem;
      
      .chart-placeholder {
        height: 300px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: #f5f5f5;
        border-radius: 4px;
        
        mat-icon {
          font-size: 64px;
          width: 64px;
          height: 64px;
          color: #999;
          margin-bottom: 1rem;
        }
        
        p {
          color: #666;
          margin: 0;
        }
      }
    }

    .empty-message {
      text-align: center;
      padding: 2rem;
      color: #666;
    }
  `]
})
export class SellerDashboardComponent implements OnInit {
  dashboard: SellerDashboard | null = null;
  loading = false;

  constructor(private sellerService: SellerService) {}

  ngOnInit(): void {
    this.loadDashboard();
  }

  loadDashboard(): void {
    this.loading = true;
    
    this.sellerService.getSellerDashboard().subscribe({
      next: (dashboard) => {
        this.dashboard = dashboard;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }
}

