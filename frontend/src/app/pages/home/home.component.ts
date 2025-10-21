import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MaterialModule } from '../../shared/material.module';
import { LoadingComponent } from '../../shared/components/loading/loading.component';
import { ErrorComponent } from '../../shared/components/error/error.component';
import { ProductService } from '../../services/product.service';
import { Product, Category } from '../../models/product.model';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MaterialModule,
    LoadingComponent,
    ErrorComponent
  ],
  template: `
    <div class="home-container">
      <!-- Hero Section -->
      <section class="hero-section">
        <div class="hero-content">
          <h1 class="hero-title">Welcome to 3D Store</h1>
          <p class="hero-subtitle">
            Professional 3D Printing Services & Ready-Made Products
          </p>
          <div class="hero-actions">
            <button mat-raised-button color="primary" routerLink="/products">
              Browse Products
            </button>
            <button mat-raised-button routerLink="/print-jobs">
              Upload 3D Model
            </button>
          </div>
        </div>
        <div class="hero-image">
          <mat-icon class="hero-icon">print</mat-icon>
        </div>
      </section>

      <!-- Features Section -->
      <section class="features-section">
        <h2>Why Choose Us</h2>
        <div class="features-grid">
          <mat-card class="feature-card">
            <mat-icon color="primary">settings</mat-icon>
            <h3>Custom 3D Printing</h3>
            <p>Upload your 3D models and get professional prints with multiple material options</p>
          </mat-card>
          
          <mat-card class="feature-card">
            <mat-icon color="primary">inventory_2</mat-icon>
            <h3>Ready-Made Products</h3>
            <p>Browse our collection of pre-printed products ready for immediate delivery</p>
          </mat-card>
          
          <mat-card class="feature-card">
            <mat-icon color="primary">speed</mat-icon>
            <h3>Fast Turnaround</h3>
            <p>Quick production times with real-time tracking of your print jobs</p>
          </mat-card>
          
          <mat-card class="feature-card">
            <mat-icon color="primary">verified</mat-icon>
            <h3>Quality Guaranteed</h3>
            <p>High-quality prints with multiple quality options to suit your needs</p>
          </mat-card>
        </div>
      </section>

      <!-- Featured Categories -->
      <section class="categories-section">
        <h2>Browse Categories</h2>
        
        @if (loadingCategories) {
          <app-loading type="skeleton"></app-loading>
        } @else if (categoriesError) {
          <app-error [message]="categoriesError" (retry)="loadCategories()"></app-error>
        } @else {
          <div class="categories-grid">
            @for (category of categories; track category.id) {
              <mat-card class="category-card" [routerLink]="['/products']" [queryParams]="{category: category.id}">
                <mat-card-content>
                  <mat-icon>category</mat-icon>
                  <h3>{{ category.name }}</h3>
                  @if (category.product_count) {
                    <p class="product-count">{{ category.product_count }} products</p>
                  }
                </mat-card-content>
              </mat-card>
            }
          </div>
        }
      </section>

      <!-- Featured Products -->
      <section class="featured-products-section">
        <div class="section-header">
          <h2>Featured Products</h2>
          <button mat-button routerLink="/products">View All</button>
        </div>
        
        @if (loadingProducts) {
          <app-loading type="skeleton"></app-loading>
        } @else if (productsError) {
          <app-error [message]="productsError" (retry)="loadFeaturedProducts()"></app-error>
        } @else {
          <div class="products-grid">
            @for (product of featuredProducts; track product.id) {
              <mat-card class="product-card" [routerLink]="['/products', product.id]">
                <img 
                  mat-card-image 
                  [src]="product.image_url || 'assets/placeholder-product.png'" 
                  [alt]="product.name">
                <mat-card-content>
                  <h3 class="product-name">{{ product.name }}</h3>
                  @if (product.description) {
                    <p class="product-description">{{ product.description }}</p>
                  }
                  <div class="product-footer">
                    <span class="product-price">{{ product.base_price }} {{ product.currency }}</span>
                    @if (product.rating) {
                      <div class="product-rating">
                        <mat-icon>star</mat-icon>
                        <span>{{ product.rating }}</span>
                      </div>
                    }
                  </div>
                </mat-card-content>
                <mat-card-actions>
                  <button mat-button color="primary">View Details</button>
                </mat-card-actions>
              </mat-card>
            }
          </div>
        }
      </section>

      <!-- Call to Action -->
      <section class="cta-section">
        <h2>Ready to Start Your Project?</h2>
        <p>Upload your 3D model or browse our ready-made products</p>
        <div class="cta-actions">
          <button mat-raised-button color="primary" routerLink="/print-jobs">
            <mat-icon>upload</mat-icon>
            Upload 3D Model
          </button>
          <button mat-raised-button color="accent" routerLink="/products">
            <mat-icon>shopping_cart</mat-icon>
            Browse Products
          </button>
        </div>
      </section>
    </div>
  `,
  styles: [`
    .home-container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem 1rem;
    }

    .hero-section {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 2rem;
      align-items: center;
      padding: 4rem 0;
      
      @media (max-width: 768px) {
        grid-template-columns: 1fr;
        text-align: center;
      }
    }

    .hero-title {
      font-size: 3rem;
      margin: 0 0 1rem;
      color: #333;
      
      @media (max-width: 768px) {
        font-size: 2rem;
      }
    }

    .hero-subtitle {
      font-size: 1.25rem;
      color: #666;
      margin-bottom: 2rem;
    }

    .hero-actions {
      display: flex;
      gap: 1rem;
      
      @media (max-width: 768px) {
        justify-content: center;
      }
    }

    .hero-image {
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .hero-icon {
      font-size: 200px;
      width: 200px;
      height: 200px;
      color: #3f51b5;
    }

    .features-section,
    .categories-section,
    .featured-products-section {
      padding: 4rem 0;
    }

    .features-section h2,
    .categories-section h2,
    .featured-products-section h2 {
      text-align: center;
      margin-bottom: 2rem;
      font-size: 2rem;
    }

    .features-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 2rem;
    }

    .feature-card {
      text-align: center;
      padding: 2rem;
      
      mat-icon {
        font-size: 48px;
        width: 48px;
        height: 48px;
        margin-bottom: 1rem;
      }
      
      h3 {
        margin: 1rem 0;
      }
      
      p {
        color: #666;
      }
    }

    .categories-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 1rem;
    }

    .category-card {
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
      
      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
      }
      
      mat-card-content {
        text-align: center;
        padding: 2rem;
        
        mat-icon {
          font-size: 48px;
          width: 48px;
          height: 48px;
          margin-bottom: 1rem;
        }
        
        h3 {
          margin: 0.5rem 0;
        }
        
        .product-count {
          color: #666;
          font-size: 0.875rem;
        }
      }
    }

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
    }

    .products-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 2rem;
    }

    .product-card {
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
      
      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
      }
      
      img {
        height: 200px;
        object-fit: cover;
      }
    }

    .product-name {
      margin: 0 0 0.5rem;
      font-size: 1.125rem;
    }

    .product-description {
      color: #666;
      font-size: 0.875rem;
      margin: 0 0 1rem;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .product-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
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
    }

    .cta-section {
      text-align: center;
      padding: 4rem 2rem;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 8px;
      color: white;
      
      h2 {
        font-size: 2rem;
        margin: 0 0 1rem;
      }
      
      p {
        font-size: 1.125rem;
        margin-bottom: 2rem;
      }
    }

    .cta-actions {
      display: flex;
      gap: 1rem;
      justify-content: center;
      
      button {
        mat-icon {
          margin-right: 0.5rem;
        }
      }
    }
  `]
})
export class HomeComponent implements OnInit {
  featuredProducts: Product[] = [];
  categories: Category[] = [];
  loadingProducts = false;
  loadingCategories = false;
  productsError: string | null = null;
  categoriesError: string | null = null;

  constructor(private productService: ProductService) {}

  ngOnInit(): void {
    this.loadFeaturedProducts();
    this.loadCategories();
  }

  loadFeaturedProducts(): void {
    this.loadingProducts = true;
    this.productsError = null;

    this.productService.getFeaturedProducts(6).subscribe({
      next: (products) => {
        this.featuredProducts = products;
        this.loadingProducts = false;
      },
      error: (error) => {
        this.productsError = error.message;
        this.loadingProducts = false;
      }
    });
  }

  loadCategories(): void {
    this.loadingCategories = true;
    this.categoriesError = null;

    this.productService.getFeaturedCategories().subscribe({
      next: (categories) => {
        this.categories = categories;
        this.loadingCategories = false;
      },
      error: (error) => {
        this.categoriesError = error.message;
        this.loadingCategories = false;
      }
    });
  }
}

