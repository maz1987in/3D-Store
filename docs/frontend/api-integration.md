# Frontend-Backend API Integration Guide

This document provides comprehensive guidance on integrating the Angular frontend with the Flask backend API.

## Overview

The 3D Store frontend communicates with the backend through:
- **REST API**: HTTP requests for CRUD operations
- **WebSocket**: Real-time updates for print jobs and orders
- **File Upload**: Multipart form data for 3D model files

## API Configuration

### Environment Setup

**File**: `src/environments/environment.ts`

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:5000/3dstore/api/v1',
  wsUrl: 'ws://localhost:5000/ws',
  uploadUrl: 'http://localhost:5000/3dstore/api/v1/upload',
  maxFileSize: 104857600, // 100MB
  supportedFormats: ['.stl', '.obj', '.3mf'],
  tokenKey: 'auth_token',
  refreshTokenKey: 'refresh_token'
};
```

**Production**: `src/environments/environment.prod.ts`

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://api.3dstore.com/3dstore/api/v1',
  wsUrl: 'wss://api.3dstore.com/ws',
  uploadUrl: 'https://api.3dstore.com/3dstore/api/v1/upload',
  maxFileSize: 104857600,
  supportedFormats: ['.stl', '.obj', '.3mf'],
  tokenKey: 'auth_token',
  refreshTokenKey: 'refresh_token'
};
```

---

## Base API Service

### API Service Implementation

**File**: `src/app/services/api.service.ts`

```typescript
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface ApiResponse<T> {
  data: T;
  message: string;
  status: number;
}

export interface PaginationMeta {
  page: number;
  per_page: number;
  total: number;
  pages: number;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  /**
   * GET request
   */
  get<T>(endpoint: string, params?: any): Observable<T> {
    const httpParams = this.buildParams(params);
    return this.http.get<ApiResponse<T>>(`${this.apiUrl}/${endpoint}`, { params: httpParams })
      .pipe(
        map(response => response.data),
        catchError(this.handleError)
      );
  }

  /**
   * POST request
   */
  post<T>(endpoint: string, data: any): Observable<T> {
    return this.http.post<ApiResponse<T>>(`${this.apiUrl}/${endpoint}`, data)
      .pipe(
        map(response => response.data),
        catchError(this.handleError)
      );
  }

  /**
   * PUT request
   */
  put<T>(endpoint: string, data: any): Observable<T> {
    return this.http.put<ApiResponse<T>>(`${this.apiUrl}/${endpoint}`, data)
      .pipe(
        map(response => response.data),
        catchError(this.handleError)
      );
  }

  /**
   * DELETE request
   */
  delete<T>(endpoint: string): Observable<T> {
    return this.http.delete<ApiResponse<T>>(`${this.apiUrl}/${endpoint}`)
      .pipe(
        map(response => response.data),
        catchError(this.handleError)
      );
  }

  /**
   * Upload file
   */
  upload<T>(endpoint: string, file: File, additionalData?: any): Observable<T> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (additionalData) {
      Object.keys(additionalData).forEach(key => {
        formData.append(key, additionalData[key]);
      });
    }

    return this.http.post<ApiResponse<T>>(`${this.apiUrl}/${endpoint}`, formData)
      .pipe(
        map(response => response.data),
        catchError(this.handleError)
      );
  }

  /**
   * Build HTTP params
   */
  private buildParams(params?: any): HttpParams {
    let httpParams = new HttpParams();
    
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key].toString());
        }
      });
    }
    
    return httpParams;
  }

  /**
   * Handle HTTP errors
   */
  private handleError(error: any): Observable<never> {
    let errorMessage = 'An error occurred';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = error.error.message;
    } else {
      // Server-side error
      errorMessage = error.error?.error?.message || error.error?.message || error.message;
    }
    
    console.error('API Error:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}
```

---

## HTTP Interceptors

### Authentication Interceptor

**File**: `src/app/interceptors/auth.interceptor.ts`

```typescript
import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    // Add JWT token to headers
    const token = this.authService.getToken();
    
    if (token) {
      request = request.clone({
        setHeaders: {
          'x-access-tokens': token
        }
      });
    }

    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) {
          // Token expired or invalid
          this.authService.logout();
          this.router.navigate(['/login']);
        }
        return throwError(() => error);
      })
    );
  }
}
```

### Logging Interceptor

**File**: `src/app/interceptors/logging.interceptor.ts`

```typescript
import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpResponse
} from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable()
export class LoggingInterceptor implements HttpInterceptor {
  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    const started = Date.now();
    
    return next.handle(request).pipe(
      tap(event => {
        if (event instanceof HttpResponse) {
          const elapsed = Date.now() - started;
          console.log(`Request for ${request.urlWithParams} took ${elapsed} ms.`);
        }
      })
    );
  }
}
```

### Error Interceptor

**File**: `src/app/interceptors/error.interceptor.ts`

