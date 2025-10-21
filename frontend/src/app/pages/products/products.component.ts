import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { MaterialModule } from '../../shared/material.module';
import { LoadingComponent } from '../../shared/components/loading/loading.component';
import { ErrorComponent } from '../../shared/components/error/error.component';
import { PaginationComponent } from '../../shared/components/pagination/pagination.component';
import { SearchComponent } from '../../shared/components/search/search.component';
import { ProductService } from '../../services/product.service';
import { CartService } from '../../services/cart.service';
import { Product, Category, Material, ProductFilter } from '../../models/product.model';
import { SearchFilter } from '../../models/common.model';

@Component({
  selector: 'app-products',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
    MaterialModule,
    LoadingComponent,
    ErrorComponent,
    PaginationComponent,
    SearchComponent
  ],
  template: `
    <div class="products-container">
      <!-- Header -->
      <div class="page-header">
        <h1>Products</h1>
        <p>Browse our collection of 3D printing services and ready-made products</p>
      </div>

      <!-- Search and Filters -->
      <div class="search-section">
        <app-search
          placeholder="Search products..."
          [showFilters]="true"
          [filters]="searchFilters"
          (search)="onSearch($event)"
          (filterChange)="onFilterChange($event)">
        </app-search>
      </div>

      <!-- Main Content -->
      <div class="content-layout">
        <!-- Sidebar Filters -->
        <aside class="filters-sidebar">
          <mat-card>
            <mat-card-header>
              <mat-card-title>Filters</mat-card-title>
            </mat-card-header>
            <mat-card-content>
              <!-- Categories -->
              <div class="filter-group">
                <h3>Categories</h3>
                @if (loadingCategories) {
                  <mat-progress-spinner diameter="30"></mat-progress-spinner>
                } @else {
                  @for (category of categories; track category.id) {
                    <mat-checkbox
                      [checked]="filters.category_id === category.id"
                      (change)="onCategoryChange(category.id, $event.checked)">
                      {{ category.name }}
                    </mat-checkbox>
                  }
                }
              </div>

              <!-- Price Range -->
              <div class="filter-group">
                <h3>Price Range</h3>
                <div class="price-inputs">
                  <mat-form-field appearance="outline">
                    <mat-label>Min</mat-label>
                    <input matInput type="number" [(ngModel)]="filters.min_price" (ngModelChange)="applyFilters()">
                  </mat-form-field>
                  <span>-</span>
                  <mat-form-field appearance="outline">
                    <mat-label>Max</mat-label>
                    <input matInput type="number" [(ngModel)]="filters.max_price" (ngModelChange)="applyFilters()">
                  </mat-form-field>
                </div>
              </div>

              <!-- Product Type -->
              <div class="filter-group">
                <h3>Product Type</h3>
                <mat-radio-group [(ngModel)]="filters.product_type" (ngModelChange)="applyFilters()">
                  <mat-radio-button value="">All</mat-radio-button>
                  <mat-radio-button value="service">Custom Print Service</mat-radio-button>
                  <mat-radio-button value="ready_made">Ready-Made</mat-radio-button>
                </mat-radio-group>
              </div>

              <!-- Materials -->
              @if (materials.length > 0) {
                <div class="filter-group">
                  <h3>Materials</h3>
                  @for (material of materials; track material.id) {
                    <mat-checkbox
                      [checked]="filters.material_id === material.id"
                      (change)="onMaterialChange(material.id, $event.checked)">
                      {{ material.name }}
                    </mat-checkbox>
                  }
                </div>
              }

              <!-- Clear Filters -->
              <button mat-raised-button color="warn" (click)="clearFilters()" class="clear-filters-btn">
                Clear All Filters
              </button>
            </mat-card-content>
          </mat-card>
        </aside>

        <!-- Products Grid -->
        <main class="products-main">
          <!-- Sort Options -->
          <div class="toolbar">
            <span class="results-count">
              @if (totalProducts > 0) {
                Showing {{ products.length }} of {{ totalProducts }} products
              }
            </span>
            
            <mat-form-field appearance="outline" class="sort-field">
              <mat-label>Sort By</mat-label>
              <mat-select [(ngModel)]="sortOption" (ngModelChange)="onSortChange()">
                <mat-option value="name_asc">Name (A-Z)</mat-option>
                <mat-option value="name_desc">Name (Z-A)</mat-option>
                <mat-option value="price_asc">Price (Low to High)</mat-option>
                <mat-option value="price_desc">Price (High to Low)</mat-option>
                <mat-option value="rating_desc">Highest Rated</mat-option>
              </mat-select>
            </mat-form-field>

            <mat-button-toggle-group [value]="viewMode" (change)="viewMode = $event.value">
              <mat-button-toggle value="grid">
                <mat-icon>grid_view</mat-icon>
              </mat-button-toggle>
              <mat-button-toggle value="list">
                <mat-icon>view_list</mat-icon>
              </mat-button-toggle>
            </mat-button-toggle-group>
          </div>

          <!-- Loading State -->
          @if (loading) {
            <app-loading type="skeleton"></app-loading>
          }

          <!-- Error State -->
          @else if (error) {
            <app-error [message]="error" (retry)="loadProducts()"></app-error>
          }

          <!-- Empty State -->
          @else if (products.length === 0) {
            <div class="empty-state">
              <mat-icon>inventory_2</mat-icon>
              <h2>No products found</h2>
              <p>Try adjusting your filters or search criteria</p>
              <button mat-raised-button color="primary" (click)="clearFilters()">
                Clear Filters
              </button>
            </div>
          }

          <!-- Products Grid/List -->
          @else {
            <div [class]="'products-' + viewMode">
              @for (product of products; track product.id) {
                <mat-card class="product-card" [class.list-view]="viewMode === 'list'">
                  <img 
                    mat-card-image 
                    [src]="product.image_url || 'assets/placeholder-product.png'" 
                    [alt]="product.name"
                    [routerLink]="['/products', product.id]">
                  
                  <mat-card-content>
                    <h3 class="product-name" [routerLink]="['/products', product.id]">
                      {{ product.name }}
                    </h3>
                    
                    @if (product.category) {
                      <span class="product-category">{{ product.category.name }}</span>
                    }
                    
                    @if (product.description) {
                      <p class="product-description">{{ product.description }}</p>
                    }
                    
                    <div class="product-meta">
                      <span class="product-price">{{ product.base_price }} {{ product.currency }}</span>
                      
                      @if (product.rating) {
                        <div class="product-rating">
                          <mat-icon>star</mat-icon>
                          <span>{{ product.rating }}</span>
                          @if (product.reviews_count) {
                            <span class="reviews-count">({{ product.reviews_count }})</span>
                          }
                        </div>
                      }
                    </div>

                    @if (product.product_type) {
                      <mat-chip-set>
                        <mat-chip [color]="product.product_type === 'service' ? 'primary' : 'accent'">
                          {{ product.product_type === 'service' ? 'Custom Print' : 'Ready-Made' }}
                        </mat-chip>
                      </mat-chip-set>
                    }
                  </mat-card-content>

                  <mat-card-actions>
                    <button mat-button color="primary" [routerLink]="['/products', product.id]">
                      <mat-icon>visibility</mat-icon>
                      View Details
                    </button>
                    <button mat-button (click)="addToCart(product, $event)">
                      <mat-icon>shopping_cart</mat-icon>
                      Add to Cart
                    </button>
                  </mat-card-actions>
                </mat-card>
              }
            </div>

            <!-- Pagination -->
            <app-pagination
              [totalItems]="totalProducts"
              [currentPage]="currentPage"
              [pageSize]="pageSize"
              (pageChange)="onPageChange($event)"
              (pageSizeChange)="onPageSizeChange($event)">
            </app-pagination>
          }
        </main>
      </div>
    </div>
  `,
  styles: [`
    .products-container {
      max-width: 1400px;
      margin: 0 auto;
      padding: 2rem 1rem;
    }

    .page-header {
      text-align: center;
      margin-bottom: 2rem;
      
      h1 {
        font-size: 2.5rem;
        margin: 0 0 0.5rem;
      }
      
      p {
        color: #666;
        font-size: 1.125rem;
      }
    }

    .search-section {
      margin-bottom: 2rem;
    }

    .content-layout {
      display: grid;
      grid-template-columns: 280px 1fr;
      gap: 2rem;
      
      @media (max-width: 968px) {
        grid-template-columns: 1fr;
      }
    }

    .filters-sidebar {
      @media (max-width: 968px) {
        display: none;
      }
      
      .filter-group {
        margin-bottom: 1.5rem;
        
        h3 {
          font-size: 1rem;
          margin: 0 0 0.5rem;
          font-weight: 600;
        }
        
        mat-checkbox,
        mat-radio-button {
          display: block;
          margin-bottom: 0.5rem;
        }
      }

      .price-inputs {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        
        mat-form-field {
          flex: 1;
        }
      }

      .clear-filters-btn {
        width: 100%;
        margin-top: 1rem;
      }
    }

    .toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
      flex-wrap: wrap;
      gap: 1rem;
      
      .results-count {
        color: #666;
      }
      
      .sort-field {
        min-width: 200px;
      }
    }

    .products-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 1.5rem;
    }

    .products-list {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .product-card {
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
      display: flex;
      flex-direction: column;
      
      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
      }
      
      &.list-view {
        flex-direction: row;
        
        img {
          width: 200px;
          height: 200px;
          object-fit: cover;
        }
        
        mat-card-content {
          flex: 1;
        }
      }
      
      img {
        height: 220px;
        object-fit: cover;
        cursor: pointer;
      }
    }

    .product-name {
      margin: 0 0 0.5rem;
      font-size: 1.125rem;
      font-weight: 600;
      cursor: pointer;
      
      &:hover {
        color: #3f51b5;
      }
    }

    .product-category {
      display: inline-block;
      font-size: 0.75rem;
      color: #666;
      background: #f0f0f0;
      padding: 0.25rem 0.5rem;
      border-radius: 4px;
      margin-bottom: 0.5rem;
    }

    .product-description {
      color: #666;
      font-size: 0.875rem;
      margin: 0.5rem 0 1rem;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .product-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }

    .product-price {
      font-size: 1.25rem;
      font-weight: 600;
      color: #3f51b5;
    }

    .product-rating {
      display: flex;
      align-items: center;
      gap: 0.25rem;
      
      mat-icon {
        font-size: 18px;
        width: 18px;
        height: 18px;
        color: #ffa000;
      }
      
      .reviews-count {
        font-size: 0.875rem;
        color: #666;
        margin-left: 0.25rem;
      }
    }

    .empty-state {
      text-align: center;
      padding: 4rem 2rem;
      
      mat-icon {
        font-size: 80px;
        width: 80px;
        height: 80px;
        color: #ccc;
        margin-bottom: 1rem;
      }
      
      h2 {
        margin: 0 0 0.5rem;
        color: #666;
      }
      
      p {
        color: #999;
        margin-bottom: 1.5rem;
      }
    }

    mat-card-actions {
      display: flex;
      gap: 0.5rem;
      padding: 0.5rem 1rem;
      
      button {
        flex: 1;
        
        mat-icon {
          margin-right: 0.25rem;
          font-size: 18px;
          width: 18px;
          height: 18px;
        }
      }
    }
  `]
})
export class ProductsComponent implements OnInit, OnDestroy {
  products: Product[] = [];
  categories: Category[] = [];
  materials: Material[] = [];
  
