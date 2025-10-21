import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../../../shared/material.module';

@Component({
  selector: 'app-admin-print-jobs',
  standalone: true,
  imports: [CommonModule, MaterialModule],
  template: `
    <div class="admin-print-jobs">
      <h1>Print Job Monitoring</h1>
      <p>Print job monitoring interface will be implemented here</p>
    </div>
  `,
  styles: [`
    .admin-print-jobs {
      h1 {
        margin: 0 0 1rem;
      }
    }
  `]
})
export class AdminPrintJobsComponent {}

