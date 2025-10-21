import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MaterialModule } from '../../shared/material.module';

@Component({
  selector: 'app-unauthorized',
  standalone: true,
  imports: [CommonModule, RouterModule, MaterialModule],
  template: `
    <div class="error-container">
      <div class="error-content">
        <mat-icon class="error-icon">lock</mat-icon>
        <h1>Access Denied</h1>
        <p>You don't have permission to access this page.</p>
        <div class="actions">
          <button mat-raised-button color="primary" routerLink="/">
            <mat-icon>home</mat-icon>
            Go Home
          </button>
          <button mat-raised-button routerLink="/dashboard">
            <mat-icon>dashboard</mat-icon>
            Go to Dashboard
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .error-container {
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 2rem;
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }

    .error-content {
      text-align: center;
      color: white;
      
      .error-icon {
        font-size: 120px;
        width: 120px;
        height: 120px;
        margin-bottom: 1rem;
      }
      
      h1 {
        font-size: 2.5rem;
        margin: 1rem 0;
      }
      
      p {
        font-size: 1.125rem;
        margin-bottom: 2rem;
        opacity: 0.9;
      }
      
      .actions {
        display: flex;
        gap: 1rem;
        justify-content: center;
        
        button mat-icon {
          margin-right: 0.5rem;
        }
      }
    }
  `]
})
export class UnauthorizedComponent {}

