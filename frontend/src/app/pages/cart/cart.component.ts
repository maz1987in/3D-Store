import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { MaterialModule } from '../../shared/material.module';
import { LoadingComponent } from '../../shared/components/loading/loading.component';
import { ErrorComponent } from '../../shared/components/error/error.component';
import { ConfirmationDialogComponent } from '../../shared/components/confirmation-dialog/confirmation-dialog.component';
import { MatDialog } from '@angular/material/dialog';
import { CartService } from '../../services/cart.service';
import { Cart, CartItem } from '../../models/cart.model';

@Component({
  selector: 'app-cart',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
    MaterialModule,
    LoadingComponent,
    ErrorComponent
  ],
  template: `
    <div class="cart-container">
      <h1>Shopping Cart</h1>

      @if (loading) {
        <app-loading type="skeleton"></app-loading>
      } @else if (error) {
        <app-error [message]="error" (retry)="loadCart()"></app-error>
      } @else if (!cart || cart.items.length === 0) {
        <!-- Empty Cart -->
        <div class="empty-cart">
          <mat-icon>shopping_cart</mat-icon>
          <h2>Your cart is empty</h2>
          <p>Add some products to get started</p>
          <button mat-raised-button color="primary" routerLink="/products">
            <mat-icon>shopping_bag</mat-icon>
            Browse Products
          </button>
        </div>
      } @else {
        <div class="cart-content">
          <!-- Cart Items -->
          <div class="cart-items">
            @for (item of cart.items; track item.id) {
              <mat-card class="cart-item">
                <div class="item-image">
                  @if (item.product?.image_url) {
                    <img [src]="item.product.image_url" [alt]="item.product?.name">
                  } @else {
                    <div class="placeholder-image">
                      <mat-icon>inventory_2</mat-icon>
                    </div>
                  }
                </div>

                <div class="item-details">
                  <h3 class="item-name">{{ item.product?.name }}</h3>
                  
                  @if (item.product?.category) {
                    <p class="item-category">{{ item.product.category.name }}</p>
                  }
                  
                  @if (item.item_type === 'print_job') {
                    <mat-chip-set>
                      <mat-chip color="primary">Custom Print</mat-chip>
                    </mat-chip-set>
                  }
                  
                  <p class="item-price">
                    {{ item.unit_price }} {{ cart.currency }} each
                  </p>
                </div>

                <div class="item-quantity">
                  <label>Quantity</label>
                  <div class="quantity-control">
                    <button 
                      mat-icon-button 
                      (click)="updateQuantity(item, item.quantity - 1)"
                      [disabled]="item.quantity <= 1 || updatingItem === item.id">
                      <mat-icon>remove</mat-icon>
                    </button>
                    <input 
                      type="number" 
                      [value]="item.quantity" 
                      min="1" 
                      max="100"
                      (change)="onQuantityInput(item, $event)"
                      [disabled]="updatingItem === item.id">
                    <button 
                      mat-icon-button 
                      (click)="updateQuantity(item, item.quantity + 1)"
                      [disabled]="item.quantity >= 100 || updatingItem === item.id">
                      <mat-icon>add</mat-icon>
                    </button>
                  </div>
                </div>

                <div class="item-total">
                  <label>Total</label>
                  <p class="total-price">
                    {{ item.total_price }} {{ cart.currency }}
                  </p>
                </div>

                <div class="item-actions">
                  <button 
                    mat-icon-button 
                    color="warn"
                    (click)="removeItem(item)"
                    [disabled]="updatingItem === item.id"
                    matTooltip="Remove from cart">
                    <mat-icon>delete</mat-icon>
                  </button>
                </div>
              </mat-card>
            }
          </div>

          <!-- Cart Summary -->
          <div class="cart-summary">
            <mat-card>
              <mat-card-header>
                <mat-card-title>Order Summary</mat-card-title>
              </mat-card-header>
              
              <mat-card-content>
                <div class="summary-row">
                  <span>Subtotal</span>
                  <span>{{ cart.subtotal }} {{ cart.currency }}</span>
                </div>
                
                @if (cart.packaging_cost > 0) {
                  <div class="summary-row">
                    <span>Packaging</span>
                    <span>{{ cart.packaging_cost }} {{ cart.currency }}</span>
                  </div>
                }
                
                @if (cart.shipping_cost > 0) {
                  <div class="summary-row">
                    <span>Shipping</span>
                    <span>{{ cart.shipping_cost }} {{ cart.currency }}</span>
                  </div>
                }
                
                @if (cart.tax > 0) {
                  <div class="summary-row">
                    <span>Tax</span>
                    <span>{{ cart.tax }} {{ cart.currency }}</span>
                  </div>
                }
                
                <mat-divider></mat-divider>
                
                <div class="summary-row total">
                  <span>Total</span>
                  <span class="total-amount">{{ cart.total }} {{ cart.currency }}</span>
                </div>
              </mat-card-content>
              
              <mat-card-actions>
                <button 
                  mat-raised-button 
                  color="primary" 
                  class="checkout-btn"
                  (click)="proceedToCheckout()">
                  <mat-icon>payment</mat-icon>
                  Proceed to Checkout
                </button>
                
                <button 
                  mat-button 
                  routerLink="/products"
                  class="continue-shopping-btn">
                  <mat-icon>arrow_back</mat-icon>
                  Continue Shopping
                </button>
              </mat-card-actions>
            </mat-card>

            <!-- Promotional Info -->
            <mat-card class="promo-card">
              <mat-card-content>
                <div class="promo-item">
                  <mat-icon color="accent">local_shipping</mat-icon>
                  <div>
                    <strong>Free Shipping</strong>
                    <p>On orders over $50</p>
                  </div>
                </div>
                
                <mat-divider></mat-divider>
                
                <div class="promo-item">
                  <mat-icon color="accent">verified</mat-icon>
                  <div>
                    <strong>Quality Guarantee</strong>
                    <p>30-day return policy</p>
                  </div>
                </div>
                
                <mat-divider></mat-divider>
                
                <div class="promo-item">
                  <mat-icon color="accent">support_agent</mat-icon>
                  <div>
                    <strong>Customer Support</strong>
                    <p>24/7 available</p>
                  </div>
                </div>
              </mat-card-content>
            </mat-card>
          </div>
        </div>
      }
    </div>
  `,
  styles: [`
    .cart-container {
      max-width: 1200px;
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
        font-size: 100px;
        width: 100px;
        height: 100px;
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

    .cart-content {
      display: grid;
      grid-template-columns: 1fr 400px;
      gap: 2rem;
      
      @media (max-width: 968px) {
        grid-template-columns: 1fr;
      }
    }

    .cart-items {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .cart-item {
      display: grid;
      grid-template-columns: 120px 1fr auto auto auto;
      gap: 1.5rem;
      align-items: center;
      padding: 1.5rem;
      
      @media (max-width: 768px) {
        grid-template-columns: 80px 1fr;
        
        .item-quantity,
        .item-total,
        .item-actions {
          grid-column: 1 / -1;
        }
      }
      
      .item-image {
        img {
          width: 120px;
          height: 120px;
          object-fit: cover;
          border-radius: 8px;
        }
        
        .placeholder-image {
          width: 120px;
          height: 120px;
          background: #f5f5f5;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          
          mat-icon {
            font-size: 48px;
            width: 48px;
            height: 48px;
            color: #999;
          }
        }
      }
      
      .item-details {
        .item-name {
          margin: 0 0 0.5rem;
          font-size: 1.125rem;
        }
        
        .item-category {
          color: #666;
          font-size: 0.875rem;
          margin: 0 0 0.5rem;
        }
        
        .item-price {
          color: #3f51b5;
          font-weight: 600;
          margin: 0.5rem 0 0;
        }
      }
      
      .item-quantity {
        label {
          display: block;
          font-size: 0.875rem;
          color: #666;
          margin-bottom: 0.5rem;
        }
        
        .quantity-control {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          
          input {
            width: 60px;
            text-align: center;
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 4px;
          }
        }
      }
      
      .item-total {
        label {
          display: block;
          font-size: 0.875rem;
          color: #666;
          margin-bottom: 0.5rem;
        }
        
        .total-price {
          font-size: 1.25rem;
          font-weight: 600;
          color: #3f51b5;
          margin: 0;
        }
      }
    }

    .cart-summary {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      height: fit-content;
      position: sticky;
      top: 2rem;
      
      mat-card {
        .summary-row {
          display: flex;
          justify-content: space-between;
          padding: 0.75rem 0;
          
          &.total {
            font-size: 1.25rem;
            font-weight: 600;
            margin-top: 0.5rem;
            
            .total-amount {
              color: #3f51b5;
            }
          }
        }
        
        mat-divider {
          margin: 1rem 0;
        }
      }
      
      .checkout-btn,
      .continue-shopping-btn {
        width: 100%;
        
        mat-icon {
          margin-right: 0.5rem;
        }
      }
      
      .checkout-btn {
        height: 48px;
      }
    }

    .promo-card {
      .promo-item {
        display: flex;
        gap: 1rem;
        padding: 0.75rem 0;
        
        mat-icon {
          flex-shrink: 0;
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
      
      mat-divider {
        margin: 0.75rem 0;
      }
    }
  `]
})
export class CartComponent implements OnInit, OnDestroy {
  cart: Cart | null = null;
  loading = false;
  error: string | null = null;
  updatingItem: string | null = null;
  
