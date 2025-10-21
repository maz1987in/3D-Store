import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../../../shared/material.module';

@Component({
  selector: 'app-admin-reports',
  standalone: true,
  imports: [CommonModule, MaterialModule],
  template: `
    <div class="admin-reports">
      <h1>Financial Reports</h1>
      <p>Financial reporting interface will be implemented here</p>
    </div>
  `,
  styles: [`
    .admin-reports {
      h1 {
        margin: 0 0 1rem;
      }
    }
  `]
})
export class AdminReportsComponent {}

