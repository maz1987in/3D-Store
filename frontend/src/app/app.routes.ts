import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'products', pathMatch: 'full' },
  {
    path: 'products',
    loadComponent: () => import('./shared/components/product-card/product-card.component').then(m => m.ProductCardComponent)
  },
  {
    path: 'orders',
    canActivate: [authGuard],
    loadComponent: () => import('./shared/components/order-card/order-card.component').then(m => m.OrderCardComponent)
  },
  {
    path: 'upload',
    canActivate: [authGuard],
    loadComponent: () => import('./shared/components/file-upload/file-upload.component').then(m => m.FileUploadComponent)
  },
  {
    path: 'preview',
    canActivate: [authGuard],
    loadComponent: () => import('./shared/components/print-preview/print-preview.component').then(m => m.PrintPreviewComponent)
  }
];
