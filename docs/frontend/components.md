# Angular Component Library Documentation

This document provides comprehensive documentation for all reusable Angular components in the 3D Store application.

## Overview

The component library is organized into three main categories:
- **Shared Components**: Generic, reusable components used across the application
- **Feature Components**: Business-specific components (product cards, order cards, etc.)
- **Page Components**: Full-page components representing routes

## Component Organization

```
src/app/
├── shared/components/       # Generic reusable components
│   ├── loading/
│   ├── error/
│   ├── pagination/
│   ├── search/
│   └── confirmation-dialog/
├── components/             # Feature-specific components
│   ├── file-upload/
│   ├── print-preview/
│   ├── product-card/
│   └── order-card/
└── pages/                 # Page components
    ├── home/
    ├── products/
    ├── orders/
    └── ...
```

---

## Shared Components

### Loading Component

**Path**: `src/app/shared/components/loading/loading.component.ts`

**Purpose**: Display loading states with spinner, progress bars, or skeleton loaders.

**API Reference**:

```typescript
@Component({
  selector: 'app-loading',
  templateUrl: './loading.component.html',
  styleUrls: ['./loading.component.scss']
})
export class LoadingComponent {
  @Input() type: 'spinner' | 'progress' | 'skeleton' = 'spinner';
  @Input() message?: string;
  @Input() progress?: number;
  @Input() overlay: boolean = false;
}
```

**Inputs**:
- `type` - Type of loading indicator (spinner, progress, skeleton)
- `message` - Optional loading message
- `progress` - Progress percentage (0-100) for progress bar
- `overlay` - Whether to show as full-screen overlay

**Usage Example**:

```html
<!-- Spinner -->
<app-loading type="spinner" message="Loading products..."></app-loading>

<!-- Progress bar -->
<app-loading type="progress" [progress]="uploadProgress"></app-loading>

<!-- Full-screen overlay -->
<app-loading type="spinner" message="Processing..." [overlay]="true"></app-loading>
```

---

### Error Component

**Path**: `src/app/shared/components/error/error.component.ts`

**Purpose**: Display error messages with retry functionality.

**API Reference**:

```typescript
@Component({
  selector: 'app-error',
  templateUrl: './error.component.html',
  styleUrls: ['./error.component.scss']
})
export class ErrorComponent {
  @Input() message: string;
  @Input() details?: string;
  @Input() showRetry: boolean = true;
  @Output() retry = new EventEmitter<void>();
}
```

**Inputs**:
- `message` - Error message to display
- `details` - Optional detailed error information
- `showRetry` - Whether to show retry button

**Outputs**:
- `retry` - Emitted when retry button is clicked

**Usage Example**:

```html
<app-error 
  message="Failed to load products" 
  details="Network connection error"
  (retry)="loadProducts()">
</app-error>
```

---

### Pagination Component

**Path**: `src/app/shared/components/pagination/pagination.component.ts`

**Purpose**: Navigate through paginated data with page size options.

**API Reference**:

```typescript
@Component({
  selector: 'app-pagination',
  templateUrl: './pagination.component.html',
  styleUrls: ['./pagination.component.scss']
})
export class PaginationComponent {
  @Input() totalItems: number;
  @Input() currentPage: number = 1;
  @Input() pageSize: number = 10;
  @Input() pageSizeOptions: number[] = [10, 20, 50, 100];
  @Output() pageChange = new EventEmitter<number>();
  @Output() pageSizeChange = new EventEmitter<number>();
}
```

**Inputs**:
- `totalItems` - Total number of items
- `currentPage` - Current page number (1-based)
- `pageSize` - Number of items per page
- `pageSizeOptions` - Available page size options

**Outputs**:
- `pageChange` - Emitted when page changes
- `pageSizeChange` - Emitted when page size changes

**Usage Example**:

```html
<app-pagination 
  [totalItems]="totalProducts" 
  [currentPage]="currentPage"
  [pageSize]="pageSize"
  (pageChange)="onPageChange($event)"
  (pageSizeChange)="onPageSizeChange($event)">
</app-pagination>
```

---

### Search Component

**Path**: `src/app/shared/components/search/search.component.ts`

