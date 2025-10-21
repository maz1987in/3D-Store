import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MaterialModule } from '../../shared/material.module';

@Component({
  selector: 'app-not-found',
  standalone: true,
  imports: [CommonModule, RouterModule, MaterialModule],
  template: `
    <div class="error-container">
      <div class="error-content">
        <h1 class="error-code">404</h1>
        <h2>Page Not Found</h2>
        <p>The page you're looking for doesn't exist or has been moved.</p>
        <div class="actions">
          <button mat-raised-button color="primary" routerLink="/">
            <mat-icon>home</mat-icon>
            Go Home
          </button>
          <button mat-raised-button routerLink="/products">
            <mat-icon>shopping_bag</mat-icon>
            Browse Products
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
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .error-content {
      text-align: center;
      color: white;
      
      .error-code {
        font-size: 8rem;
        font-weight: 700;
        margin: 0;
        line-height: 1;
      }
      
      h2 {
        font-size: 2rem;
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
export class NotFoundComponent {}

