import { ActionReducerMap } from '@ngrx/store';
import { authReducer, AuthState } from './reducers/auth.reducer';
import { cartReducer, CartState } from './reducers/cart.reducer';
import { productReducer, ProductState } from './reducers/product.reducer';
import { orderReducer, OrderState } from './reducers/order.reducer';

export interface AppState {
  auth: AuthState;
  cart: CartState;
  product: ProductState;
  order: OrderState;
}

export const reducers: ActionReducerMap<AppState> = {
  auth: authReducer,
  cart: cartReducer,
  product: productReducer,
  order: orderReducer
};