**Purpose**: Real-time search with advanced filtering capabilities.

**API Reference**:

```typescript
@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.scss']
})
export class SearchComponent {
  @Input() placeholder: string = 'Search...';
  @Input() debounceTime: number = 300;
  @Input() showFilters: boolean = false;
  @Input() filters: SearchFilter[] = [];
  @Output() search = new EventEmitter<string>();
  @Output() filterChange = new EventEmitter<any>();
}
```

**Inputs**:
- `placeholder` - Search input placeholder text
- `debounceTime` - Debounce time in milliseconds
- `showFilters` - Whether to show advanced filters
- `filters` - Available filter options

**Outputs**:
- `search` - Emitted when search query changes
- `filterChange` - Emitted when filters change

**Usage Example**:

```html
<app-search 
  placeholder="Search products..."
  [showFilters]="true"
  [filters]="productFilters"
  (search)="onSearch($event)"
  (filterChange)="onFilterChange($event)">
</app-search>
```

---

### Confirmation Dialog Component

**Path**: `src/app/shared/components/confirmation-dialog/confirmation-dialog.component.ts`

**Purpose**: Generic confirmation modal for user actions.

**API Reference**:

```typescript
@Component({
  selector: 'app-confirmation-dialog',
  templateUrl: './confirmation-dialog.component.html',
  styleUrls: ['./confirmation-dialog.component.scss']
})
export class ConfirmationDialogComponent {
  @Inject(MAT_DIALOG_DATA) public data: {
    title: string;
    message: string;
    confirmText?: string;
    cancelText?: string;
    confirmColor?: 'primary' | 'accent' | 'warn';
  };
}
```

**Dialog Data**:
- `title` - Dialog title
- `message` - Confirmation message
- `confirmText` - Confirm button text (default: 'Confirm')
- `cancelText` - Cancel button text (default: 'Cancel')
- `confirmColor` - Confirm button color

**Usage Example**:

```typescript
// In component
const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
  data: {
    title: 'Delete Product',
    message: 'Are you sure you want to delete this product?',
    confirmText: 'Delete',
    cancelText: 'Cancel',
    confirmColor: 'warn'
  }
});

dialogRef.afterClosed().subscribe(result => {
  if (result) {
    this.deleteProduct();
  }
});
```

---

## Feature Components

### File Upload Component

**Path**: `src/app/components/file-upload/file-upload.component.ts`

**Purpose**: Upload 3D model files with drag-and-drop support.

**API Reference**:

```typescript
@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.scss']
})
export class FileUploadComponent {
  @Input() accept: string = '.stl,.obj,.3mf';
  @Input() maxSize: number = 104857600; // 100MB
  @Input() multiple: boolean = false;
  @Output() filesSelected = new EventEmitter<File[]>();
  @Output() uploadProgress = new EventEmitter<number>();
  @Output() uploadComplete = new EventEmitter<any>();
  @Output() uploadError = new EventEmitter<string>();
}
```

**Inputs**:
- `accept` - Accepted file types
- `maxSize` - Maximum file size in bytes
- `multiple` - Allow multiple file selection

**Outputs**:
- `filesSelected` - Emitted when files are selected
- `uploadProgress` - Emitted during upload with progress percentage
- `uploadComplete` - Emitted when upload completes
- `uploadError` - Emitted on upload error

**Usage Example**:

```html
<app-file-upload 
  accept=".stl,.obj,.3mf"
  [maxSize]="104857600"
  [multiple]="false"
  (filesSelected)="onFilesSelected($event)"
  (uploadProgress)="onUploadProgress($event)"
  (uploadComplete)="onUploadComplete($event)"
  (uploadError)="onUploadError($event)">
</app-file-upload>
```

---

### 3D Model Preview Component

**Path**: `src/app/components/print-preview/print-preview.component.ts`

**Purpose**: Preview 3D models using Three.js.

**API Reference**:

