import { createFeatureSelector, createSelector } from '@ngrx/store';
import { CartState } from '../reducers/cart.reducer';

export const selectCartState = createFeatureSelector<CartState>('cart');

export const selectCart = createSelector(
  selectCartState,
  (state) => state.cart
);

export const selectCartItems = createSelector(
  selectCart,
  (cart) => cart?.items || []
);

export const selectCartItemsCount = createSelector(
  selectCartItems,
  (items) => items.reduce((sum, item) => sum + item.quantity, 0)
);

export const selectCartSubtotal = createSelector(
  selectCart,
  (cart) => cart?.subtotal || 0
);

export const selectCartTotal = createSelector(
  selectCart,
  (cart) => cart?.total || 0
);

export const selectCartCurrency = createSelector(
  selectCart,
  (cart) => cart?.currency || 'OMR'
);

export const selectCartLoading = createSelector(
  selectCartState,
  (state) => state.loading
);

export const selectCartError = createSelector(
  selectCartState,
  (state) => state.error
);

export const selectCartSummary = createSelector(
  selectCartItemsCount,
  selectCartSubtotal,
  selectCartTotal,
  selectCartCurrency,
  (items_count, subtotal, total, currency) => ({
    items_count,
    subtotal,
    total,
    currency
  })
);

export const selectCartHasItems = createSelector(
  selectCartItemsCount,
  (count) => count > 0
);

export const selectCartItemById = (itemId: string) =>
  createSelector(selectCartItems, (items) =>
    items.find(item => item.id === itemId)
  );

