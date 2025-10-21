import { ActionReducerMap, MetaReducer } from '@ngrx/store';
import { environment } from '../../../environments/environment';
import { authReducer, AuthState } from './auth.reducer';
import { cartReducer, CartState } from './cart.reducer';
import { productReducer, ProductState } from './product.reducer';
import { orderReducer, OrderState } from './order.reducer';

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

export const metaReducers: MetaReducer<AppState>[] = !environment.production ? [] : [];

