import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from '../../../shared/material.module';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    ReactiveFormsModule,
    MaterialModule
  ],
  template: `
    <div class="login-container">
      <mat-card class="login-card">
        <mat-card-header>
          <mat-card-title>
            <h1>Welcome Back</h1>
          </mat-card-title>
          <mat-card-subtitle>
            Sign in to your account
          </mat-card-subtitle>
        </mat-card-header>

        <mat-card-content>
          <form [formGroup]="loginForm" (ngSubmit)="onSubmit()">
            <!-- Email Field -->
            <mat-form-field appearance="outline">
              <mat-label>Email</mat-label>
              <input 
                matInput 
                type="email" 
                formControlName="email"
                placeholder="you@example.com"
                autocomplete="email">
              <mat-icon matPrefix>email</mat-icon>
              @if (loginForm.get('email')?.hasError('required') && loginForm.get('email')?.touched) {
                <mat-error>Email is required</mat-error>
              }
              @if (loginForm.get('email')?.hasError('email') && loginForm.get('email')?.touched) {
                <mat-error>Please enter a valid email</mat-error>
              }
            </mat-form-field>

            <!-- Password Field -->
            <mat-form-field appearance="outline">
              <mat-label>Password</mat-label>
              <input 
                matInput 
                [type]="hidePassword ? 'password' : 'text'" 
                formControlName="password"
                autocomplete="current-password">
              <mat-icon matPrefix>lock</mat-icon>
              <button 
                mat-icon-button 
                matSuffix 
                type="button"
                (click)="hidePassword = !hidePassword">
                <mat-icon>{{ hidePassword ? 'visibility_off' : 'visibility' }}</mat-icon>
              </button>
              @if (loginForm.get('password')?.hasError('required') && loginForm.get('password')?.touched) {
                <mat-error>Password is required</mat-error>
              }
            </mat-form-field>

            <!-- Remember Me & Forgot Password -->
            <div class="form-options">
              <mat-checkbox formControlName="rememberMe">
                Remember me
              </mat-checkbox>
              <a routerLink="/forgot-password" class="forgot-link">
                Forgot password?
              </a>
            </div>

            <!-- Error Message -->
            @if (errorMessage) {
              <div class="error-message">
                <mat-icon>error</mat-icon>
                <span>{{ errorMessage }}</span>
              </div>
            }

            <!-- Submit Button -->
            <button 
              mat-raised-button 
              color="primary" 
              type="submit"
              [disabled]="loginForm.invalid || loading"
              class="submit-btn">
              @if (loading) {
                <mat-spinner diameter="20"></mat-spinner>
                Signing in...
              } @else {
                Sign In
              }
            </button>
          </form>

          <!-- Divider -->
          <div class="divider">
            <span>or continue with</span>
          </div>

          <!-- OAuth Buttons -->
          <div class="oauth-buttons">
            <button mat-stroked-button class="oauth-btn google-btn" (click)="loginWithGoogle()">
              <mat-icon>g</mat-icon>
              Google
            </button>
            <button mat-stroked-button class="oauth-btn apple-btn" (click)="loginWithApple()">
              <mat-icon>apple</mat-icon>
              Apple
            </button>
          </div>

          <!-- Register Link -->
          <div class="register-link">
            Don't have an account? 
            <a routerLink="/register">Sign up</a>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .login-container {
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 2rem 1rem;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .login-card {
      max-width: 450px;
      width: 100%;
      
      mat-card-header {
        text-align: center;
        margin-bottom: 1rem;
        
        h1 {
          margin: 0;
          font-size: 2rem;
        }
      }
    }

    form {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      
      mat-form-field {
        width: 100%;
      }
    }

    .form-options {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.5rem;
      
      .forgot-link {
        color: #3f51b5;
        text-decoration: none;
        font-size: 0.875rem;
        
        &:hover {
          text-decoration: underline;
        }
      }
    }

    .error-message {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.75rem;
      background: #ffebee;
      border-radius: 4px;
      color: #c62828;
      
      mat-icon {
        font-size: 20px;
        width: 20px;
        height: 20px;
      }
    }

    .submit-btn {
      width: 100%;
      height: 48px;
      font-size: 1rem;
      
      mat-spinner {
        display: inline-block;
        margin-right: 0.5rem;
      }
    }

    .divider {
      text-align: center;
      margin: 1.5rem 0;
      position: relative;
      
      &::before,
      &::after {
        content: '';
        position: absolute;
        top: 50%;
        width: 45%;
        height: 1px;
        background: #ddd;
      }
      
      &::before {
        left: 0;
      }
      
      &::after {
        right: 0;
      }
      
      span {
        background: white;
        padding: 0 1rem;
        color: #666;
        font-size: 0.875rem;
      }
    }

    .oauth-buttons {
      display: flex;
      gap: 1rem;
      
      .oauth-btn {
        flex: 1;
        
        mat-icon {
          margin-right: 0.5rem;
        }
      }
    }

    .register-link {
      text-align: center;
      margin-top: 1.5rem;
      color: #666;
      
      a {
        color: #3f51b5;
        text-decoration: none;
        font-weight: 600;
        
        &:hover {
          text-decoration: underline;
        }
      }
    }
  `]
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup;
  loading = false;
  errorMessage: string | null = null;
  hidePassword = true;
  returnUrl = '/dashboard';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]],
      rememberMe: [false]
    });
  }

  ngOnInit(): void {
    // Get return URL from route parameters or default to dashboard
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/dashboard';
    
    // Redirect if already logged in
    if (this.authService.isAuthenticated()) {
      this.router.navigate([this.returnUrl]);
    }
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      return;
    }

    this.loading = true;
    this.errorMessage = null;

    const { email, password } = this.loginForm.value;

    this.authService.login({ email, password }).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate([this.returnUrl]);
      },
      error: (error) => {
        this.loading = false;
        this.errorMessage = error.message || 'Invalid email or password';
      }
    });
  }

  loginWithGoogle(): void {
    // Redirect to Google OAuth
    window.location.href = 'http://localhost:5000/3dstore/api/v1/auth/google';
  }

  loginWithApple(): void {
    // Redirect to Apple OAuth
    window.location.href = 'http://localhost:5000/3dstore/api/v1/auth/apple';
  }
}

