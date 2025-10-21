import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterModule, Router } from '@angular/router';
import { MaterialModule } from './shared/material.module';
import { AuthService } from './core/services/auth.service';
import { CartService } from './services/cart.service';
import { User } from './models/user.model';
import { CartSummary } from './models/cart.model';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    RouterModule,
    MaterialModule
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {
  title = '3D Store';
  currentUser: User | null = null;
  isAuthenticated = false;
  currentYear = new Date().getFullYear();
  cartSummary: CartSummary = {
    items_count: 0,
    subtotal: 0,
    total: 0,
    currency: 'OMR'
  };

  constructor(
    public authService: AuthService,
    private cartService: CartService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Subscribe to auth state
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });

    this.authService.isAuthenticated$.subscribe(isAuth => {
      this.isAuthenticated = isAuth;
    });

    // Subscribe to cart updates
    this.cartService.cartSummary$.subscribe(summary => {
      this.cartSummary = summary;
    });
  }

  logout(): void {
    this.authService.logout();
  }

  isAdminOrSeller(): boolean {
    return this.currentUser?.user_type === 'ADMIN' || this.currentUser?.roles?.includes('seller') || false;
  }

  isAdmin(): boolean {
    return this.currentUser?.user_type === 'ADMIN' || false;
  }

  isSeller(): boolean {
    return this.currentUser?.roles?.includes('seller') || false;
  }
}
