import { createAction, props } from '@ngrx/store';
import { Product, Category, Material, ProductFilter } from '../../models/product.model';
import { PaginatedResponse } from '../../models/common.model';

// Load Products Actions
export const loadProducts = createAction(
  '[Product] Load Products',
  props<{ filters?: ProductFilter & { page?: number; limit?: number } }>()
);

export const loadProductsSuccess = createAction(
  '[Product] Load Products Success',
  props<{ response: PaginatedResponse<Product> }>()
);

export const loadProductsFailure = createAction(
  '[Product] Load Products Failure',
  props<{ error: string }>()
);

// Load Product Details Actions
export const loadProduct = createAction(
  '[Product] Load Product',
  props<{ id: string }>()
);

export const loadProductSuccess = createAction(
  '[Product] Load Product Success',
  props<{ product: Product }>()
);

export const loadProductFailure = createAction(
  '[Product] Load Product Failure',
  props<{ error: string }>()
);

// Search Products Actions
export const searchProducts = createAction(
  '[Product] Search Products',
  props<{ query: string }>()
);

export const searchProductsSuccess = createAction(
  '[Product] Search Products Success',
  props<{ products: Product[] }>()
);

export const searchProductsFailure = createAction(
  '[Product] Search Products Failure',
  props<{ error: string }>()
);

// Load Categories Actions
export const loadCategories = createAction('[Product] Load Categories');

export const loadCategoriesSuccess = createAction(
  '[Product] Load Categories Success',
  props<{ categories: Category[] }>()
);

export const loadCategoriesFailure = createAction(
  '[Product] Load Categories Failure',
  props<{ error: string }>()
);

// Load Materials Actions
export const loadMaterials = createAction('[Product] Load Materials');

export const loadMaterialsSuccess = createAction(
  '[Product] Load Materials Success',
  props<{ materials: Material[] }>()
);

export const loadMaterialsFailure = createAction(
  '[Product] Load Materials Failure',
  props<{ error: string }>()
);

// Set Filters Actions
export const setFilters = createAction(
  '[Product] Set Filters',
  props<{ filters: ProductFilter }>()
);

export const clearFilters = createAction('[Product] Clear Filters');

// Set Sort Actions
export const setSort = createAction(
  '[Product] Set Sort',
  props<{ sort: string; order: 'asc' | 'desc' }>()
);

// Set Page Actions
export const setPage = createAction(
  '[Product] Set Page',
  props<{ page: number }>()
);

export const setPageSize = createAction(
  '[Product] Set Page Size',
  props<{ pageSize: number }>()
);

// Add to Favorites Actions
export const addToFavorites = createAction(
  '[Product] Add to Favorites',
  props<{ productId: string }>()
);

export const addToFavoritesSuccess = createAction(
  '[Product] Add to Favorites Success',
  props<{ productId: string }>()
);

export const removeFromFavorites = createAction(
  '[Product] Remove from Favorites',
  props<{ productId: string }>()
);

export const removeFromFavoritesSuccess = createAction(
  '[Product] Remove from Favorites Success',
  props<{ productId: string }>()
);

