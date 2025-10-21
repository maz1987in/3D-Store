import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../../material.module';

@Component({
  selector: 'app-error',
  standalone: true,
  imports: [CommonModule, MaterialModule],
  template: `
    <div class="error-container">
      <mat-card class="error-card">
        <mat-card-content>
          <div class="error-icon">
            <mat-icon color="warn">error_outline</mat-icon>
          </div>
          
          <h3 class="error-message">{{ message }}</h3>
          
          @if (details) {
            <p class="error-details">{{ details }}</p>
          }
          
          @if (showRetry) {
            <div class="error-actions">
              <button mat-raised-button color="primary" (click)="onRetry()">
                <mat-icon>refresh</mat-icon>
                Retry
              </button>
            </div>
          }
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .error-container {
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 2rem;
      min-height: 200px;
    }
    
    .error-card {
      max-width: 600px;
      width: 100%;
    }
    
    .error-icon {
      text-align: center;
      margin-bottom: 1rem;
      
      mat-icon {
        font-size: 48px;
        width: 48px;
        height: 48px;
      }
    }
    
    .error-message {
      text-align: center;
      color: #d32f2f;
      margin: 0 0 0.5rem;
    }
    
    .error-details {
      text-align: center;
      color: #666;
      font-size: 14px;
      margin: 0 0 1rem;
    }
    
    .error-actions {
      display: flex;
      justify-content: center;
      margin-top: 1.5rem;
      
      button {
        min-width: 120px;
        
        mat-icon {
          margin-right: 0.5rem;
        }
      }
    }
  `]
})
export class ErrorComponent {
  @Input() message: string = 'An error occurred';
  @Input() details?: string;
  @Input() showRetry: boolean = true;
  @Output() retry = new EventEmitter<void>();
  
  onRetry(): void {
    this.retry.emit();
  }
}

