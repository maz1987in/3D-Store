import { createFeatureSelector, createSelector } from '@ngrx/store';
import { ProductState } from '../reducers/product.reducer';

export const selectProductState = createFeatureSelector<ProductState>('product');

export const selectAllProducts = createSelector(
  selectProductState,
  (state) => state.products
);

export const selectCurrentProduct = createSelector(
  selectProductState,
  (state) => state.currentProduct
);

export const selectCategories = createSelector(
  selectProductState,
  (state) => state.categories
);

export const selectMaterials = createSelector(
  selectProductState,
  (state) => state.materials
);

export const selectProductFilters = createSelector(
  selectProductState,
  (state) => state.filters
);

export const selectProductPagination = createSelector(
  selectProductState,
  (state) => state.pagination
);

export const selectProductLoading = createSelector(
  selectProductState,
  (state) => state.loading
);

export const selectProductError = createSelector(
  selectProductState,
  (state) => state.error
);

export const selectFavoriteIds = createSelector(
  selectProductState,
  (state) => state.favoriteIds
);

export const selectTotalProducts = createSelector(
  selectProductPagination,
  (pagination) => pagination?.total || 0
);

export const selectCurrentPage = createSelector(
  selectProductPagination,
  (pagination) => pagination?.page || 1
);

export const selectPageSize = createSelector(
  selectProductPagination,
  (pagination) => pagination?.per_page || 20
);

export const selectTotalPages = createSelector(
  selectProductPagination,
  (pagination) => pagination?.pages || 1
);

export const selectProductById = (productId: string) =>
  createSelector(selectAllProducts, (products) =>
    products.find(p => p.id === productId)
  );

export const selectProductsByCategory = (categoryId: string) =>
  createSelector(selectAllProducts, (products) =>
    products.filter(p => p.category_id === categoryId)
  );

export const selectFeaturedProducts = createSelector(
  selectAllProducts,
  (products) => products.filter(p => p.is_featured)
);

export const selectProductIsFavorite = (productId: string) =>
  createSelector(selectFavoriteIds, (favoriteIds) =>
    favoriteIds.includes(productId)
  );

export const selectActiveCategoryId = createSelector(
  selectProductFilters,
  (filters) => filters.category_id
);

export const selectActiveCategory = createSelector(
  selectCategories,
  selectActiveCategoryId,
  (categories, categoryId) =>
    categoryId ? categories.find(c => c.id === categoryId) : null
);

