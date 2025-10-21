import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { MaterialModule } from '../../shared/material.module';
import { LoadingComponent } from '../../shared/components/loading/loading.component';
import { ErrorComponent } from '../../shared/components/error/error.component';
import { ProductService } from '../../services/product.service';
import { CartService } from '../../services/cart.service';
import { Product, ProductReview, Material } from '../../models/product.model';

@Component({
  selector: 'app-product-detail',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
    MaterialModule,
    LoadingComponent,
    ErrorComponent
  ],
  template: `
    <div class="product-detail-container">
      @if (loading) {
        <app-loading type="skeleton"></app-loading>
      } @else if (error) {
        <app-error [message]="error" (retry)="loadProduct()"></app-error>
      } @else if (product) {
        <!-- Breadcrumb -->
        <nav class="breadcrumb">
          <a routerLink="/">Home</a>
          <mat-icon>chevron_right</mat-icon>
          <a routerLink="/products">Products</a>
          <mat-icon>chevron_right</mat-icon>
          @if (product.category) {
            <a [routerLink]="['/products']" [queryParams]="{category: product.category.id}">
              {{ product.category.name }}
            </a>
            <mat-icon>chevron_right</mat-icon>
          }
          <span>{{ product.name }}</span>
        </nav>

        <div class="product-content">
          <!-- Product Images / 3D Preview -->
          <div class="product-media">
            @if (product.model_url) {
              <div class="model-preview">
                <!-- 3D Model Preview will be integrated here -->
                <div class="preview-placeholder">
                  <mat-icon>view_in_ar</mat-icon>
                  <p>3D Model Preview</p>
                  <p class="preview-note">Click and drag to rotate</p>
                </div>
              </div>
            } @else if (product.image_url) {
              <img [src]="product.image_url" [alt]="product.name" class="product-image">
            }
            
            @if (product.images && product.images.length > 1) {
              <div class="image-thumbnails">
                @for (image of product.images; track image) {
                  <img 
                    [src]="image" 
                    [alt]="product.name"
                    class="thumbnail"
                    [class.active]="selectedImage === image"
                    (click)="selectedImage = image">
                }
              </div>
            }
          </div>

          <!-- Product Information -->
          <div class="product-info">
            <h1 class="product-title">{{ product.name }}</h1>
            
            @if (product.rating) {
              <div class="product-rating">
                <div class="stars">
                  @for (star of [1,2,3,4,5]; track star) {
                    <mat-icon [class.filled]="star <= (product.rating || 0)">
                      {{ star <= (product.rating || 0) ? 'star' : 'star_border' }}
                    </mat-icon>
                  }
                </div>
                <span class="rating-value">{{ product.rating }}</span>
                @if (product.reviews_count) {
                  <span class="reviews-count">({{ product.reviews_count }} reviews)</span>
                }
              </div>
            }

            <div class="product-price">
              <span class="price-value">{{ product.base_price }} {{ product.currency }}</span>
              @if (product.product_type === 'service') {
                <span class="price-note">Base price - final cost depends on options</span>
              }
            </div>

            @if (product.description) {
              <div class="product-description">
                <h3>Description</h3>
                <p>{{ product.description }}</p>
              </div>
            }

            <!-- Product Type Badge -->
            <mat-chip-set class="product-tags">
              <mat-chip [color]="product.product_type === 'service' ? 'primary' : 'accent'">
                {{ product.product_type === 'service' ? 'Custom Print Service' : 'Ready-Made Product' }}
              </mat-chip>
              @if (product.is_featured) {
                <mat-chip color="warn">Featured</mat-chip>
              }
            </mat-chip-set>

            <!-- Material Selection (for custom prints) -->
            @if (product.product_type === 'service' && materials.length > 0) {
              <div class="option-group">
                <h3>Select Material</h3>
                <mat-form-field appearance="outline">
                  <mat-label>Material</mat-label>
                  <mat-select [(ngModel)]="selectedMaterial">
                    @for (material of materials; track material.id) {
                      <mat-option [value]="material.id">
                        {{ material.name }} - {{ material.type }}
                      </mat-option>
                    }
                  </mat-select>
                </mat-form-field>
              </div>
            }

            <!-- Quantity -->
            <div class="option-group">
              <h3>Quantity</h3>
              <div class="quantity-selector">
                <button mat-icon-button (click)="decreaseQuantity()" [disabled]="quantity <= 1">
                  <mat-icon>remove</mat-icon>
                </button>
                <input type="number" [(ngModel)]="quantity" min="1" max="100">
                <button mat-icon-button (click)="increaseQuantity()" [disabled]="quantity >= 100">
                  <mat-icon>add</mat-icon>
                </button>
              </div>
            </div>

            <!-- Stock Status -->
            @if (product.stock_quantity !== undefined) {
              <div class="stock-status">
                @if (product.stock_quantity > 0) {
                  <mat-icon color="accent">check_circle</mat-icon>
                  <span class="in-stock">In Stock ({{ product.stock_quantity }} available)</span>
                } @else {
                  <mat-icon color="warn">cancel</mat-icon>
                  <span class="out-of-stock">Out of Stock</span>
                }
              </div>
            }

            <!-- Actions -->
            <div class="product-actions">
              <button 
                mat-raised-button 
                color="primary" 
                class="add-to-cart-btn"
                [disabled]="addingToCart || (product.stock_quantity !== undefined && product.stock_quantity === 0)"
                (click)="addToCart()">
                <mat-icon>shopping_cart</mat-icon>
                {{ addingToCart ? 'Adding...' : 'Add to Cart' }}
              </button>
              
              <button mat-raised-button (click)="buyNow()" [disabled]="product.stock_quantity === 0">
                <mat-icon>flash_on</mat-icon>
                Buy Now
              </button>
              
              <button mat-icon-button (click)="toggleFavorite()" matTooltip="Add to Favorites">
                <mat-icon [color]="isFavorite ? 'warn' : ''">
                  {{ isFavorite ? 'favorite' : 'favorite_border' }}
                </mat-icon>
              </button>
            </div>

            <!-- Additional Information -->
            <mat-accordion class="info-accordion">
              @if (product.product_type === 'service') {
                <mat-expansion-panel>
                  <mat-expansion-panel-header>
                    <mat-panel-title>
                      <mat-icon>settings</mat-icon>
                      Print Settings
                    </mat-panel-title>
                  </mat-expansion-panel-header>
                  <div class="panel-content">
                    <p><strong>Quality Options:</strong> Draft, Standard, High, Ultra</p>
                    <p><strong>Supported Formats:</strong> STL, OBJ, 3MF</p>
                    <p><strong>Max File Size:</strong> 100MB</p>
                  </div>
                </mat-expansion-panel>
              }

              <mat-expansion-panel>
                <mat-expansion-panel-header>
                  <mat-panel-title>
                    <mat-icon>local_shipping</mat-icon>
                    Shipping Information
                  </mat-panel-title>
                </mat-expansion-panel-header>
                <div class="panel-content">
                  <p>Free shipping on orders over $50</p>
                  <p>Estimated delivery: 3-5 business days</p>
                </div>
              </mat-expansion-panel>

              <mat-expansion-panel>
                <mat-expansion-panel-header>
                  <mat-panel-title>
                    <mat-icon>sync</mat-icon>
                    Returns & Refunds
                  </mat-panel-title>
                </mat-expansion-panel-header>
                <div class="panel-content">
                  <p>30-day return policy</p>
                  <p>Full refund for defective products</p>
                </div>
              </mat-expansion-panel>
            </mat-accordion>
          </div>
        </div>

        <!-- Reviews Section -->
        <section class="reviews-section">
          <h2>Customer Reviews</h2>
          
          @if (loadingReviews) {
            <app-loading type="spinner"></app-loading>
          } @else if (reviews.length > 0) {
            <div class="reviews-list">
              @for (review of reviews; track review.id) {
                <mat-card class="review-card">
                  <mat-card-header>
                    <mat-card-title>
                      <div class="review-header">
                        <span class="reviewer-name">{{ review.user_name || 'Anonymous' }}</span>
                        <div class="review-rating">
                          @for (star of [1,2,3,4,5]; track star) {
                            <mat-icon [class.filled]="star <= review.rating">
                              {{ star <= review.rating ? 'star' : 'star_border' }}
                            </mat-icon>
                          }
                        </div>
                      </div>
                    </mat-card-title>
                    <mat-card-subtitle>
                      {{ review.create_date | date:'mediumDate' }}
                    </mat-card-subtitle>
                  </mat-card-header>
                  <mat-card-content>
                    @if (review.comment) {
                      <p>{{ review.comment }}</p>
                    }
                  </mat-card-content>
                </mat-card>
              }
            </div>
          } @else {
            <div class="no-reviews">
              <p>No reviews yet. Be the first to review this product!</p>
            </div>
          }
        </section>
      }
    </div>
  `,
  styles: [`
    .product-detail-container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem 1rem;
    }

    .breadcrumb {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 2rem;
      font-size: 0.875rem;
      
      a {
        color: #3f51b5;
        text-decoration: none;
        
        &:hover {
          text-decoration: underline;
        }
      }
      
      mat-icon {
        font-size: 16px;
        width: 16px;
        height: 16px;
        color: #999;
      }
      
      span {
        color: #666;
      }
    }

    .product-content {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 3rem;
      margin-bottom: 3rem;
      
      @media (max-width: 968px) {
        grid-template-columns: 1fr;
      }
    }

    .product-media {
      .model-preview {
        width: 100%;
        height: 500px;
        background: #f5f5f5;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .preview-placeholder {
        text-align: center;
        
        mat-icon {
          font-size: 80px;
          width: 80px;
          height: 80px;
          color: #999;
        }
        
        p {
          color: #666;
          margin: 1rem 0 0;
        }
        
        .preview-note {
          font-size: 0.875rem;
          color: #999;
        }
      }
      
      .product-image {
        width: 100%;
        height: 500px;
        object-fit: cover;
        border-radius: 8px;
      }
      
      .image-thumbnails {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
        
        .thumbnail {
          width: 80px;
          height: 80px;
          object-fit: cover;
          border-radius: 4px;
          cursor: pointer;
          border: 2px solid transparent;
          
          &:hover,
          &.active {
            border-color: #3f51b5;
          }
        }
      }
    }

    .product-info {
      .product-title {
        font-size: 2rem;
        margin: 0 0 1rem;
      }
      
      .product-rating {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
        
        .stars {
          display: flex;
          
          mat-icon {
            font-size: 20px;
            width: 20px;
            height: 20px;
            color: #ffa000;
            
            &.filled {
              color: #ffa000;
            }
          }
        }
        
        .rating-value {
          font-weight: 600;
        }
        
        .reviews-count {
          color: #666;
          font-size: 0.875rem;
        }
      }
      
      .product-price {
        margin-bottom: 1.5rem;
        
        .price-value {
          font-size: 2rem;
          font-weight: 700;
          color: #3f51b5;
          display: block;
        }
        
        .price-note {
          font-size: 0.875rem;
          color: #666;
          display: block;
          margin-top: 0.25rem;
        }
      }
      
      .product-description {
        margin-bottom: 1.5rem;
        
        h3 {
          font-size: 1.125rem;
          margin: 0 0 0.5rem;
        }
        
        p {
          color: #666;
          line-height: 1.6;
        }
      }
      
      .product-tags {
        margin-bottom: 1.5rem;
      }
      
      .option-group {
        margin-bottom: 1.5rem;
        
        h3 {
          font-size: 1rem;
          margin: 0 0 0.5rem;
          font-weight: 600;
        }
        
        mat-form-field {
          width: 100%;
        }
      }
      
      .quantity-selector {
        display: flex;
        align-items: center;
        gap: 1rem;
        
        input {
          width: 80px;
          text-align: center;
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 1rem;
        }
      }
      
      .stock-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
        
        .in-stock {
          color: #4caf50;
        }
        
        .out-of-stock {
          color: #f44336;
        }
      }
      
      .product-actions {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
        
        .add-to-cart-btn {
          flex: 1;
        }
        
        button mat-icon {
          margin-right: 0.5rem;
        }
      }
      
      .info-accordion {
        .panel-content {
          padding: 1rem 0;
          
          p {
            margin: 0.5rem 0;
            color: #666;
          }
        }
        
        mat-icon {
          margin-right: 0.5rem;
        }
      }
    }

    .reviews-section {
      margin-top: 3rem;
      
      h2 {
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
      }
      
      .reviews-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
      }
      
      .review-card {
        .review-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          width: 100%;
          
          .reviewer-name {
            font-weight: 600;
          }
          
          .review-rating {
            display: flex;
            
            mat-icon {
              font-size: 16px;
              width: 16px;
              height: 16px;
              color: #ffa000;
            }
          }
        }
      }
      
      .no-reviews {
        text-align: center;
        padding: 2rem;
        color: #666;
      }
    }
  `]
})
export class ProductDetailComponent implements OnInit, OnDestroy {
  product: Product | null = null;
  reviews: ProductReview[] = [];
  materials: Material[] = [];
  
