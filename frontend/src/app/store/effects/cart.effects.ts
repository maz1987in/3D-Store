import { Injectable, inject } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { of } from 'rxjs';
import { map, catchError, exhaustMap, tap } from 'rxjs/operators';
import { CartService } from '../../services/cart.service';
import * as CartActions from '../actions/cart.actions';

@Injectable()
export class CartEffects {
  
  private actions$ = inject(Actions);
  private cartService = inject(CartService);
  loadCart$ = createEffect(() =>
    this.actions$.pipe(
      ofType(CartActions.loadCart),
      exhaustMap(() =>
        this.cartService.getCart().pipe(
          map(cart => CartActions.loadCartSuccess({ cart })),
          catchError(error => of(CartActions.loadCartFailure({ error: error.message })))
        )
      )
    )
  );

  addToCart$ = createEffect(() =>
    this.actions$.pipe(
      ofType(CartActions.addToCart),
      exhaustMap(({ request }) =>
        this.cartService.addToCart(request).pipe(
          map(cart => CartActions.addToCartSuccess({ cart })),
          catchError(error => of(CartActions.addToCartFailure({ error: error.message })))
        )
      )
    )
  );

  updateCartItem$ = createEffect(() =>
    this.actions$.pipe(
      ofType(CartActions.updateCartItem),
      exhaustMap(({ itemId, request }) =>
        this.cartService.updateCartItem(itemId, request).pipe(
          map(cart => CartActions.updateCartItemSuccess({ cart })),
          catchError(error => of(CartActions.updateCartItemFailure({ error: error.message })))
        )
      )
    )
  );

  removeFromCart$ = createEffect(() =>
    this.actions$.pipe(
      ofType(CartActions.removeFromCart),
      exhaustMap(({ itemId }) =>
        this.cartService.removeFromCart(itemId).pipe(
          map(cart => CartActions.removeFromCartSuccess({ cart })),
          catchError(error => of(CartActions.removeFromCartFailure({ error: error.message })))
        )
      )
    )
  );

  clearCart$ = createEffect(() =>
    this.actions$.pipe(
      ofType(CartActions.clearCart),
      exhaustMap(() =>
        this.cartService.clearCart().pipe(
          map(() => CartActions.clearCartSuccess()),
          catchError(error => of(CartActions.clearCartFailure({ error: error.message })))
        )
      )
    )
  );

  // Sync cart to localStorage on success
  syncCartToStorage$ = createEffect(
    () =>
      this.actions$.pipe(
        ofType(
          CartActions.loadCartSuccess,
          CartActions.addToCartSuccess,
          CartActions.updateCartItemSuccess,
          CartActions.removeFromCartSuccess
        ),
        tap(({ cart }) => {
          if (cart) {
            localStorage.setItem('shopping_cart', JSON.stringify(cart));
          }
        })
      ),
    { dispatch: false }
  );

  clearCartStorage$ = createEffect(
    () =>
      this.actions$.pipe(
        ofType(CartActions.clearCartSuccess),
        tap(() => {
          localStorage.removeItem('shopping_cart');
        })
      ),
    { dispatch: false }
  );
}

