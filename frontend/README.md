# 3D Store Frontend - Angular 18 Application

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
ng serve

# Open browser to http://localhost:4200
```

## ✅ What's Implemented (45+ files)

### Core Infrastructure (100% Complete)
- ✅ **Environment Configuration** - Dev & Production configs
- ✅ **App Configuration** - Providers, Interceptors, Store setup
- ✅ **Routing** - Complete route structure with lazy loading
- ✅ **Material UI** - All Angular Material modules configured

### Models (100% Complete)
All TypeScript interfaces defined:
- ✅ `models/common.model.ts` - ApiResponse, Pagination, Address
- ✅ `models/user.model.ts` - User, Auth, Role, Permission
- ✅ `models/product.model.ts` - Product, Category, Material
- ✅ `models/order.model.ts` - Order, OrderItem, OrderStatus
- ✅ `models/print-job.model.ts` - PrintJob, Upload, Metadata
- ✅ `models/cart.model.ts` - Cart, CartItem
- ✅ `models/seller.model.ts` - Seller, Commission, Payment
- ✅ `models/expense.model.ts` - Expense, Category, Budget

### Services (100% Complete)

#### Core Services
- ✅ `core/services/api.service.ts` - Base HTTP service
- ✅ `core/services/auth.service.ts` - Authentication & Authorization

#### Feature Services
- ✅ `services/product.service.ts` - Product management
- ✅ `services/order.service.ts` - Order management
- ✅ `services/cart.service.ts` - Shopping cart with state
- ✅ `services/upload.service.ts` - File upload with progress
- ✅ `services/websocket.service.ts` - Real-time updates
- ✅ `services/print-job.service.ts` - Print job management
- ✅ `services/seller.service.ts` - Seller dashboard
- ✅ `services/expense.service.ts` - Expense tracking

#### 3D Visualization Services
- ✅ `services/three/three.service.ts` - Three.js scene management
- ✅ `services/three/model-loader.service.ts` - STL/OBJ loading

### Guards & Interceptors (100% Complete)
- ✅ `core/guards/auth.guard.ts` - Authentication guard
- ✅ `core/guards/role.guard.ts` - Role/permission guard
- ✅ `core/interceptors/auth.interceptor.ts` - JWT injection
- ✅ `core/interceptors/error.interceptor.ts` - Error handling

### Shared Components (100% Complete)
- ✅ `shared/components/loading/` - Loading states
- ✅ `shared/components/error/` - Error display
- ✅ `shared/components/pagination/` - Pagination controls
- ✅ `shared/components/search/` - Search with filters
- ✅ `shared/components/confirmation-dialog/` - Confirmation modal

## 🔧 How to Use

### Using Services in Components

```typescript
import { Component, OnInit } from '@angular/core';
import { ProductService } from '../services/product.service';
import { Product } from '../models/product.model';

export class ProductsComponent implements OnInit {
  products: Product[] = [];
  loading = false;
  
  constructor(private productService: ProductService) {}
  
  ngOnInit() {
    this.loadProducts();
  }
  
  loadProducts() {
    this.loading = true;
    this.productService.getProducts({ page: 1, limit: 20 }).subscribe({
      next: (response) => {
        this.products = response.data;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading products:', error);
        this.loading = false;
      }
    });
  }
}
```

### Using Authentication

```typescript
import { AuthService } from './core/services/auth.service';

// Login
this.authService.login({ email, password }).subscribe({
  next: (response) => {
    // User is logged in, navigate to dashboard
    this.router.navigate(['/dashboard']);
  }
});

// Check if authenticated
const isAuth = this.authService.isAuthenticated();

// Check permissions
this.authService.hasPermission('product.create').subscribe(hasPermission => {
  if (hasPermission) {
    // Show create product button
  }
});
```

### Uploading 3D Models

```typescript
import { UploadService } from './services/upload.service';

onFileSelected(file: File) {
  this.uploadService.uploadModel(file).subscribe({
    next: (progress) => {
      if (progress.status === 'uploading') {
        this.uploadProgress = progress.progress;
      } else if (progress.status === 'completed') {
        console.log('Upload complete:', progress.response);
      }
    },
    error: (error) => {
      console.error('Upload failed:', error);
    }
  });
}
```

### Using 3D Visualization

```typescript
import { ThreeService } from './services/three/three.service';
import { ModelLoaderService } from './services/three/model-loader.service';

ngAfterViewInit() {
  // Initialize Three.js scene
  this.threeService.initScene(this.containerElement.nativeElement);
  
  // Load 3D model
  this.modelLoader.loadSTL(modelUrl).subscribe({
    next: (mesh) => {
      this.threeService.addObject(mesh);
    }
  });
}
```

### Using Shared Components

```typescript
// In your template
<app-loading 
  type="spinner" 
  [overlay]="true" 
  message="Loading products...">
</app-loading>

<app-error 
  message="Failed to load data"
  (retry)="loadData()">
</app-error>

<app-pagination
  [totalItems]="totalProducts"
  [currentPage]="currentPage"
  [pageSize]="pageSize"
  (pageChange)="onPageChange($event)">
</app-pagination>

