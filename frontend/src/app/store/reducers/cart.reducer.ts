import { createReducer, on } from '@ngrx/store';
import { Cart } from '../../models/cart.model';
import * as CartActions from '../actions/cart.actions';

export interface CartState {
  cart: Cart | null;
  loading: boolean;
  error: string | null;
}

export const initialState: CartState = {
  cart: null,
  loading: false,
  error: null
};

export const cartReducer = createReducer(
  initialState,
  
  // Load Cart
  on(CartActions.loadCart, (state) => ({
    ...state,
    loading: true,
    error: null
  })),
  
  on(CartActions.loadCartSuccess, (state, { cart }) => ({
    ...state,
    cart,
    loading: false,
    error: null
  })),
  
  on(CartActions.loadCartFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Add to Cart
  on(CartActions.addToCart, (state) => ({
    ...state,
    loading: true,
    error: null
  })),
  
  on(CartActions.addToCartSuccess, (state, { cart }) => ({
    ...state,
    cart,
    loading: false,
    error: null
  })),
  
  on(CartActions.addToCartFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Update Cart Item
  on(CartActions.updateCartItem, (state) => ({
    ...state,
    loading: true,
    error: null
  })),
  
  on(CartActions.updateCartItemSuccess, (state, { cart }) => ({
    ...state,
    cart,
    loading: false,
    error: null
  })),
  
  on(CartActions.updateCartItemFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Remove from Cart
  on(CartActions.removeFromCart, (state) => ({
    ...state,
    loading: true,
    error: null
  })),
  
  on(CartActions.removeFromCartSuccess, (state, { cart }) => ({
    ...state,
    cart,
    loading: false,
    error: null
  })),
  
  on(CartActions.removeFromCartFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Clear Cart
  on(CartActions.clearCart, (state) => ({
    ...state,
    loading: true,
    error: null
  })),
  
  on(CartActions.clearCartSuccess, (state) => ({
    ...state,
    cart: null,
    loading: false,
    error: null
  })),
  
  on(CartActions.clearCartFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Set Cart (local action)
  on(CartActions.setCart, (state, { cart }) => ({
    ...state,
    cart
  }))
);