```typescript
import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { MatSnackBar } from '@angular/material/snack-bar';

@Injectable()
export class ErrorInterceptor implements HttpInterceptor {
  constructor(private snackBar: MatSnackBar) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        let errorMessage = 'An error occurred';
        
        if (error.error instanceof ErrorEvent) {
          // Client-side error
          errorMessage = error.error.message;
        } else {
          // Server-side error
          errorMessage = error.error?.error?.message || error.error?.message || error.message;
        }
        
        // Show error notification
        this.snackBar.open(errorMessage, 'Close', {
          duration: 5000,
          panelClass: ['error-snackbar']
        });
        
        return throwError(() => error);
      })
    );
  }
}
```

---

## Feature Services

### Product Service

**File**: `src/app/services/product.service.ts`

```typescript
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Product, Category, Material } from '../models/product.model';

@Injectable({
  providedIn: 'root'
})
export class ProductService {
  constructor(private api: ApiService) {}

  /**
   * Get all products with optional filters
   */
  getProducts(params?: {
    page?: number;
    limit?: number;
    category?: string;
    material?: string;
    minPrice?: number;
    maxPrice?: number;
    sort?: string;
    order?: 'asc' | 'desc';
  }): Observable<{ products: Product[]; meta: any }> {
    return this.api.get('products', params);
  }

  /**
   * Get product by ID
   */
  getProduct(id: string): Observable<Product> {
    return this.api.get(`products/${id}`);
  }

  /**
   * Search products
   */
  searchProducts(query: string): Observable<Product[]> {
    return this.api.get('products/search', { q: query });
  }

  /**
   * Get categories
   */
  getCategories(): Observable<Category[]> {
    return this.api.get('categories');
  }

  /**
   * Get materials
   */
  getMaterials(): Observable<Material[]> {
    return this.api.get('materials');
  }
}
```

### Order Service

**File**: `src/app/services/order.service.ts`

```typescript
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Order, OrderItem } from '../models/order.model';

@Injectable({
  providedIn: 'root'
})
export class OrderService {
  constructor(private api: ApiService) {}

  /**
   * Create new order
   */
  createOrder(orderData: {
    items: OrderItem[];
    shipping_address: any;
    payment_method: string;
  }): Observable<Order> {
    return this.api.post('orders', orderData);
  }

  /**
   * Get user orders
   */
  getUserOrders(params?: {
    page?: number;
    limit?: number;
    status?: string;
  }): Observable<{ orders: Order[]; meta: any }> {
    return this.api.get('orders', params);
  }

  /**
   * Get order by ID
   */
  getOrder(id: string): Observable<Order> {
    return this.api.get(`orders/${id}`);
  }

  /**
   * Update order status
   */
  updateOrderStatus(id: string, status: string): Observable<Order> {
    return this.api.put(`orders/${id}`, { status });
  }

  /**
   * Cancel order
   */
  cancelOrder(id: string): Observable<Order> {
    return this.api.put(`orders/${id}/cancel`, {});
  }
}
```

### Upload Service

**File**: `src/app/services/upload.service.ts`

```typescript
import { Injectable } from '@angular/core';
import { HttpClient, HttpEventType } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface UploadProgress {
  progress: number;
  loaded: number;
  total: number;
}

@Injectable({
  providedIn: 'root'
})
export class UploadService {
  private uploadUrl = environment.uploadUrl;

  constructor(private http: HttpClient) {}

  /**
   * Upload 3D model file with progress tracking
   */
  uploadModel(file: File, metadata?: any): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', this.getFileExtension(file.name));
    
    if (metadata) {
      Object.keys(metadata).forEach(key => {
        formData.append(key, metadata[key]);
      });
    }

    const progressSubject = new Subject<UploadProgress>();

    this.http.post(`${this.uploadUrl}/model`, formData, {
      reportProgress: true,
      observe: 'events'
    }).subscribe({
      next: (event) => {
        if (event.type === HttpEventType.UploadProgress) {
          const progress = Math.round(100 * event.loaded / (event.total || event.loaded));
          progressSubject.next({
            progress,
            loaded: event.loaded,
            total: event.total || 0
          });
        } else if (event.type === HttpEventType.Response) {
          progressSubject.next({ progress: 100, loaded: event.body, total: 100 });
          progressSubject.complete();
        }
      },
      error: (error) => progressSubject.error(error)
    });

    return progressSubject.asObservable();
  }

  /**
   * Validate file before upload
   */
  validateFile(file: File): { valid: boolean; error?: string } {
    const extension = this.getFileExtension(file.name);
    
    if (!environment.supportedFormats.includes(extension)) {
      return {
        valid: false,
        error: `Unsupported file format. Supported formats: ${environment.supportedFormats.join(', ')}`
      };
    }
    
    if (file.size > environment.maxFileSize) {
      return {
        valid: false,
        error: `File size exceeds maximum allowed size of ${environment.maxFileSize / 1024 / 1024}MB`
      };
    }
    
    return { valid: true };
  }

  private getFileExtension(filename: string): string {
    return '.' + filename.split('.').pop()?.toLowerCase();
  }
}
```

