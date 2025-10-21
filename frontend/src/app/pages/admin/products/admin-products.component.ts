import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../../../shared/material.module';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';
import { PaginationComponent } from '../../../shared/components/pagination/pagination.component';
import { SearchComponent } from '../../../shared/components/search/search.component';
import { ProductService } from '../../../services/product.service';
import { Product } from '../../../models/product.model';

@Component({
  selector: 'app-admin-products',
  standalone: true,
  imports: [
    CommonModule,
    MaterialModule,
    LoadingComponent,
    PaginationComponent,
    SearchComponent
  ],
  template: `
    <div class="admin-products">
      <div class="page-header">
        <h1>Product Management</h1>
        <button mat-raised-button color="primary">
          <mat-icon>add</mat-icon>
          Add Product
        </button>
      </div>

      <app-search
        placeholder="Search products..."
        (search)="onSearch($event)">
      </app-search>

      @if (loading) {
        <app-loading type="skeleton"></app-loading>
      } @else {
        <div class="table-container">
          <table mat-table [dataSource]="products" class="products-table">
            <ng-container matColumnDef="image">
              <th mat-header-cell *matHeaderCellDef>Image</th>
              <td mat-cell *matCellDef="let product">
                @if (product.image_url) {
                  <img [src]="product.image_url" [alt]="product.name" class="product-thumbnail">
                } @else {
                  <div class="placeholder-thumbnail">
                    <mat-icon>image</mat-icon>
                  </div>
                }
              </td>
            </ng-container>

            <ng-container matColumnDef="name">
              <th mat-header-cell *matHeaderCellDef>Name</th>
              <td mat-cell *matCellDef="let product">{{ product.name }}</td>
            </ng-container>

            <ng-container matColumnDef="type">
              <th mat-header-cell *matHeaderCellDef>Type</th>
              <td mat-cell *matCellDef="let product">
                <mat-chip [color]="product.product_type === 'service' ? 'primary' : 'accent'">
                  {{ product.product_type }}
                </mat-chip>
              </td>
            </ng-container>

            <ng-container matColumnDef="price">
              <th mat-header-cell *matHeaderCellDef>Price</th>
              <td mat-cell *matCellDef="let product">
                {{ product.base_price }} {{ product.currency }}
              </td>
            </ng-container>

            <ng-container matColumnDef="status">
              <th mat-header-cell *matHeaderCellDef>Status</th>
              <td mat-cell *matCellDef="let product">
                <mat-chip [color]="product.is_active ? 'accent' : 'warn'">
                  {{ product.is_active ? 'Active' : 'Inactive' }}
                </mat-chip>
              </td>
            </ng-container>

            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef>Actions</th>
              <td mat-cell *matCellDef="let product">
                <button mat-icon-button [matMenuTriggerFor]="menu">
                  <mat-icon>more_vert</mat-icon>
                </button>
                <mat-menu #menu="matMenu">
                  <button mat-menu-item>
                    <mat-icon>edit</mat-icon>
                    Edit
                  </button>
                  <button mat-menu-item>
                    <mat-icon>visibility</mat-icon>
                    View
                  </button>
                  <button mat-menu-item>
                    <mat-icon>delete</mat-icon>
                    Delete
                  </button>
                </mat-menu>
              </td>
            </ng-container>

            <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
            <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
          </table>
        </div>

        <app-pagination
          [totalItems]="totalProducts"
          [currentPage]="currentPage"
          [pageSize]="pageSize"
          (pageChange)="onPageChange($event)">
        </app-pagination>
      }
    </div>
  `,
  styles: [`
    .admin-products {
      h1 {
        margin: 0;
      }
    }

    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
      
      button mat-icon {
        margin-right: 0.5rem;
      }
    }

    .table-container {
      background: white;
      border-radius: 8px;
      margin: 2rem 0;
      overflow: auto;
    }

    .products-table {
      width: 100%;
      
      .product-thumbnail {
        width: 50px;
        height: 50px;
        object-fit: cover;
        border-radius: 4px;
      }
      
      .placeholder-thumbnail {
        width: 50px;
        height: 50px;
        background: #f5f5f5;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        
        mat-icon {
          color: #999;
        }
      }
    }
  `]
})
export class AdminProductsComponent implements OnInit {
  products: Product[] = [];
  loading = false;
  totalProducts = 0;
  currentPage = 1;
  pageSize = 20;
  
  displayedColumns = ['image', 'name', 'type', 'price', 'status', 'actions'];

  constructor(private productService: ProductService) {}

  ngOnInit(): void {
    this.loadProducts();
  }

  loadProducts(): void {
    this.loading = true;
    
    this.productService.getProducts({ page: this.currentPage, limit: this.pageSize }).subscribe({
      next: (response) => {
        this.products = response.data;
        this.totalProducts = response.meta.total;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  onSearch(query: string): void {
    // Implement search
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadProducts();
  }
}

