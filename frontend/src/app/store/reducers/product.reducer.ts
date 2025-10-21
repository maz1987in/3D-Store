import { createReducer, on } from '@ngrx/store';
import { Product, Category, Material, ProductFilter } from '../../models/product.model';
import { PaginationMeta } from '../../models/common.model';
import * as ProductActions from '../actions/product.actions';

export interface ProductState {
  products: Product[];
  currentProduct: Product | null;
  categories: Category[];
  materials: Material[];
  filters: ProductFilter;
  pagination: PaginationMeta | null;
  loading: boolean;
  error: string | null;
  favoriteIds: string[];
}

export const initialState: ProductState = {
  products: [],
  currentProduct: null,
  categories: [],
  materials: [],
  filters: {},
  pagination: null,
  loading: false,
  error: null,
  favoriteIds: []
};

export const productReducer = createReducer(
  initialState,
  
  // Load Products
  on(ProductActions.loadProducts, (state) => ({
    ...state,
    loading: true,
    error: null
  })),
  
  on(ProductActions.loadProductsSuccess, (state, { response }) => ({
    ...state,
    products: response.data,
    pagination: response.meta,
    loading: false,
    error: null
  })),
  
  on(ProductActions.loadProductsFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Load Product
  on(ProductActions.loadProduct, (state) => ({
    ...state,
    loading: true,
    error: null
  })),
  
  on(ProductActions.loadProductSuccess, (state, { product }) => ({
    ...state,
    currentProduct: product,
    loading: false,
    error: null
  })),
  
  on(ProductActions.loadProductFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Search Products
  on(ProductActions.searchProducts, (state) => ({
    ...state,
    loading: true,
    error: null
  })),
  
  on(ProductActions.searchProductsSuccess, (state, { products }) => ({
    ...state,
    products,
    loading: false,
    error: null
  })),
  
  on(ProductActions.searchProductsFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Load Categories
  on(ProductActions.loadCategories, (state) => ({
    ...state,
    loading: true
  })),
  
  on(ProductActions.loadCategoriesSuccess, (state, { categories }) => ({
    ...state,
    categories,
    loading: false
  })),
  
  on(ProductActions.loadCategoriesFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Load Materials
  on(ProductActions.loadMaterials, (state) => ({
    ...state,
    loading: true
  })),
  
  on(ProductActions.loadMaterialsSuccess, (state, { materials }) => ({
    ...state,
    materials,
    loading: false
  })),
  
  on(ProductActions.loadMaterialsFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Filters
  on(ProductActions.setFilters, (state, { filters }) => ({
    ...state,
    filters: { ...state.filters, ...filters }
  })),
  
  on(ProductActions.clearFilters, (state) => ({
    ...state,
    filters: {}
  })),
  
  // Sort
  on(ProductActions.setSort, (state, { sort, order }) => ({
    ...state,
    filters: { ...state.filters, sort, order }
  })),
  
  // Pagination
  on(ProductActions.setPage, (state, { page }) => ({
    ...state,
    pagination: state.pagination ? { ...state.pagination, page } : null
  })),
  
  on(ProductActions.setPageSize, (state, { pageSize }) => ({
    ...state,
    pagination: state.pagination ? { ...state.pagination, per_page: pageSize } : null
  })),
  
  // Favorites
  on(ProductActions.addToFavoritesSuccess, (state, { productId }) => ({
    ...state,
    favoriteIds: [...state.favoriteIds, productId]
  })),
  
  on(ProductActions.removeFromFavoritesSuccess, (state, { productId }) => ({
    ...state,
    favoriteIds: state.favoriteIds.filter(id => id !== productId)
  }))
);

