import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MaterialModule } from '../../shared/material.module';
import { Product } from '../../models/product.model';

@Component({
  selector: 'app-product-card',
  standalone: true,
  imports: [CommonModule, RouterModule, MaterialModule],
  template: `
    <mat-card class="product-card" [class.list-view]="layout === 'list'">
      <!-- Product Image -->
      <div class="image-container" [routerLink]="['/products', product.id]">
        @if (product.image_url) {
          <img 
            mat-card-image 
            [src]="product.image_url" 
            [alt]="product.name"
            class="product-image">
        } @else {
          <div class="placeholder-image">
            <mat-icon>inventory_2</mat-icon>
          </div>
        }
        
        <!-- Badge Overlays -->
        <div class="image-badges">
          @if (product.is_featured) {
            <mat-chip color="warn" class="featured-badge">
              <mat-icon>star</mat-icon>
              Featured
            </mat-chip>
          }
          
          @if (product.stock_quantity !== undefined && product.stock_quantity === 0) {
            <mat-chip color="warn" class="stock-badge">
              Out of Stock
            </mat-chip>
          }
        </div>

        <!-- Favorite Button -->
        <button 
          mat-icon-button 
          class="favorite-btn"
          (click)="onToggleFavorite($event)"
          [class.is-favorite]="isFavorite">
          <mat-icon>{{ isFavorite ? 'favorite' : 'favorite_border' }}</mat-icon>
        </button>
      </div>

      <!-- Product Content -->
      <mat-card-content>
        <!-- Category -->
        @if (product.category) {
          <span class="product-category">{{ product.category.name }}</span>
        }

        <!-- Product Name -->
        <h3 class="product-name" [routerLink]="['/products', product.id]">
          {{ product.name }}
        </h3>

        <!-- Description -->
        @if (product.description && layout === 'list') {
          <p class="product-description">{{ product.description }}</p>
        }

        <!-- Rating -->
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
              <span class="reviews-count">({{ product.reviews_count }})</span>
            }
          </div>
        }

        <!-- Price and Type -->
        <div class="product-footer">
          <div class="price-section">
            <span class="product-price">{{ product.base_price }} {{ product.currency }}</span>
            @if (product.product_type) {
              <mat-chip [color]="product.product_type === 'service' ? 'primary' : 'accent'" class="type-chip">
                {{ product.product_type === 'service' ? 'Custom' : 'Ready' }}
              </mat-chip>
            }
          </div>
        </div>
      </mat-card-content>

      <!-- Actions -->
      @if (showActions) {
        <mat-card-actions>
          <button 
            mat-button 
            color="primary"
            [routerLink]="['/products', product.id]">
            <mat-icon>visibility</mat-icon>
            View
          </button>
          
          @if (product.stock_quantity === undefined || product.stock_quantity > 0) {
            <button 
              mat-button
              (click)="onAddToCart($event)"
              class="add-to-cart-btn">
              <mat-icon class="cart-icon">shopping_cart</mat-icon>
              Add to Cart
            </button>
          }
          
          <button 
            mat-icon-button 
            (click)="onQuickView($event)"
            matTooltip="Quick View">
            <mat-icon>open_in_new</mat-icon>
          </button>
        </mat-card-actions>
      }
    </mat-card>
  `,
  styles: [`
    .product-card {
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      position: relative;
      overflow: hidden;
      
      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        
        .product-image {
          transform: scale(1.05);
        }
        
        .favorite-btn {
          opacity: 1;
        }
        
        .add-to-cart-btn {
          background: #3f51b5;
          color: white;
          
          .cart-icon {
            animation: cartBounce 0.5s ease;
          }
        }
      }
      
      &.list-view {
        display: flex;
        
        .image-container {
          width: 200px;
          flex-shrink: 0;
        }
        
        mat-card-content {
          flex: 1;
        }
      }
    }

    .image-container {
      position: relative;
      overflow: hidden;
      aspect-ratio: 1;
      background: #f5f5f5;
      
      .product-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.3s;
      }
      
      .placeholder-image {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        
        mat-icon {
          font-size: 64px;
          width: 64px;
          height: 64px;
          color: #ccc;
        }
      }
      
      .image-badges {
        position: absolute;
        top: 0.5rem;
        left: 0.5rem;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        
        .featured-badge,
        .stock-badge {
          mat-icon {
            font-size: 14px;
            width: 14px;
            height: 14px;
            margin-right: 0.25rem;
          }
        }
      }
      
      .favorite-btn {
        position: absolute;
        top: 0.5rem;
        right: 0.5rem;
        background: white;
        opacity: 0;
        transition: opacity 0.3s;
        
        &.is-favorite {
          opacity: 1;
          
          mat-icon {
            color: #f44336;
            animation: heartBeat 0.3s ease;
          }
        }
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

    .product-name {
      margin: 0.5rem 0;
      font-size: 1.125rem;
      font-weight: 600;
      cursor: pointer;
      transition: color 0.2s;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      
      &:hover {
        color: #3f51b5;
      }
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

    .product-rating {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 1rem;
      
      .stars {
        display: flex;
        gap: 2px;
        
        mat-icon {
          font-size: 16px;
          width: 16px;
          height: 16px;
          color: #e0e0e0;
          
          &.filled {
            color: #ffa000;
          }
        }
      }
      
      .rating-value {
        font-weight: 600;
        font-size: 0.875rem;
      }
      
      .reviews-count {
        font-size: 0.75rem;
        color: #666;
      }
    }

    .product-footer {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      
      .price-section {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      
      .product-price {
        font-size: 1.25rem;
        font-weight: 700;
        color: #3f51b5;
      }
      
      .type-chip {
        height: 24px;
        font-size: 0.75rem;
      }
    }

    mat-card-actions {
      display: flex;
      gap: 0.5rem;
      padding: 0.75rem 1rem;
      
      button {
        flex: 1;
        
        mat-icon {
          font-size: 18px;
          width: 18px;
          height: 18px;
          margin-right: 0.25rem;
        }
      }
      
      .add-to-cart-btn {
        transition: all 0.3s;
      }
    }

    @keyframes heartBeat {
      0%, 100% { transform: scale(1); }
      25% { transform: scale(1.3); }
      50% { transform: scale(1.1); }
      75% { transform: scale(1.25); }
    }

    @keyframes cartBounce {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-4px); }
    }
  `]
})
export class ProductCardComponent {
  @Input() product!: Product;
  @Input() showActions: boolean = true;
  @Input() layout: 'grid' | 'list' = 'grid';
  @Input() isFavorite: boolean = false;
  
  @Output() addToCart = new EventEmitter<Product>();
  @Output() addToFavorites = new EventEmitter<Product>();
  @Output() quickView = new EventEmitter<Product>();

  onAddToCart(event: Event): void {
    event.stopPropagation();
    event.preventDefault();
    this.addToCart.emit(this.product);
  }

  onToggleFavorite(event: Event): void {
    event.stopPropagation();
    event.preventDefault();
    this.addToFavorites.emit(this.product);
  }

  onQuickView(event: Event): void {
    event.stopPropagation();
    event.preventDefault();
    this.quickView.emit(this.product);
  }
}