---

## Error Handling Strategies

### Service-Level Error Handling

```typescript
import { catchError, retry } from 'rxjs/operators';
import { throwError } from 'rxjs';

getProducts(): Observable<Product[]> {
  return this.api.get<Product[]>('products').pipe(
    retry(2), // Retry failed requests twice
    catchError(error => {
      console.error('Failed to load products:', error);
      return throwError(() => new Error('Failed to load products'));
    })
  );
}
```

### Component-Level Error Handling

```typescript
export class ProductsComponent implements OnInit {
  products: Product[] = [];
  loading = false;
  error: string | null = null;

  ngOnInit(): void {
    this.loadProducts();
  }

  loadProducts(): void {
    this.loading = true;
    this.error = null;

    this.productService.getProducts().subscribe({
      next: (data) => {
        this.products = data.products;
        this.loading = false;
      },
      error: (error) => {
        this.error = error.message;
        this.loading = false;
      }
    });
  }

  retry(): void {
    this.loadProducts();
  }
}
```

---

## Caching Strategies

### Simple In-Memory Cache

```typescript
import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class CacheService {
  private cache = new Map<string, any>();
  private cacheTime = new Map<string, number>();
  private defaultTTL = 5 * 60 * 1000; // 5 minutes

  get<T>(key: string): T | null {
    const cached = this.cache.get(key);
    const timestamp = this.cacheTime.get(key);
    
    if (cached && timestamp && Date.now() - timestamp < this.defaultTTL) {
      return cached;
    }
    
    this.cache.delete(key);
    this.cacheTime.delete(key);
    return null;
  }

  set(key: string, value: any): void {
    this.cache.set(key, value);
    this.cacheTime.set(key, Date.now());
  }

  clear(): void {
    this.cache.clear();
    this.cacheTime.clear();
  }
}
```

### Using Cache in Service

```typescript
getProducts(): Observable<Product[]> {
  const cacheKey = 'products';
  const cached = this.cacheService.get<Product[]>(cacheKey);
  
  if (cached) {
    return of(cached);
  }
  
  return this.api.get<Product[]>('products').pipe(
    tap(products => this.cacheService.set(cacheKey, products))
  );
}
```

---

## Request/Response Transformation

### Custom Response Mapping

```typescript
import { map } from 'rxjs/operators';

getProducts(): Observable<Product[]> {
  return this.api.get<any>('products').pipe(
    map(response => response.products.map(product => ({
      id: product.id,
      name: product.name,
      price: parseFloat(product.base_price),
      imageUrl: product.image_url,
      category: product.category.name
    })))
  );
}
```

---

## Best Practices

### 1. Use TypeScript Interfaces

Always define interfaces for API responses:

```typescript
export interface ProductResponse {
  products: Product[];
  meta: PaginationMeta;
}
```

### 2. Handle Loading States

```typescript
loading$ = new BehaviorSubject<boolean>(false);

loadData(): void {
  this.loading$.next(true);
  this.service.getData().subscribe({
    next: (data) => {
      this.data = data;
      this.loading$.next(false);
    },
    error: () => this.loading$.next(false)
  });
}
```

### 3. Unsubscribe from Observables

```typescript
private destroy$ = new Subject<void>();

ngOnInit(): void {
  this.service.getData()
    .pipe(takeUntil(this.destroy$))
    .subscribe(data => this.data = data);
}

ngOnDestroy(): void {
  this.destroy$.next();
  this.destroy$.complete();
}
```

### 4. Use Async Pipe

```typescript
// In component
products$ = this.productService.getProducts();

// In template
<div *ngIf="products$ | async as products">
  <app-product-card *ngFor="let product of products" [product]="product">
  </app-product-card>
</div>
```

### 5. Error Recovery

```typescript
import { catchError, retryWhen, delay, take } from 'rxjs/operators';

getData(): Observable<any> {
  return this.api.get('data').pipe(
    retryWhen(errors =>
      errors.pipe(
        delay(1000),
        take(3)
      )
    ),
    catchError(error => {
      console.error('Failed after retries:', error);
      return of([]);
    })
  );
}
```

---

## Testing API Integration

### Mocking HTTP Requests

```typescript
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';

describe('ProductService', () => {
  let service: ProductService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ProductService]
    });
    
    service = TestBed.inject(ProductService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  it('should fetch products', () => {
    const mockProducts = [{ id: '1', name: 'Test Product' }];

    service.getProducts().subscribe(products => {
      expect(products).toEqual(mockProducts);
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/products`);
    expect(req.request.method).toBe('GET');
    req.flush({ data: mockProducts });
  });

  afterEach(() => {
    httpMock.verify();
  });
});
```

---

## Additional Resources

- [Angular HTTP Client Guide](https://angular.io/guide/http)
- [RxJS Documentation](https://rxjs.dev/)
- [Angular Interceptors](https://angular.io/guide/http#intercepting-requests-and-responses)

---

**Last Updated**: January 2025  
**Version**: 1.0.0

