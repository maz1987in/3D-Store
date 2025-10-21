import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { MaterialModule } from '../../shared/material.module';
import { LoadingComponent } from '../../shared/components/loading/loading.component';
import { ErrorComponent } from '../../shared/components/error/error.component';
import { PaginationComponent } from '../../shared/components/pagination/pagination.component';
import { PrintJobService } from '../../services/print-job.service';
import { WebSocketService } from '../../services/websocket.service';
import { PrintJob, PrintJobStatus } from '../../models/print-job.model';

@Component({
  selector: 'app-print-jobs',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MaterialModule,
    LoadingComponent,
    ErrorComponent,
    PaginationComponent
  ],
  template: `
    <div class="print-jobs-container">
      <div class="page-header">
        <h1>Print Jobs</h1>
        <button mat-raised-button color="primary" routerLink="/upload">
          <mat-icon>upload</mat-icon>
          Upload New Model
        </button>
      </div>

      <!-- Status Filter -->
      <div class="filters-section">
        <mat-chip-set aria-label="Status filter">
          <mat-chip 
            [highlighted]="!selectedStatus"
            (click)="filterByStatus(undefined)">
            All Jobs
          </mat-chip>
          <mat-chip 
            [highlighted]="selectedStatus === 'queued'"
            (click)="filterByStatus('queued')">
            Queued
          </mat-chip>
          <mat-chip 
            [highlighted]="selectedStatus === 'printing'"
            (click)="filterByStatus('printing')">
            Printing
          </mat-chip>
          <mat-chip 
            [highlighted]="selectedStatus === 'completed'"
            (click)="filterByStatus('completed')">
            Completed
          </mat-chip>
          <mat-chip 
            [highlighted]="selectedStatus === 'failed'"
            (click)="filterByStatus('failed')">
            Failed
          </mat-chip>
        </mat-chip-set>
      </div>

      @if (loading) {
        <app-loading type="skeleton"></app-loading>
      } @else if (error) {
        <app-error [message]="error" (retry)="loadPrintJobs()"></app-error>
      } @else if (printJobs.length === 0) {
        <div class="empty-state">
          <mat-icon>print</mat-icon>
          <h2>No print jobs found</h2>
          <p>Upload a 3D model to create your first print job</p>
          <button mat-raised-button color="primary" routerLink="/upload">
            <mat-icon>upload</mat-icon>
            Upload 3D Model
          </button>
        </div>
      } @else {
        <div class="print-jobs-list">
          @for (job of printJobs; track job.id) {
            <mat-card class="print-job-card">
              <mat-card-header>
                <mat-card-title>
                  <div class="job-header">
                    <div>
                      <h3>{{ job.material_name }}</h3>
                      <p class="job-meta">
                        {{ job.quality }} quality • Quantity: {{ job.quantity }}
                      </p>
                    </div>
                    <mat-chip [color]="getStatusColor(job.status)">
                      {{ job.status }}
                    </mat-chip>
                  </div>
                </mat-card-title>
              </mat-card-header>

              <mat-card-content>
                <div class="job-details">
                  <!-- Progress Bar (for active jobs) -->
                  @if (job.status === 'printing' || job.status === 'preparing') {
                    <div class="progress-section">
                      <div class="progress-header">
                        <span>Progress</span>
                        <span class="progress-value">{{ job.progress }}%</span>
                      </div>
                      <mat-progress-bar 
                        mode="determinate" 
                        [value]="job.progress"
                        [color]="'primary'">
                      </mat-progress-bar>
                    </div>
                  }

                  <!-- Job Information -->
                  <div class="info-grid">
                    @if (job.estimated_time_hours) {
                      <div class="info-item">
                        <mat-icon>schedule</mat-icon>
                        <div>
                          <p class="label">Estimated Time</p>
                          <p class="value">{{ job.estimated_time_hours }} hours</p>
                        </div>
                      </div>
                    }

                    @if (job.estimated_cost) {
                      <div class="info-item">
                        <mat-icon>attach_money</mat-icon>
                        <div>
                          <p class="label">Estimated Cost</p>
                          <p class="value">{{ job.estimated_cost }}</p>
                        </div>
                      </div>
                    }

                    @if (job.start_date) {
                      <div class="info-item">
                        <mat-icon>play_arrow</mat-icon>
                        <div>
                          <p class="label">Started</p>
                          <p class="value">{{ job.start_date | date:'short' }}</p>
                        </div>
                      </div>
                    }

                    @if (job.completion_date) {
                      <div class="info-item">
                        <mat-icon>check_circle</mat-icon>
                        <div>
                          <p class="label">Completed</p>
                          <p class="value">{{ job.completion_date | date:'short' }}</p>
                        </div>
                      </div>
                    }
                  </div>

                  <!-- Error Message -->
                  @if (job.status === 'failed' && job.error_message) {
                    <div class="error-message">
                      <mat-icon color="warn">error</mat-icon>
                      <span>{{ job.error_message }}</span>
                    </div>
                  }

                  <!-- Notes -->
                  @if (job.notes) {
                    <div class="job-notes">
                      <strong>Notes:</strong>
                      <p>{{ job.notes }}</p>
                    </div>
                  }
                </div>
              </mat-card-content>

              <mat-card-actions>
                @if (job.model_url) {
                  <button mat-button>
                    <mat-icon>visibility</mat-icon>
                    View Model
                  </button>
                }
                
                @if (job.status === 'queued' || job.status === 'preparing') {
                  <button mat-button color="warn" (click)="cancelJob(job)">
                    <mat-icon>cancel</mat-icon>
                    Cancel
                  </button>
                }
              </mat-card-actions>
            </mat-card>
          }
        </div>

        <app-pagination
          [totalItems]="totalJobs"
          [currentPage]="currentPage"
          [pageSize]="pageSize"
          (pageChange)="onPageChange($event)"
          (pageSizeChange)="onPageSizeChange($event)">
        </app-pagination>
      }
    </div>
  `,
  styles: [`
    .print-jobs-container {
      max-width: 1000px;
      margin: 0 auto;
      padding: 2rem 1rem;
    }

    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
      
      h1 {
        margin: 0;
      }
      
      button mat-icon {
        margin-right: 0.5rem;
      }
    }

    .filters-section {
      margin-bottom: 2rem;
    }

    .empty-state {
      text-align: center;
      padding: 4rem 2rem;
      
      mat-icon {
        font-size: 80px;
        width: 80px;
        height: 80px;
        color: #ccc;
        margin-bottom: 1rem;
      }
      
      h2 {
        margin: 0 0 0.5rem;
        color: #666;
      }
      
      p {
        color: #999;
        margin-bottom: 2rem;
      }
      
      button mat-icon {
        margin-right: 0.5rem;
      }
    }

    .print-jobs-list {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
      margin-bottom: 2rem;
    }

    .print-job-card {
      .job-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        width: 100%;
        
        h3 {
          margin: 0 0 0.5rem;
          font-size: 1.25rem;
        }
        
        .job-meta {
          margin: 0;
          color: #666;
          font-size: 0.875rem;
        }
      }
      
      .job-details {
        .progress-section {
          margin-bottom: 1.5rem;
          
          .progress-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
            
            .progress-value {
              font-weight: 600;
              color: #3f51b5;
            }
          }
        }
        
        .info-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
          margin-bottom: 1rem;
          
          .info-item {
            display: flex;
            gap: 0.75rem;
            
            mat-icon {
              color: #3f51b5;
              flex-shrink: 0;
            }
            
            .label {
              font-size: 0.75rem;
              color: #999;
              margin: 0 0 0.25rem;
            }
            
            .value {
              margin: 0;
              font-weight: 600;
            }
          }
        }
        
        .error-message {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem;
          background: #ffebee;
          border-radius: 4px;
          color: #c62828;
          margin-bottom: 1rem;
        }
        
        .job-notes {
          padding: 0.75rem;
          background: #f5f5f5;
          border-radius: 4px;
          
          strong {
            display: block;
            margin-bottom: 0.5rem;
          }
          
          p {
            margin: 0;
            color: #666;
          }
        }
      }
    }

    mat-card-actions {
      display: flex;
      gap: 0.5rem;
      
      button mat-icon {
        margin-right: 0.25rem;
        font-size: 18px;
        width: 18px;
        height: 18px;
      }
    }
  `]
})
export class PrintJobsComponent implements OnInit, OnDestroy {
  printJobs: PrintJob[] = [];
  loading = false;
  error: string | null = null;
  