  loading = false;
  loadingCategories = false;
  error: string | null = null;
  
  totalProducts = 0;
  currentPage = 1;
  pageSize = 20;
  
  filters: ProductFilter = {};
  sortOption = 'name_asc';
  viewMode: 'grid' | 'list' = 'grid';
  
  searchFilters: SearchFilter[] = [
    { field: 'category', label: 'Category', type: 'select', options: [] },
    { field: 'min_price', label: 'Min Price', type: 'number' },
    { field: 'max_price', label: 'Max Price', type: 'number' }
  ];
  
  private destroy$ = new Subject<void>();

  constructor(
    private productService: ProductService,
    private cartService: CartService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadCategories();
    this.loadMaterials();
    
    // Load query params
    this.route.queryParams.pipe(takeUntil(this.destroy$)).subscribe(params => {
      if (params['category']) {
        this.filters.category_id = params['category'];
      }
      if (params['search']) {
        this.filters.search = params['search'];
      }
      this.loadProducts();
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadProducts(): void {
    this.loading = true;
    this.error = null;

    const [sortField, sortOrder] = this.sortOption.split('_');
    
    this.productService.getProducts({
      ...this.filters,
      page: this.currentPage,
      limit: this.pageSize,
      sort: sortField,
      order: sortOrder as 'asc' | 'desc'
    }).subscribe({
      next: (response) => {
        this.products = response.data;
        this.totalProducts = response.meta.total;
        this.loading = false;
      },
      error: (error) => {
        this.error = error.message;
        this.loading = false;
      }
    });
  }

  loadCategories(): void {
    this.loadingCategories = true;
    this.productService.getCategories().subscribe({
      next: (categories) => {
        this.categories = categories;
        this.searchFilters[0].options = categories.map(cat => ({
          value: cat.id,
          label: cat.name
        }));
        this.loadingCategories = false;
      },
      error: () => {
        this.loadingCategories = false;
      }
    });
  }

  loadMaterials(): void {
    this.productService.getMaterials().subscribe({
      next: (materials) => {
        this.materials = materials;
      }
    });
  }

  onSearch(query: string): void {
    this.filters.search = query;
    this.currentPage = 1;
    this.loadProducts();
  }

  onFilterChange(filterValues: any): void {
    this.filters = { ...this.filters, ...filterValues };
    this.currentPage = 1;
    this.loadProducts();
  }

  onCategoryChange(categoryId: string, checked: boolean): void {
    this.filters.category_id = checked ? categoryId : undefined;
    this.currentPage = 1;
    this.loadProducts();
  }

  onMaterialChange(materialId: string, checked: boolean): void {
    this.filters.material_id = checked ? materialId : undefined;
    this.currentPage = 1;
    this.loadProducts();
  }

  onSortChange(): void {
    this.loadProducts();
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadProducts();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  onPageSizeChange(size: number): void {
    this.pageSize = size;
    this.currentPage = 1;
    this.loadProducts();
  }

  applyFilters(): void {
    this.currentPage = 1;
    this.loadProducts();
  }

  clearFilters(): void {
    this.filters = {};
    this.currentPage = 1;
    this.router.navigate([], { queryParams: {} });
    this.loadProducts();
  }

  addToCart(product: Product, event: Event): void {
    event.stopPropagation();
    
    this.cartService.addToCart({
      item_type: 'product',
      product_id: product.id,
      quantity: 1
    }).subscribe({
      next: () => {
        // Show success message
        console.log('Product added to cart');
      },
      error: (error) => {
        console.error('Failed to add to cart:', error);
      }
    });
  }
}

