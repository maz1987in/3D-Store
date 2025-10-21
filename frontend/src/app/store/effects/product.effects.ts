import { Injectable, inject } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { of } from 'rxjs';
import { map, catchError, exhaustMap, switchMap } from 'rxjs/operators';
import { ProductService } from '../../services/product.service';
import * as ProductActions from '../actions/product.actions';

@Injectable()
export class ProductEffects {
  
  private actions$ = inject(Actions);
  private productService = inject(ProductService);
  
  loadProducts$ = createEffect(() =>
    this.actions$.pipe(
      ofType(ProductActions.loadProducts),
      switchMap(({ filters }) =>
        this.productService.getProducts(filters).pipe(
          map(response => ProductActions.loadProductsSuccess({ response })),
          catchError(error => of(ProductActions.loadProductsFailure({ error: error.message })))
        )
      )
    )
  );

  loadProduct$ = createEffect(() =>
    this.actions$.pipe(
      ofType(ProductActions.loadProduct),
      switchMap(({ id }) =>
        this.productService.getProduct(id).pipe(
          map(product => ProductActions.loadProductSuccess({ product })),
          catchError(error => of(ProductActions.loadProductFailure({ error: error.message })))
        )
      )
    )
  );

  searchProducts$ = createEffect(() =>
    this.actions$.pipe(
      ofType(ProductActions.searchProducts),
      switchMap(({ query }) =>
        this.productService.searchProducts(query).pipe(
          map(products => ProductActions.searchProductsSuccess({ products })),
          catchError(error => of(ProductActions.searchProductsFailure({ error: error.message })))
        )
      )
    )
  );

  loadCategories$ = createEffect(() =>
    this.actions$.pipe(
      ofType(ProductActions.loadCategories),
      exhaustMap(() =>
        this.productService.getCategories().pipe(
          map(categories => ProductActions.loadCategoriesSuccess({ categories })),
          catchError(error => of(ProductActions.loadCategoriesFailure({ error: error.message })))
        )
      )
    )
  );

  loadMaterials$ = createEffect(() =>
    this.actions$.pipe(
      ofType(ProductActions.loadMaterials),
      exhaustMap(() =>
        this.productService.getMaterials().pipe(
          map(materials => ProductActions.loadMaterialsSuccess({ materials })),
          catchError(error => of(ProductActions.loadMaterialsFailure({ error: error.message })))
        )
      )
    )
  );

  addToFavorites$ = createEffect(() =>
    this.actions$.pipe(
      ofType(ProductActions.addToFavorites),
      exhaustMap(({ productId }) =>
        this.productService.addToFavorites(productId).pipe(
          map(() => ProductActions.addToFavoritesSuccess({ productId })),
          catchError(() => of({ type: '[Product] Add to Favorites Failure' }))
        )
      )
    )
  );

  removeFromFavorites$ = createEffect(() =>
    this.actions$.pipe(
      ofType(ProductActions.removeFromFavorites),
      exhaustMap(({ productId }) =>
        this.productService.removeFromFavorites(productId).pipe(
          map(() => ProductActions.removeFromFavoritesSuccess({ productId })),
          catchError(() => of({ type: '[Product] Remove from Favorites Failure' }))
        )
      )
    )
  );

  // Reload products when filters change
  filtersChanged$ = createEffect(() =>
    this.actions$.pipe(
      ofType(ProductActions.setFilters, ProductActions.setSort, ProductActions.setPage, ProductActions.setPageSize),
      map(() => ProductActions.loadProducts({ filters: {} }))
    )
  );
}