```typescript
@Component({
  selector: 'app-print-preview',
  templateUrl: './print-preview.component.html',
  styleUrls: ['./print-preview.component.scss']
})
export class PrintPreviewComponent implements OnInit, OnDestroy {
  @Input() modelUrl: string;
  @Input() modelType: 'stl' | 'obj' | '3mf';
  @Input() showControls: boolean = true;
  @Input() backgroundColor: string = '#f0f0f0';
  @Output() modelLoaded = new EventEmitter<void>();
  @Output() loadError = new EventEmitter<string>();
  
  // Public methods
  resetCamera(): void;
  takeScreenshot(): string;
  toggleWireframe(): void;
}
```

**Inputs**:
- `modelUrl` - URL to 3D model file
- `modelType` - Type of 3D model
- `showControls` - Show camera controls UI
- `backgroundColor` - Scene background color

**Outputs**:
- `modelLoaded` - Emitted when model loads successfully
- `loadError` - Emitted on load error

**Public Methods**:
- `resetCamera()` - Reset camera to default position
- `takeScreenshot()` - Capture screenshot, returns base64 image
- `toggleWireframe()` - Toggle wireframe view

**Usage Example**:

```html
<app-print-preview 
  [modelUrl]="product.modelUrl"
  [modelType]="'stl'"
  [showControls]="true"
  (modelLoaded)="onModelLoaded()"
  (loadError)="onLoadError($event)">
</app-print-preview>
```

---

### Product Card Component

**Path**: `src/app/components/product-card/product-card.component.ts`

**Purpose**: Display product information in a card layout.

**API Reference**:

```typescript
@Component({
  selector: 'app-product-card',
  templateUrl: './product-card.component.html',
  styleUrls: ['./product-card.component.scss']
})
export class ProductCardComponent {
  @Input() product: Product;
  @Input() showActions: boolean = true;
  @Input() layout: 'grid' | 'list' = 'grid';
  @Output() addToCart = new EventEmitter<Product>();
  @Output() addToFavorites = new EventEmitter<Product>();
  @Output() quickView = new EventEmitter<Product>();
}
```

**Inputs**:
- `product` - Product data
- `showActions` - Show action buttons
- `layout` - Card layout style

**Outputs**:
- `addToCart` - Emitted when add to cart is clicked
- `addToFavorites` - Emitted when favorite is toggled
- `quickView` - Emitted when quick view is clicked

**Usage Example**:

```html
<app-product-card 
  [product]="product"
  [layout]="'grid'"
  (addToCart)="addToCart($event)"
  (addToFavorites)="toggleFavorite($event)"
  (quickView)="showQuickView($event)">
</app-product-card>
```

---

### Order Card Component

**Path**: `src/app/components/order-card/order-card.component.ts`

**Purpose**: Display order information with status tracking.

**API Reference**:

```typescript
@Component({
  selector: 'app-order-card',
  templateUrl: './order-card.component.html',
  styleUrls: ['./order-card.component.scss']
})
export class OrderCardComponent {
  @Input() order: Order;
  @Input() showTimeline: boolean = true;
  @Input() showActions: boolean = true;
  @Output() viewDetails = new EventEmitter<Order>();
  @Output() cancelOrder = new EventEmitter<Order>();
  @Output() downloadInvoice = new EventEmitter<Order>();
}
```

**Inputs**:
- `order` - Order data
- `showTimeline` - Show order timeline
- `showActions` - Show action buttons

**Outputs**:
- `viewDetails` - Emitted when view details is clicked
- `cancelOrder` - Emitted when cancel is clicked
- `downloadInvoice` - Emitted when download invoice is clicked

**Usage Example**:

```html
<app-order-card 
  [order]="order"
  [showTimeline]="true"
  (viewDetails)="viewOrderDetails($event)"
  (cancelOrder)="cancelOrder($event)"
  (downloadInvoice)="downloadInvoice($event)">
</app-order-card>
```

---

## Best Practices

### Component Design Principles

1. **Single Responsibility**: Each component should have one clear purpose
2. **Reusability**: Design components to be used in multiple contexts
3. **Encapsulation**: Use proper input/output bindings, avoid global state
4. **Performance**: Use OnPush change detection when possible
5. **Accessibility**: Follow WCAG guidelines, use proper ARIA attributes

### Naming Conventions

