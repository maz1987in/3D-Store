import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { ApiService } from '../core/services/api.service';
import {
  Cart,
  CartItem,
  AddToCartRequest,
  UpdateCartItemRequest,
  CartSummary
} from '../models/cart.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class CartService {
  private cartKey = environment.cartKey;
  private cartSubject = new BehaviorSubject<Cart | null>(null);
  public cart$ = this.cartSubject.asObservable();

  private cartSummarySubject = new BehaviorSubject<CartSummary>({
    items_count: 0,
    subtotal: 0,
    total: 0,
    currency: 'USD'
  });
  public cartSummary$ = this.cartSummarySubject.asObservable();

  constructor(private api: ApiService) {
    this.loadCartFromStorage();
  }

  /**
   * Get current cart
   */
  getCart(): Observable<Cart> {
    return this.api.get<Cart>('cart').pipe(
      tap(cart => {
        this.updateCart(cart);
      })
    );
  }

  /**
   * Add item to cart
   */
  addToCart(request: AddToCartRequest): Observable<Cart> {
    return this.api.post<Cart>('cart/items', request).pipe(
      tap(cart => {
        this.updateCart(cart);
      })
    );
  }

  /**
   * Update cart item
   */
  updateCartItem(itemId: string, request: UpdateCartItemRequest): Observable<Cart> {
    return this.api.put<Cart>(`cart/items/${itemId}`, request).pipe(
      tap(cart => {
        this.updateCart(cart);
      })
    );
  }

  /**
   * Remove item from cart
   */
  removeFromCart(itemId: string): Observable<Cart> {
    return this.api.delete<Cart>(`cart/items/${itemId}`).pipe(
      tap(cart => {
        this.updateCart(cart);
      })
    );
  }

  /**
   * Clear cart
   */
  clearCart(): Observable<void> {
    return this.api.delete<void>('cart').pipe(
      tap(() => {
        this.updateCart(null);
      })
    );
  }

  /**
   * Get cart summary
   */
  getCartSummary(): CartSummary {
    return this.cartSummarySubject.value;
  }

  /**
   * Update cart state
   */
  private updateCart(cart: Cart | null): void {
    this.cartSubject.next(cart);
    
    if (cart) {
      // Save to localStorage
      localStorage.setItem(this.cartKey, JSON.stringify(cart));
      
      // Update summary
      this.cartSummarySubject.next({
        items_count: cart.items.length,
        subtotal: cart.subtotal,
        total: cart.total,
        currency: cart.currency
      });
    } else {
      // Clear localStorage
      localStorage.removeItem(this.cartKey);
      
      // Reset summary
      this.cartSummarySubject.next({
        items_count: 0,
        subtotal: 0,
        total: 0,
        currency: 'USD'
      });
    }
  }

  /**
   * Load cart from localStorage
   */
  private loadCartFromStorage(): void {
    const cartJson = localStorage.getItem(this.cartKey);
    if (cartJson) {
      try {
        const cart = JSON.parse(cartJson);
        this.cartSubject.next(cart);
        this.cartSummarySubject.next({
          items_count: cart.items.length,
          subtotal: cart.subtotal,
          total: cart.total,
          currency: cart.currency
        });
      } catch (error) {
        console.error('Error parsing cart data:', error);
        localStorage.removeItem(this.cartKey);
      }
    }
  }

  /**
   * Get current cart value
   */
  getCurrentCart(): Cart | null {
    return this.cartSubject.value;
  }

  /**
   * Check if cart has items
   */
  hasItems(): boolean {
    const cart = this.getCurrentCart();
    return !!(cart && cart.items.length > 0);
  }

  /**
   * Get item count
   */
  getItemCount(): number {
    return this.cartSummarySubject.value.items_count;
  }
}

