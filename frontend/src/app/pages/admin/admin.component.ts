import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MaterialModule } from '../../shared/material.module';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [CommonModule, RouterModule, MaterialModule],
  template: `
    <div class="admin-layout">
      <!-- Sidebar -->
      <mat-sidenav-container class="sidenav-container">
        <mat-sidenav mode="side" opened class="sidenav">
          <div class="sidenav-header">
            <h2>Admin Panel</h2>
          </div>
          
          <mat-nav-list>
            <a mat-list-item routerLink="/admin/dashboard" routerLinkActive="active">
              <mat-icon>dashboard</mat-icon>
              <span>Dashboard</span>
            </a>
            
            <a mat-list-item routerLink="/admin/products" routerLinkActive="active">
              <mat-icon>inventory_2</mat-icon>
              <span>Products</span>
            </a>
            
            <a mat-list-item routerLink="/admin/orders" routerLinkActive="active">
              <mat-icon>receipt_long</mat-icon>
              <span>Orders</span>
            </a>
            
            <a mat-list-item routerLink="/admin/users" routerLinkActive="active">
              <mat-icon>people</mat-icon>
              <span>Users</span>
            </a>
            
            <a mat-list-item routerLink="/admin/print-jobs" routerLinkActive="active">
              <mat-icon>print</mat-icon>
              <span>Print Jobs</span>
            </a>
            
            <a mat-list-item routerLink="/admin/expenses" routerLinkActive="active">
              <mat-icon>receipt</mat-icon>
              <span>Expenses</span>
            </a>
            
            <a mat-list-item routerLink="/admin/sellers" routerLinkActive="active">
              <mat-icon>store</mat-icon>
              <span>Sellers</span>
            </a>
            
            <a mat-list-item routerLink="/admin/reports" routerLinkActive="active">
              <mat-icon>assessment</mat-icon>
              <span>Reports</span>
            </a>
            
            <mat-divider></mat-divider>
            
            <a mat-list-item routerLink="/dashboard">
              <mat-icon>arrow_back</mat-icon>
              <span>Back to Store</span>
            </a>
          </mat-nav-list>
        </mat-sidenav>

        <mat-sidenav-content>
          <div class="content">
            <router-outlet></router-outlet>
          </div>
        </mat-sidenav-content>
      </mat-sidenav-container>
    </div>
  `,
  styles: [`
    .admin-layout {
      height: 100vh;
    }

    .sidenav-container {
      height: 100%;
    }

    .sidenav {
      width: 260px;
      background: #1e293b;
      color: white;
      
      .sidenav-header {
        padding: 1.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        
        h2 {
          margin: 0;
          font-size: 1.25rem;
        }
      }
      
      mat-nav-list {
        padding-top: 1rem;
        
        a {
          color: rgba(255,255,255,0.7);
          margin: 0.25rem 0.5rem;
          border-radius: 8px;
          
          &:hover {
            background: rgba(255,255,255,0.1);
            color: white;
          }
          
          &.active {
            background: #3f51b5;
            color: white;
          }
          
          mat-icon {
            margin-right: 1rem;
            color: inherit;
          }
        }
      }
    }

    .content {
      padding: 2rem;
      min-height: 100%;
      background: #f5f5f5;
    }
  `]
})
export class AdminComponent {}