- **Component selectors**: Use `app-` prefix (e.g., `app-product-card`)
- **Files**: Use kebab-case (e.g., `product-card.component.ts`)
- **Classes**: Use PascalCase (e.g., `ProductCardComponent`)
- **Inputs/Outputs**: Use camelCase (e.g., `@Input() productId`)

### Input/Output Guidelines

**Inputs**:
- Use for passing data into components
- Add type annotations
- Provide default values when appropriate
- Use `@Input()` decorator

**Outputs**:
- Use for emitting events to parent
- Use EventEmitter
- Name as actions (e.g., `click`, `change`, `submit`)
- Use `@Output()` decorator

### Change Detection Strategy

Use OnPush strategy for better performance:

```typescript
@Component({
  selector: 'app-product-card',
  templateUrl: './product-card.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ProductCardComponent {
  // ...
}
```

### Template Syntax

**Property Binding**:
```html
<app-product-card [product]="currentProduct"></app-product-card>
```

**Event Binding**:
```html
<app-product-card (addToCart)="handleAddToCart($event)"></app-product-card>
```

**Two-way Binding**:
```html
<app-search [(query)]="searchQuery"></app-search>
```

### Styling Guidelines

1. **Use component-scoped styles**: Styles in `.component.scss` are scoped to component
2. **Use CSS variables**: For theming and consistency
3. **Follow BEM naming**: For CSS class names
4. **Responsive design**: Use media queries and flexbox/grid

### Testing

Each component should have:
- Unit tests for logic
- Component tests for rendering
- Integration tests for user interactions

Example:
```typescript
describe('ProductCardComponent', () => {
  it('should display product name', () => {
    const fixture = TestBed.createComponent(ProductCardComponent);
    fixture.componentInstance.product = mockProduct;
    fixture.detectChanges();
    const name = fixture.nativeElement.querySelector('.product-name');
    expect(name.textContent).toBe(mockProduct.name);
  });
});
```

## Component Lifecycle

Understanding Angular lifecycle hooks:

- `ngOnInit()` - Initialize component after first input binding
- `ngOnChanges()` - React to input property changes
- `ngOnDestroy()` - Cleanup before component is destroyed
- `ngAfterViewInit()` - After view initialization

Example:
```typescript
export class ProductCardComponent implements OnInit, OnDestroy {
  private subscription: Subscription;
  
  ngOnInit(): void {
    this.subscription = this.productService.getProduct(this.productId)
      .subscribe(product => this.product = product);
  }
  
  ngOnDestroy(): void {
    this.subscription?.unsubscribe();
  }
}
```

## Accessibility

### ARIA Attributes

```html
<button 
  aria-label="Add to cart"
  [attr.aria-disabled]="!product.inStock">
  Add to Cart
</button>
```

### Keyboard Navigation

Ensure all interactive elements are keyboard accessible:

```typescript
@HostListener('keydown.enter')
onEnter(): void {
  this.addToCart.emit(this.product);
}
```

### Focus Management

```typescript
@ViewChild('firstInput') firstInput: ElementRef;

ngAfterViewInit(): void {
  this.firstInput.nativeElement.focus();
}
```

## Performance Optimization

### Lazy Loading

```typescript
const routes: Routes = [
  {
    path: 'admin',
    loadChildren: () => import('./admin/admin.module')
      .then(m => m.AdminModule)
  }
];
```

### TrackBy Function

```html
<div *ngFor="let product of products; trackBy: trackByProductId">
  <app-product-card [product]="product"></app-product-card>
</div>
```

```typescript
trackByProductId(index: number, product: Product): string {
  return product.id;
}
```

### Virtual Scrolling

For large lists:

```html
<cdk-virtual-scroll-viewport itemSize="200">
  <app-product-card 
    *cdkVirtualFor="let product of products"
    [product]="product">
  </app-product-card>
</cdk-virtual-scroll-viewport>
```

## Additional Resources

- [Angular Component Documentation](https://angular.io/guide/component-overview)
- [Angular Material Components](https://material.angular.io/components)
- [Angular Style Guide](https://angular.io/guide/styleguide)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

**Last Updated**: January 2025  
**Version**: 1.0.0

