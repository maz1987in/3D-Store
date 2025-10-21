import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../../../shared/material.module';

@Component({
  selector: 'app-admin-users',
  standalone: true,
  imports: [CommonModule, MaterialModule],
  template: `
    <div class="admin-users">
      <h1>User Management</h1>
      <p>User management interface will be implemented here</p>
    </div>
  `,
  styles: [`
    .admin-users {
      h1 {
        margin: 0 0 1rem;
      }
    }
  `]
})
export class AdminUsersComponent {}

