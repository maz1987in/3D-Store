import { createAction, props } from '@ngrx/store';
import { Cart, CartItem, AddToCartRequest, UpdateCartItemRequest } from '../../models/cart.model';

// Load Cart Actions
export const loadCart = createAction('[Cart] Load Cart');

export const loadCartSuccess = createAction(
  '[Cart] Load Cart Success',
  props<{ cart: Cart }>()
);

export const loadCartFailure = createAction(
  '[Cart] Load Cart Failure',
  props<{ error: string }>()
);

// Add to Cart Actions
export const addToCart = createAction(
  '[Cart] Add to Cart',
  props<{ request: AddToCartRequest }>()
);

export const addToCartSuccess = createAction(
  '[Cart] Add to Cart Success',
  props<{ cart: Cart }>()
);

export const addToCartFailure = createAction(
  '[Cart] Add to Cart Failure',
  props<{ error: string }>()
);

// Update Cart Item Actions
export const updateCartItem = createAction(
  '[Cart] Update Cart Item',
  props<{ itemId: string; request: UpdateCartItemRequest }>()
);

export const updateCartItemSuccess = createAction(
  '[Cart] Update Cart Item Success',
  props<{ cart: Cart }>()
);

export const updateCartItemFailure = createAction(
  '[Cart] Update Cart Item Failure',
  props<{ error: string }>()
);

// Remove from Cart Actions
export const removeFromCart = createAction(
  '[Cart] Remove from Cart',
  props<{ itemId: string }>()
);

export const removeFromCartSuccess = createAction(
  '[Cart] Remove from Cart Success',
  props<{ cart: Cart }>()
);

export const removeFromCartFailure = createAction(
  '[Cart] Remove from Cart Failure',
  props<{ error: string }>()
);

// Clear Cart Actions
export const clearCart = createAction('[Cart] Clear Cart');

export const clearCartSuccess = createAction('[Cart] Clear Cart Success');

export const clearCartFailure = createAction(
  '[Cart] Clear Cart Failure',
  props<{ error: string }>()
);

// Local Actions (no API call)
export const setCart = createAction(
  '[Cart] Set Cart',
  props<{ cart: Cart | null }>()
);

