import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../../../shared/material.module';

@Component({
  selector: 'app-seller-payments',
  standalone: true,
  imports: [CommonModule, MaterialModule],
  template: `
    <div class="seller-payments">
      <h1>Payment History</h1>
      <p>Payment history interface will be implemented here</p>
    </div>
  `,
  styles: [`
    .seller-payments {
      h1 {
        margin: 0 0 1rem;
      }
    }
  `]
})
export class SellerPaymentsComponent {}

