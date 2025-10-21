import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../../../shared/material.module';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, MaterialModule, LoadingComponent],
  template: `
    <div class="admin-dashboard">
      <h1>Admin Dashboard</h1>
      
      <!-- Key Metrics -->
      <div class="metrics-grid">
        <mat-card class="metric-card">
          <mat-card-content>
            <div class="metric-icon">
              <mat-icon color="primary">shopping_bag</mat-icon>
            </div>
            <div class="metric-info">
              <p class="metric-value">{{ totalOrders }}</p>
              <p class="metric-label">Total Orders</p>
            </div>
          </mat-card-content>
        </mat-card>

        <mat-card class="metric-card">
          <mat-card-content>
            <div class="metric-icon">
              <mat-icon color="accent">attach_money</mat-icon>
            </div>
            <div class="metric-info">
              <p class="metric-value">\${{ totalRevenue.toLocaleString() }}</p>
              <p class="metric-label">Total Revenue</p>
            </div>
          </mat-card-content>
        </mat-card>

        <mat-card class="metric-card">
          <mat-card-content>
            <div class="metric-icon">
              <mat-icon color="warn">people</mat-icon>
            </div>
            <div class="metric-info">
              <p class="metric-value">{{ totalUsers }}</p>
              <p class="metric-label">Total Users</p>
            </div>
          </mat-card-content>
        </mat-card>

        <mat-card class="metric-card">
          <mat-card-content>
            <div class="metric-icon">
              <mat-icon style="color: #4caf50;">print</mat-icon>
            </div>
            <div class="metric-info">
              <p class="metric-value">{{ activePrintJobs }}</p>
              <p class="metric-label">Active Print Jobs</p>
            </div>
          </mat-card-content>
        </mat-card>
      </div>

      <!-- Charts Section -->
      <div class="charts-section">
        <mat-card>
          <mat-card-header>
            <mat-card-title>Sales Overview</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="chart-placeholder">
              <mat-icon>bar_chart</mat-icon>
              <p>Sales chart will be displayed here</p>
            </div>
          </mat-card-content>
        </mat-card>

        <mat-card>
          <mat-card-header>
            <mat-card-title>Print Queue Status</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="chart-placeholder">
              <mat-icon>donut_large</mat-icon>
              <p>Print queue chart will be displayed here</p>
            </div>
          </mat-card-content>
        </mat-card>
      </div>

      <!-- Recent Activity -->
      <mat-card class="recent-activity">
        <mat-card-header>
          <mat-card-title>Recent Activity</mat-card-title>
        </mat-card-header>
        <mat-card-content>
          <mat-list>
            <mat-list-item>
              <mat-icon matListItemIcon>shopping_cart</mat-icon>
              <div matListItemTitle>New order #12345</div>
              <div matListItemLine>2 minutes ago</div>
            </mat-list-item>
            <mat-list-item>
              <mat-icon matListItemIcon>person_add</mat-icon>
              <div matListItemTitle>New user registered</div>
              <div matListItemLine>15 minutes ago</div>
            </mat-list-item>
            <mat-list-item>
              <mat-icon matListItemIcon>check_circle</mat-icon>
              <div matListItemTitle>Print job completed</div>
              <div matListItemLine>1 hour ago</div>
            </mat-list-item>
          </mat-list>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .admin-dashboard {
      h1 {
        margin: 0 0 2rem;
      }
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
    }

    .metric-card {
      mat-card-content {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        padding: 1.5rem;
        
        .metric-icon mat-icon {
          font-size: 48px;
          width: 48px;
          height: 48px;
        }
        
        .metric-info {
          .metric-value {
            margin: 0 0 0.25rem;
            font-size: 2rem;
            font-weight: 600;
          }
          
          .metric-label {
            margin: 0;
            color: #666;
            font-size: 0.875rem;
          }
        }
      }
    }

    .charts-section {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 1.5rem;
      margin-bottom: 2rem;
      
      @media (max-width: 968px) {
        grid-template-columns: 1fr;
      }
      
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
  `]
})
export class AdminDashboardComponent implements OnInit {
  totalOrders = 1234;
  totalRevenue = 45678;
  totalUsers = 567;
  activePrintJobs = 23;

  ngOnInit(): void {
    // Load admin statistics
  }
}

