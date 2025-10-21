import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from '../../shared/material.module';
import { LoadingComponent } from '../../shared/components/loading/loading.component';
import { CartService } from '../../services/cart.service';
import { OrderService } from '../../services/order.service';
import { Cart } from '../../models/cart.model';
import { PaymentMethod } from '../../models/order.model';

@Component({
  selector: 'app-checkout',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    ReactiveFormsModule,
    MaterialModule,
    LoadingComponent
  ],
  template: `
    <div class="checkout-container">
      <h1>Checkout</h1>

      @if (loading) {
        <app-loading type="skeleton"></app-loading>
      } @else if (!cart || cart.items.length === 0) {
        <div class="empty-cart">
          <mat-icon>shopping_cart</mat-icon>
          <h2>Your cart is empty</h2>
          <button mat-raised-button color="primary" routerLink="/products">
            Browse Products
          </button>
        </div>
      } @else {
        <mat-stepper #stepper linear>
          <!-- Step 1: Shipping Address -->
          <mat-step [stepControl]="shippingForm">
            <form [formGroup]="shippingForm">
              <ng-template matStepLabel>Shipping Address</ng-template>
              
              <div class="step-content">
                <h2>Shipping Information</h2>
                
                <div class="form-row">
                  <mat-form-field appearance="outline">
                    <mat-label>Street Address</mat-label>
                    <input matInput formControlName="street">
                    <mat-error>Street address is required</mat-error>
                  </mat-form-field>
                </div>

                <div class="form-row two-columns">
                  <mat-form-field appearance="outline">
                    <mat-label>City</mat-label>
                    <input matInput formControlName="city">
                    <mat-error>City is required</mat-error>
                  </mat-form-field>

                  <mat-form-field appearance="outline">
                    <mat-label>State/Province</mat-label>
                    <input matInput formControlName="state">
                  </mat-form-field>
                </div>

                <div class="form-row two-columns">
                  <mat-form-field appearance="outline">
                    <mat-label>Postal Code</mat-label>
                    <input matInput formControlName="postal_code">
                    <mat-error>Postal code is required</mat-error>
                  </mat-form-field>

                  <mat-form-field appearance="outline">
                    <mat-label>Country</mat-label>
                    <mat-select formControlName="country">
                      <mat-option value="OM">Oman</mat-option>
                      <mat-option value="UAE">United Arab Emirates</mat-option>
                      <mat-option value="SA">Saudi Arabia</mat-option>
                    </mat-select>
                    <mat-error>Country is required</mat-error>
                  </mat-form-field>
                </div>

                <div class="step-actions">
                  <button mat-raised-button color="primary" matStepperNext>
                    Continue
                  </button>
                </div>
              </div>
            </form>
          </mat-step>

          <!-- Step 2: Payment Method -->
          <mat-step [stepControl]="paymentForm">
            <form [formGroup]="paymentForm">
              <ng-template matStepLabel>Payment Method</ng-template>
              
              <div class="step-content">
                <h2>Payment Information</h2>
                
                <mat-radio-group formControlName="payment_method" class="payment-methods">
                  <mat-radio-button value="thawani" class="payment-option">
                    <div class="payment-method-content">
                      <mat-icon>credit_card</mat-icon>
                      <div>
                        <strong>Thawani Pay</strong>
                        <p>Pay securely with Thawani</p>
                      </div>
                    </div>
                  </mat-radio-button>

                  <mat-radio-button value="ompay" class="payment-option">
                    <div class="payment-method-content">
                      <mat-icon>payment</mat-icon>
                      <div>
                        <strong>OMPay</strong>
                        <p>Pay with OMPay wallet</p>
                      </div>
                    </div>
                  </mat-radio-button>

                  <mat-radio-button value="cash" class="payment-option">
                    <div class="payment-method-content">
                      <mat-icon>money</mat-icon>
                      <div>
                        <strong>Cash on Delivery</strong>
                        <p>Pay when you receive your order</p>
                      </div>
                    </div>
                  </mat-radio-button>

                  <mat-radio-button value="bank_transfer" class="payment-option">
                    <div class="payment-method-content">
                      <mat-icon>account_balance</mat-icon>
                      <div>
                        <strong>Bank Transfer</strong>
                        <p>Direct bank transfer</p>
                      </div>
                    </div>
                  </mat-radio-button>
                </mat-radio-group>

                <div class="step-actions">
                  <button mat-button matStepperPrevious>Back</button>
                  <button mat-raised-button color="primary" matStepperNext>
                    Continue
                  </button>
                </div>
              </div>
            </form>
          </mat-step>

          <!-- Step 3: Review Order -->
          <mat-step>
            <ng-template matStepLabel>Review & Place Order</ng-template>
            
            <div class="step-content">
              <h2>Review Your Order</h2>
              
              <!-- Order Summary -->
              <mat-card class="review-section">
                <mat-card-header>
                  <mat-card-title>Order Items</mat-card-title>
                </mat-card-header>
                <mat-card-content>
                  @for (item of cart.items; track item.id) {
                    <div class="review-item">
                      <div class="item-info">
                        <strong>{{ item.product?.name }}</strong>
                        <span class="item-quantity">Qty: {{ item.quantity }}</span>
                      </div>
                      <span class="item-price">{{ item.total_price }} {{ cart.currency }}</span>
                    </div>
                  }
                </mat-card-content>
              </mat-card>

              <!-- Shipping Address -->
              <mat-card class="review-section">
                <mat-card-header>
                  <mat-card-title>Shipping Address</mat-card-title>
                </mat-card-header>
                <mat-card-content>
                  <p>{{ shippingForm.value.street }}</p>
                  <p>{{ shippingForm.value.city }}, {{ shippingForm.value.state }} {{ shippingForm.value.postal_code }}</p>
                  <p>{{ shippingForm.value.country }}</p>
                </mat-card-content>
              </mat-card>

              <!-- Payment Method -->
              <mat-card class="review-section">
                <mat-card-header>
                  <mat-card-title>Payment Method</mat-card-title>
                </mat-card-header>
                <mat-card-content>
                  <p>{{ getPaymentMethodLabel(paymentForm.value.payment_method) }}</p>
                </mat-card-content>
              </mat-card>

              <!-- Order Total -->
              <mat-card class="review-section total-section">
                <mat-card-content>
                  <div class="total-row">
                    <span>Subtotal:</span>
                    <span>{{ cart.subtotal }} {{ cart.currency }}</span>
                  </div>
                  @if (cart.packaging_cost > 0) {
                    <div class="total-row">
                      <span>Packaging:</span>
                      <span>{{ cart.packaging_cost }} {{ cart.currency }}</span>
                    </div>
                  }
                  @if (cart.shipping_cost > 0) {
                    <div class="total-row">
                      <span>Shipping:</span>
                      <span>{{ cart.shipping_cost }} {{ cart.currency }}</span>
                    </div>
                  }
                  @if (cart.tax > 0) {
                    <div class="total-row">
                      <span>Tax:</span>
                      <span>{{ cart.tax }} {{ cart.currency }}</span>
                    </div>
                  }
                  <mat-divider></mat-divider>
                  <div class="total-row grand-total">
                    <span>Total:</span>
                    <span>{{ cart.total }} {{ cart.currency }}</span>
                  </div>
                </mat-card-content>
              </mat-card>

              <!-- Error Message -->
              @if (orderError) {
                <mat-card class="error-card">
                  <mat-card-content>
                    <mat-icon color="warn">error</mat-icon>
                    <span>{{ orderError }}</span>
                  </mat-card-content>
                </mat-card>
              }

              <!-- Actions -->
              <div class="step-actions">
                <button mat-button matStepperPrevious>Back</button>
                <button 
                  mat-raised-button 
                  color="primary"
                  (click)="placeOrder()"
                  [disabled]="placingOrder"
                  class="place-order-btn">
                  @if (placingOrder) {
                    <mat-spinner diameter="20"></mat-spinner>
                    Processing...
                  } @else {
                    <mat-icon>check_circle</mat-icon>
                    Place Order
                  }
                </button>
              </div>
            </div>
          </mat-step>
        </mat-stepper>
      }
    </div>
  `,
  styles: [`
    .checkout-container {
      max-width: 900px;
      margin: 0 auto;
      padding: 2rem 1rem;
      
      h1 {
        margin-bottom: 2rem;
      }
    }

    .empty-cart {
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
        margin: 0 0 2rem;
        color: #666;
      }
    }

    .step-content {
      padding: 2rem 0;
      
      h2 {
        margin: 0 0 1.5rem;
        font-size: 1.5rem;
      }
      
      .form-row {
        margin-bottom: 1rem;
        
        &.two-columns {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
        }
        
        mat-form-field {
          width: 100%;
        }
      }
    }

    .payment-methods {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      
      .payment-option {
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 8px;
        
        &.mat-radio-checked {
          border-color: #3f51b5;
          background: #f5f7ff;
        }
      }
      
      .payment-method-content {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-left: 0.5rem;
        
        mat-icon {
          font-size: 32px;
          width: 32px;
          height: 32px;
        }
        
        div {
          strong {
            display: block;
            margin-bottom: 0.25rem;
          }
          
          p {
            margin: 0;
            font-size: 0.875rem;
            color: #666;
          }
        }
      }
    }

    .review-section {
      margin-bottom: 1.5rem;
      
      .review-item {
        display: flex;
        justify-content: space-between;
        padding: 0.75rem 0;
        border-bottom: 1px solid #f0f0f0;
        
        &:last-child {
          border-bottom: none;
        }
        
        .item-info {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
          
          .item-quantity {
            font-size: 0.875rem;
            color: #666;
          }
        }
        
        .item-price {
          font-weight: 600;
          color: #3f51b5;
        }
      }
    }

    .total-section {
      .total-row {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        
        &.grand-total {
          font-size: 1.25rem;
          font-weight: 600;
          margin-top: 0.5rem;
          
          span:last-child {
            color: #3f51b5;
          }
        }
      }
      
      mat-divider {
        margin: 1rem 0;
      }
    }

    .error-card {
      margin-bottom: 1.5rem;
      background: #ffebee;
      
      mat-card-content {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #c62828;
      }
    }

    .step-actions {
      display: flex;
      justify-content: space-between;
      margin-top: 2rem;
      
      .place-order-btn {
        min-width: 180px;
        
        mat-icon,
        mat-spinner {
          margin-right: 0.5rem;
        }
      }
    }

    ::ng-deep .mat-stepper-horizontal {
      background: transparent;
    }
  `]
})
export class CheckoutComponent implements OnInit {
  cart: Cart | null = null;
  shippingForm: FormGroup;
  paymentForm: FormGroup;
  
