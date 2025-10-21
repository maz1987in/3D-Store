import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';

export const routes: Routes = [
  // Public routes - will be implemented
  {
    path: '',
    loadComponent: () => import('./pages/home/home.component').then(m => m.HomeComponent)
  },
  {
    path: 'products',
    loadComponent: () => import('./pages/products/products.component').then(m => m.ProductsComponent)
  },
  {
    path: 'products/:id',
    loadComponent: () => import('./pages/product-detail/product-detail.component').then(m => m.ProductDetailComponent)
  },
  {
    path: 'login',
    loadComponent: () => import('./pages/auth/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'register',
    loadComponent: () => import('./pages/auth/register/register.component').then(m => m.RegisterComponent)
  },

  // Protected routes - Customer
  {
    path: 'cart',
    loadComponent: () => import('./pages/cart/cart.component').then(m => m.CartComponent),
    canActivate: [authGuard]
  },
  {
    path: 'checkout',
    loadComponent: () => import('./pages/checkout/checkout.component').then(m => m.CheckoutComponent),
    canActivate: [authGuard]
  },
  {
    path: 'orders',
    loadComponent: () => import('./pages/orders/orders.component').then(m => m.OrdersComponent),
    canActivate: [authGuard]
  },
  {
    path: 'orders/:id',
    loadComponent: () => import('./pages/order-detail/order-detail.component').then(m => m.OrderDetailComponent),
    canActivate: [authGuard]
  },
  {
    path: 'print-jobs',
    loadComponent: () => import('./pages/print-jobs/print-jobs.component').then(m => m.PrintJobsComponent),
    canActivate: [authGuard]
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [authGuard]
  },
  {
    path: 'profile',
    loadComponent: () => import('./pages/profile/profile.component').then(m => m.ProfileComponent),
    canActivate: [authGuard]
  },

  // Admin routes
  {
    path: 'admin',
    loadComponent: () => import('./pages/admin/admin.component').then(m => m.AdminComponent),
    canActivate: [authGuard, roleGuard],
    data: { role: 'admin' },
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'dashboard',
        loadComponent: () => import('./pages/admin/dashboard/admin-dashboard.component').then(m => m.AdminDashboardComponent)
      },
      {
        path: 'products',
        loadComponent: () => import('./pages/admin/products/admin-products.component').then(m => m.AdminProductsComponent)
      },
      {
        path: 'orders',
        loadComponent: () => import('./pages/admin/orders/admin-orders.component').then(m => m.AdminOrdersComponent)
      },
      {
        path: 'users',
        loadComponent: () => import('./pages/admin/users/admin-users.component').then(m => m.AdminUsersComponent)
      },
      {
        path: 'print-jobs',
        loadComponent: () => import('./pages/admin/print-jobs/admin-print-jobs.component').then(m => m.AdminPrintJobsComponent)
      },
      {
        path: 'expenses',
        loadComponent: () => import('./pages/admin/expenses/admin-expenses.component').then(m => m.AdminExpensesComponent)
      },
      {
        path: 'sellers',
        loadComponent: () => import('./pages/admin/sellers/admin-sellers.component').then(m => m.AdminSellersComponent)
      },
      {
        path: 'reports',
        loadComponent: () => import('./pages/admin/reports/admin-reports.component').then(m => m.AdminReportsComponent)
      }
    ]
  },

  // Seller routes
  {
    path: 'seller',
    loadComponent: () => import('./pages/seller/seller.component').then(m => m.SellerComponent),
    canActivate: [authGuard, roleGuard],
    data: { role: 'seller' },
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'dashboard',
        loadComponent: () => import('./pages/seller/dashboard/seller-dashboard.component').then(m => m.SellerDashboardComponent)
      },
      {
        path: 'commissions',
        loadComponent: () => import('./pages/seller/commissions/seller-commissions.component').then(m => m.SellerCommissionsComponent)
      },
      {
        path: 'payments',
        loadComponent: () => import('./pages/seller/payments/seller-payments.component').then(m => m.SellerPaymentsComponent)
      },
      {
        path: 'customers',
        loadComponent: () => import('./pages/seller/customers/seller-customers.component').then(m => m.SellerCustomersComponent)
      }
    ]
  },

  // Error routes
  {
    path: 'unauthorized',
    loadComponent: () => import('./pages/error/unauthorized.component').then(m => m.UnauthorizedComponent)
  },
  {
    path: '**',
    loadComponent: () => import('./pages/error/not-found.component').then(m => m.NotFoundComponent)
  }
];