  private destroy$ = new Subject<void>();

  constructor(
    private cartService: CartService,
    private router: Router,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.loadCart();
    
    // Subscribe to cart updates
    this.cartService.cart$
      .pipe(takeUntil(this.destroy$))
      .subscribe(cart => {
        if (cart) {
          this.cart = cart;
        }
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadCart(): void {
    this.loading = true;
    this.error = null;

    this.cartService.getCart().subscribe({
      next: (cart) => {
        this.cart = cart;
        this.loading = false;
      },
      error: (error) => {
        this.error = error.message;
        this.loading = false;
      }
    });
  }

  updateQuantity(item: CartItem, newQuantity: number): void {
    if (newQuantity < 1 || newQuantity > 100) {
      return;
    }

    this.updatingItem = item.id;

    this.cartService.updateCartItem(item.id, { quantity: newQuantity }).subscribe({
      next: () => {
        this.updatingItem = null;
      },
      error: (error) => {
        this.updatingItem = null;
        console.error('Failed to update quantity:', error);
      }
    });
  }

  onQuantityInput(item: CartItem, event: Event): void {
    const input = event.target as HTMLInputElement;
    const newQuantity = parseInt(input.value, 10);
    
    if (!isNaN(newQuantity) && newQuantity > 0 && newQuantity <= 100) {
      this.updateQuantity(item, newQuantity);
    }
  }

  removeItem(item: CartItem): void {
    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        title: 'Remove Item',
        message: 'Are you sure you want to remove this item from your cart?',
        confirmText: 'Remove',
        cancelText: 'Cancel',
        confirmColor: 'warn'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.updatingItem = item.id;
        
        this.cartService.removeFromCart(item.id).subscribe({
          next: () => {
            this.updatingItem = null;
          },
          error: (error) => {
            this.updatingItem = null;
            console.error('Failed to remove item:', error);
          }
        });
      }
    });
  }

  proceedToCheckout(): void {
    this.router.navigate(['/checkout']);
  }

  clearCart(): void {
    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        title: 'Clear Cart',
        message: 'Are you sure you want to remove all items from your cart?',
        confirmText: 'Clear',
        cancelText: 'Cancel',
        confirmColor: 'warn'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.cartService.clearCart().subscribe({
          next: () => {
            this.cart = null;
          },
          error: (error) => {
            console.error('Failed to clear cart:', error);
          }
        });
      }
    });
  }
}