  loading = false;
  loadingReviews = false;
  error: string | null = null;
  
  selectedImage: string | null = null;
  selectedMaterial: string | null = null;
  quantity = 1;
  isFavorite = false;
  addingToCart = false;
  
  private destroy$ = new Subject<void>();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private productService: ProductService,
    private cartService: CartService
  ) {}

  ngOnInit(): void {
    this.route.params.pipe(takeUntil(this.destroy$)).subscribe(params => {
      const productId = params['id'];
      if (productId) {
        this.loadProduct(productId);
        this.loadReviews(productId);
      }
    });
    
    this.loadMaterials();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadProduct(id?: string): void {
    const productId = id || this.route.snapshot.params['id'];
    this.loading = true;
    this.error = null;

    this.productService.getProduct(productId).subscribe({
      next: (product) => {
        this.product = product;
        this.selectedImage = product.image_url || null;
        this.loading = false;
      },
      error: (error) => {
        this.error = error.message;
        this.loading = false;
      }
    });
  }

  loadReviews(productId: string): void {
    this.loadingReviews = true;
    
    this.productService.getProductReviews(productId, { page: 1, limit: 10 }).subscribe({
      next: (response) => {
        this.reviews = response.data;
        this.loadingReviews = false;
      },
      error: () => {
        this.loadingReviews = false;
      }
    });
  }

  loadMaterials(): void {
    this.productService.getMaterials().subscribe({
      next: (materials) => {
        this.materials = materials.filter(m => m.is_available);
        if (this.materials.length > 0) {
          this.selectedMaterial = this.materials[0].id;
        }
      }
    });
  }

  increaseQuantity(): void {
    if (this.quantity < 100) {
      this.quantity++;
    }
  }

  decreaseQuantity(): void {
    if (this.quantity > 1) {
      this.quantity--;
    }
  }

  addToCart(): void {
    if (!this.product) return;
    
    this.addingToCart = true;
    
    this.cartService.addToCart({
      item_type: 'product',
      product_id: this.product.id,
      quantity: this.quantity
    }).subscribe({
      next: () => {
        this.addingToCart = false;
        // Show success notification
        console.log('Product added to cart');
      },
      error: (error) => {
        this.addingToCart = false;
        console.error('Failed to add to cart:', error);
      }
    });
  }

  buyNow(): void {
    this.addToCart();
    // Navigate to cart after adding
    setTimeout(() => {
      this.router.navigate(['/cart']);
    }, 500);
  }

  toggleFavorite(): void {
    if (!this.product) return;
    
    if (this.isFavorite) {
      this.productService.removeFromFavorites(this.product.id).subscribe({
        next: () => {
          this.isFavorite = false;
        }
      });
    } else {
      this.productService.addToFavorites(this.product.id).subscribe({
        next: () => {
          this.isFavorite = true;
        }
      });
    }
  }
}

