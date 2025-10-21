import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../../../shared/material.module';

@Component({
  selector: 'app-admin-sellers',
  standalone: true,
  imports: [CommonModule, MaterialModule],
  template: `
    <div class="admin-sellers">
      <h1>Seller Management</h1>
      <p>Seller management interface will be implemented here</p>
    </div>
  `,
  styles: [`
    .admin-sellers {
      h1 {
        margin: 0 0 1rem;
      }
    }
  `]
})
export class AdminSellersComponent {}