  totalJobs = 0;
  currentPage = 1;
  pageSize = 10;
  selectedStatus: PrintJobStatus | undefined;
  
  private destroy$ = new Subject<void>();

  constructor(
    private printJobService: PrintJobService,
    private wsService: WebSocketService
  ) {}

  ngOnInit(): void {
    this.loadPrintJobs();
    this.subscribeToUpdates();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadPrintJobs(): void {
    this.loading = true;
    this.error = null;

    this.printJobService.getUserPrintJobs({
      page: this.currentPage,
      limit: this.pageSize,
      status: this.selectedStatus
    }).subscribe({
      next: (response) => {
        this.printJobs = response.data;
        this.totalJobs = response.meta.total;
        this.loading = false;
      },
      error: (error) => {
        this.error = error.message;
        this.loading = false;
      }
    });
  }

  filterByStatus(status: PrintJobStatus | undefined): void {
    this.selectedStatus = status;
    this.currentPage = 1;
    this.loadPrintJobs();
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadPrintJobs();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  onPageSizeChange(size: number): void {
    this.pageSize = size;
    this.currentPage = 1;
    this.loadPrintJobs();
  }

  cancelJob(job: PrintJob): void {
    this.printJobService.cancelPrintJob(job.id).subscribe({
      next: () => {
        this.loadPrintJobs();
      },
      error: (error) => {
        console.error('Failed to cancel job:', error);
      }
    });
  }

  subscribeToUpdates(): void {
    this.wsService.on('print_progress')
      .pipe(takeUntil(this.destroy$))
      .subscribe(data => {
        const job = this.printJobs.find(j => j.id === data.job_id);
        if (job) {
          job.progress = data.progress;
        }
      });

    this.wsService.on('print_completed')
      .pipe(takeUntil(this.destroy$))
      .subscribe(data => {
        const job = this.printJobs.find(j => j.id === data.job_id);
        if (job) {
          job.status = 'completed';
          job.progress = 100;
        }
      });
  }

  getStatusColor(status: PrintJobStatus): 'primary' | 'accent' | 'warn' | undefined {
    switch (status) {
      case 'completed':
        return 'accent';
      case 'failed':
      case 'cancelled':
        return 'warn';
      case 'printing':
      case 'preparing':
        return 'primary';
      default:
        return undefined;
    }
  }
}

