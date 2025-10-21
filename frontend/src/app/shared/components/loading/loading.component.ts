import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../../material.module';

@Component({
  selector: 'app-loading',
  standalone: true,
  imports: [CommonModule, MaterialModule],
  template: `
    <div class="loading-container" [class.overlay]="overlay">
      <div class="loading-content">
        @if (type === 'spinner') {
          <mat-spinner [diameter]="diameter"></mat-spinner>
        } @else if (type === 'progress') {
          <mat-progress-bar mode="determinate" [value]="progress"></mat-progress-bar>
        } @else if (type === 'skeleton') {
          <div class="skeleton-loader">
            <div class="skeleton-line" *ngFor="let line of skeletonLines"></div>
          </div>
        }
        
        @if (message) {
          <p class="loading-message">{{ message }}</p>
        }
      </div>
    </div>
  `,
  styles: [`
    .loading-container {
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 2rem;
      
      &.overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.9);
        z-index: 9999;
      }
    }
    
    .loading-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1rem;
    }
    
    .loading-message {
      margin: 0;
      color: #666;
      font-size: 14px;
    }
    
    .skeleton-loader {
      width: 100%;
      max-width: 600px;
    }
    
    .skeleton-line {
      height: 20px;
      background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
      background-size: 200% 100%;
      animation: skeleton-loading 1.5s infinite;
      margin-bottom: 10px;
      border-radius: 4px;
      
      &:nth-child(odd) {
        width: 100%;
      }
      
      &:nth-child(even) {
        width: 80%;
      }
    }
    
    @keyframes skeleton-loading {
      0% {
        background-position: 200% 0;
      }
      100% {
        background-position: -200% 0;
      }
    }
  `]
})
export class LoadingComponent {
  @Input() type: 'spinner' | 'progress' | 'skeleton' = 'spinner';
  @Input() message?: string;
  @Input() progress: number = 0;
  @Input() overlay: boolean = false;
  @Input() diameter: number = 50;
  
  skeletonLines = Array(5).fill(0);
}

