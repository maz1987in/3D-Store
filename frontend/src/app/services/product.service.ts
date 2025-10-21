import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../core/services/api.service';
import {
  Product,
  Category,
  Material,
  ProductFilter,
  ProductReview
} from '../models/product.model';
import { PaginatedResponse } from '../models/common.model';

@Injectable({
  providedIn: 'root'
})
export class ProductService {
  constructor(private api: ApiService) {}

  /**
   * Get all products with optional filters
   */
  getProducts(params?: ProductFilter & {
    page?: number;
    limit?: number;
  }): Observable<PaginatedResponse<Product>> {
    return this.api.getPaginated<Product>('products', params);
  }

  /**
   * Get product by ID
   */
  getProduct(id: string): Observable<Product> {
    return this.api.get<Product>(`products/${id}`);
  }

  /**
   * Search products
   */
  searchProducts(query: string, params?: any): Observable<Product[]> {
    return this.api.get<Product[]>('products/search', { q: query, ...params });
  }

  /**
   * Get featured products
   */
  getFeaturedProducts(limit: number = 10): Observable<Product[]> {
    return this.api.get<Product[]>('products/featured', { limit });
  }

  /**
   * Get products by category
   */
  getProductsByCategory(categoryId: string, params?: any): Observable<PaginatedResponse<Product>> {
    return this.api.getPaginated<Product>(`categories/${categoryId}/products`, params);
  }

  /**
   * Get all categories
   */
  getCategories(): Observable<Category[]> {
    return this.api.get<Category[]>('categories');
  }

  /**
   * Get category by ID
   */
  getCategory(id: string): Observable<Category> {
    return this.api.get<Category>(`categories/${id}`);
  }

  /**
   * Get featured categories
   */
  getFeaturedCategories(): Observable<Category[]> {
    return this.api.get<Category[]>('categories/featured');
  }

  /**
   * Get all materials
   */
  getMaterials(): Observable<Material[]> {
    return this.api.get<Material[]>('materials');
  }

  /**
   * Get material by ID
   */
  getMaterial(id: string): Observable<Material> {
    return this.api.get<Material>(`materials/${id}`);
  }

  /**
   * Get product reviews
   */
  getProductReviews(productId: string, params?: { page?: number; limit?: number }): Observable<PaginatedResponse<ProductReview>> {
    return this.api.getPaginated<ProductReview>(`products/${productId}/reviews`, params);
  }

  /**
   * Add product review
   */
  addProductReview(productId: string, review: { rating: number; comment?: string }): Observable<ProductReview> {
    return this.api.post<ProductReview>(`products/${productId}/reviews`, review);
  }

  /**
   * Add product to favorites
   */
  addToFavorites(productId: string): Observable<void> {
    return this.api.post<void>(`products/${productId}/favorite`, {});
  }

  /**
   * Remove product from favorites
   */
  removeFromFavorites(productId: string): Observable<void> {
    return this.api.delete<void>(`products/${productId}/favorite`);
  }

  /**
   * Get user's favorite products
   */
  getFavoriteProducts(): Observable<Product[]> {
    return this.api.get<Product[]>('products/favorites');
  }

  /**
   * Create product (admin only)
   */
  createProduct(product: Partial<Product>): Observable<Product> {
    return this.api.post<Product>('products', product);
  }

  /**
   * Update product (admin only)
   */
  updateProduct(id: string, product: Partial<Product>): Observable<Product> {
    return this.api.put<Product>(`products/${id}`, product);
  }

  /**
   * Delete product (admin only)
   */
  deleteProduct(id: string): Observable<void> {
    return this.api.delete<void>(`products/${id}`);
  }
}

