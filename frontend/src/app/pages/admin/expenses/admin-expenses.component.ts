import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../../../shared/material.module';

@Component({
  selector: 'app-admin-expenses',
  standalone: true,
  imports: [CommonModule, MaterialModule],
  template: `
    <div class="admin-expenses">
      <h1>Expense Management</h1>
      <p>Expense management interface will be implemented here</p>
    </div>
  `,
  styles: [`
    .admin-expenses {
      h1 {
        margin: 0 0 1rem;
      }
    }
  `]
})
export class AdminExpensesComponent {}