<app-search
  placeholder="Search products..."
  [showFilters]="true"
  [filters]="productFilters"
  (search)="onSearch($event)"
  (filterChange)="onFilterChange($event)">
</app-search>
```

## 📁 Project Structure

```
frontend/src/app/
├── core/                    # Core services and guards
│   ├── services/           # Base services (API, Auth)
│   ├── guards/             # Route guards (Auth, Role)
│   └── interceptors/       # HTTP interceptors
├── models/                  # TypeScript interfaces
├── services/                # Feature services
│   └── three/              # Three.js services
├── shared/                  # Shared modules and components
│   ├── components/         # Reusable components
│   └── material.module.ts  # Material UI modules
├── pages/                   # Page components (to be created)
├── app.config.ts           # App configuration
└── app.routes.ts           # Route configuration
```

## 🔐 Authentication Flow

1. User logs in via `AuthService.login()`
2. JWT token is stored in localStorage
3. `authInterceptor` adds token to all HTTP requests
4. `authGuard` protects routes requiring authentication
5. `roleGuard` protects routes requiring specific roles/permissions

## 🎨 Styling with Angular Material

All Material UI modules are pre-configured in `shared/material.module.ts`. Simply import `MaterialModule` in your components:

```typescript
import { MaterialModule } from './shared/material.module';

@Component({
  standalone: true,
  imports: [CommonModule, MaterialModule],
  // ...
})
```

## 🌐 API Integration

### Base URL Configuration
- **Development**: `http://localhost:5000/3dstore/api/v1`
- **Production**: `https://api.3dstore.com/3dstore/api/v1`

### Environment Variables
Edit `src/environments/environment.ts` or `environment.development.ts`:

```typescript
export const environment = {
  apiUrl: 'your-api-url',
  wsUrl: 'your-websocket-url',
  maxFileSize: 104857600,
  // ...
};
```

## 📡 WebSocket Integration

Real-time updates for print jobs and orders:

```typescript
import { WebSocketService } from './services/websocket.service';

// Subscribe to print job updates
this.wsService.subscribeToPrintJobUpdates(jobId).subscribe(update => {
  console.log('Print job progress:', update);
});

// Subscribe to order updates
this.wsService.subscribeToOrderUpdates(orderId).subscribe(update => {
  console.log('Order status:', update);
});
```

## 🛣️ Routing

All routes are configured in `app.routes.ts` with lazy loading:

```typescript
// Protected routes require authentication
{ 
  path: 'dashboard', 
  canActivate: [authGuard],
  loadComponent: () => import('./pages/dashboard/dashboard.component')
}

// Admin routes require admin role
{
  path: 'admin',
  canActivate: [authGuard, roleGuard],
  data: { role: 'admin' },
  loadComponent: () => import('./pages/admin/admin.component')
}
```

## ⚡ What Still Needs Implementation

### Page Components (0%)
All page component files are configured in routing but need to be created:
- Home page
- Products list & detail
- Cart & Checkout
- Orders & Order detail
- Print jobs
- Dashboard & Profile
- Admin panel (8 sub-pages)
- Seller portal (4 sub-pages)

### NgRx Store (0%)
State management needs to be implemented:
- Actions, Reducers, Effects, Selectors
- For: Auth, Products, Cart, Orders

### i18n (0%)
- English and Arabic translation files
- Language switcher component
- RTL support

### PWA (0%)
- Service worker configuration
- Offline support
- App manifest

## 🔨 Development Commands

```bash
# Start development server
ng serve

# Build for production
ng build --configuration production

# Run tests
ng test

# Run linter
ng lint

# Generate component
ng generate component pages/home

# Generate service
ng generate service services/notification
```

## 📦 Dependencies

Key dependencies installed:
- `@angular/core` ^18.2.0
- `@angular/material` ^18.2.14
- `@ngrx/store` ^18.1.1
- `three` ^0.180.0
- `socket.io-client` ^4.7.5

## 🐛 Common Issues

### CORS Errors
Make sure backend is running and CORS is configured:
```python
# Backend config
CORS_ORIGINS=http://localhost:4200
```

### Authentication Not Working
1. Check if backend is running
2. Verify API URL in environment file
3. Check browser console for errors
4. Verify JWT token in localStorage

### 3D Model Not Loading
1. Check file format (STL, OBJ supported)
2. Verify file size < 100MB
3. Check model URL is accessible
4. Verify CORS headers for model files

## 📚 Additional Documentation

- **Component Documentation**: `/docs/frontend/components.md`
- **API Integration**: `/docs/frontend/api-integration.md`
- **Authentication**: `/docs/api/authentication.md`
- **File Upload**: `/docs/api/file-upload.md`
- **Environment Config**: `/docs/deployment/environment.md`

## 🎯 Next Steps

1. **Create Page Components** - Start with Home, Products, Cart
2. **Implement NgRx Store** - Add state management
3. **Add i18n Support** - Multi-language support
4. **Configure PWA** - Offline capabilities
5. **Add Tests** - Unit and E2E tests

## 📞 Support

For issues or questions:
- Check the documentation in `/docs/frontend/`
- Review the implementation status in `/IMPLEMENTATION_STATUS.md`
- Create an issue in the repository

---

**Status**: Core infrastructure complete, ready for page components implementation! 🚀