  loading = false;
  placingOrder = false;
  orderError: string | null = null;

  constructor(
    private fb: FormBuilder,
    private cartService: CartService,
    private orderService: OrderService,
    private router: Router
  ) {
    this.shippingForm = this.fb.group({
      street: ['', Validators.required],
      city: ['', Validators.required],
      state: [''],
      postal_code: ['', Validators.required],
      country: ['OM', Validators.required]
    });

    this.paymentForm = this.fb.group({
      payment_method: ['thawani', Validators.required]
    });
  }

  ngOnInit(): void {
    this.loadCart();
  }

  loadCart(): void {
    this.loading = true;

    this.cartService.cart$.subscribe({
      next: (cart) => {
        this.cart = cart;
        this.loading = false;
        
        if (!cart || cart.items.length === 0) {
          this.router.navigate(['/cart']);
        }
      },
      error: (error) => {
        this.loading = false;
        console.error('Failed to load cart:', error);
      }
    });
  }

  placeOrder(): void {
    if (!this.cart || this.shippingForm.invalid || this.paymentForm.invalid) {
      return;
    }

    this.placingOrder = true;
    this.orderError = null;

    const orderData = {
      items: this.cart.items.map(item => ({
        type: item.item_type as 'print_job' | 'product',
        print_job_id: item.print_job_id,
        product_id: item.product_id,
        quantity: item.quantity,
        packaging_id: item.packaging_id
      })),
      shipping_address: this.shippingForm.value,
      payment_method: this.paymentForm.value.payment_method as PaymentMethod
    };

    this.orderService.createOrder(orderData).subscribe({
      next: (order) => {
        this.placingOrder = false;
        
        // Clear cart
        this.cartService.clearCart().subscribe();
        
        // Navigate to order confirmation
        this.router.navigate(['/orders', order.id], {
          queryParams: { success: true }
        });
      },
      error: (error) => {
        this.placingOrder = false;
        this.orderError = error.message || 'Failed to place order. Please try again.';
      }
    });
  }

  getPaymentMethodLabel(method: string): string {
    const labels: { [key: string]: string } = {
      'thawani': 'Thawani Pay',
      'ompay': 'OMPay',
      'cash': 'Cash on Delivery',
      'bank_transfer': 'Bank Transfer',
      'card': 'Credit/Debit Card'
    };
    return labels[method] || method;
  }
}

