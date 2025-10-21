import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from '../../../shared/material.module';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    ReactiveFormsModule,
    MaterialModule
  ],
  template: `
    <div class="register-container">
      <mat-card class="register-card">
        <mat-card-header>
          <mat-card-title>
            <h1>Create Account</h1>
          </mat-card-title>
          <mat-card-subtitle>
            Join 3D Store today
          </mat-card-subtitle>
        </mat-card-header>

        <mat-card-content>
          <form [formGroup]="registerForm" (ngSubmit)="onSubmit()">
            <!-- Name Fields -->
            <div class="name-fields">
              <mat-form-field appearance="outline">
                <mat-label>First Name</mat-label>
                <input matInput formControlName="first_name" autocomplete="given-name">
                <mat-icon matPrefix>person</mat-icon>
                @if (registerForm.get('first_name')?.hasError('required') && registerForm.get('first_name')?.touched) {
                  <mat-error>First name is required</mat-error>
                }
              </mat-form-field>

              <mat-form-field appearance="outline">
                <mat-label>Last Name</mat-label>
                <input matInput formControlName="last_name" autocomplete="family-name">
                @if (registerForm.get('last_name')?.hasError('required') && registerForm.get('last_name')?.touched) {
                  <mat-error>Last name is required</mat-error>
                }
              </mat-form-field>
            </div>

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
              @if (registerForm.get('email')?.hasError('required') && registerForm.get('email')?.touched) {
                <mat-error>Email is required</mat-error>
              }
              @if (registerForm.get('email')?.hasError('email') && registerForm.get('email')?.touched) {
                <mat-error>Please enter a valid email</mat-error>
              }
            </mat-form-field>

            <!-- Phone Field -->
            <mat-form-field appearance="outline">
              <mat-label>Phone</mat-label>
              <input 
                matInput 
                type="tel" 
                formControlName="phone"
                placeholder="+968 12345678"
                autocomplete="tel">
              <mat-icon matPrefix>phone</mat-icon>
              @if (registerForm.get('phone')?.hasError('required') && registerForm.get('phone')?.touched) {
                <mat-error>Phone is required</mat-error>
              }
            </mat-form-field>

            <!-- Password Field -->
            <mat-form-field appearance="outline">
              <mat-label>Password</mat-label>
              <input 
                matInput 
                [type]="hidePassword ? 'password' : 'text'" 
                formControlName="password"
                autocomplete="new-password">
              <mat-icon matPrefix>lock</mat-icon>
              <button 
                mat-icon-button 
                matSuffix 
                type="button"
                (click)="hidePassword = !hidePassword">
                <mat-icon>{{ hidePassword ? 'visibility_off' : 'visibility' }}</mat-icon>
              </button>
              @if (registerForm.get('password')?.hasError('required') && registerForm.get('password')?.touched) {
                <mat-error>Password is required</mat-error>
              }
              @if (registerForm.get('password')?.hasError('minlength') && registerForm.get('password')?.touched) {
                <mat-error>Password must be at least 8 characters</mat-error>
              }
              <mat-hint>At least 8 characters with uppercase, lowercase, and number</mat-hint>
            </mat-form-field>

            <!-- Confirm Password Field -->
            <mat-form-field appearance="outline">
              <mat-label>Confirm Password</mat-label>
              <input 
                matInput 
                [type]="hideConfirmPassword ? 'password' : 'text'" 
                formControlName="confirmPassword"
                autocomplete="new-password">
              <mat-icon matPrefix>lock</mat-icon>
              <button 
                mat-icon-button 
                matSuffix 
                type="button"
                (click)="hideConfirmPassword = !hideConfirmPassword">
                <mat-icon>{{ hideConfirmPassword ? 'visibility_off' : 'visibility' }}</mat-icon>
              </button>
              @if (registerForm.get('confirmPassword')?.hasError('required') && registerForm.get('confirmPassword')?.touched) {
                <mat-error>Please confirm your password</mat-error>
              }
              @if (registerForm.hasError('passwordMismatch') && registerForm.get('confirmPassword')?.touched) {
                <mat-error>Passwords do not match</mat-error>
              }
            </mat-form-field>

            <!-- Language Selection -->
            <mat-form-field appearance="outline">
              <mat-label>Preferred Language</mat-label>
              <mat-select formControlName="language">
                <mat-option value="ENGLISH">English</mat-option>
                <mat-option value="ARABIC">Arabic</mat-option>
              </mat-select>
              <mat-icon matPrefix>language</mat-icon>
            </mat-form-field>

            <!-- Terms and Conditions -->
            <mat-checkbox formControlName="acceptTerms" class="terms-checkbox">
              I agree to the 
              <a routerLink="/terms" target="_blank">Terms of Service</a> 
              and 
              <a routerLink="/privacy" target="_blank">Privacy Policy</a>
            </mat-checkbox>
            @if (registerForm.get('acceptTerms')?.hasError('required') && registerForm.get('acceptTerms')?.touched) {
              <mat-error class="terms-error">You must accept the terms and conditions</mat-error>
            }

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
              [disabled]="registerForm.invalid || loading"
              class="submit-btn">
              @if (loading) {
                <mat-spinner diameter="20"></mat-spinner>
                Creating account...
              } @else {
                Create Account
              }
            </button>
          </form>

          <!-- Login Link -->
          <div class="login-link">
            Already have an account? 
            <a routerLink="/login">Sign in</a>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .register-container {
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 2rem 1rem;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .register-card {
      max-width: 500px;
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
    }

    .name-fields {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
      
      mat-form-field {
        width: 100%;
      }
    }

    mat-form-field {
      width: 100%;
    }

    .terms-checkbox {
      margin: 0.5rem 0;
      
      a {
        color: #3f51b5;
        text-decoration: none;
        
        &:hover {
          text-decoration: underline;
        }
      }
    }

    .terms-error {
      color: #f44336;
      font-size: 0.75rem;
      margin-top: -0.5rem;
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
      margin-top: 0.5rem;
      
      mat-spinner {
        display: inline-block;
        margin-right: 0.5rem;
      }
    }

    .login-link {
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
export class RegisterComponent implements OnInit {
  registerForm: FormGroup;
  loading = false;
  errorMessage: string | null = null;
  hidePassword = true;
  hideConfirmPassword = true;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.registerForm = this.fb.group({
      first_name: ['', [Validators.required]],
      last_name: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      phone: ['', [Validators.required]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', [Validators.required]],
      language: ['ENGLISH'],
      acceptTerms: [false, [Validators.requiredTrue]]
    }, { validators: this.passwordMatchValidator });
  }

  ngOnInit(): void {
    // Redirect if already logged in
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/dashboard']);
    }
  }

  onSubmit(): void {
    if (this.registerForm.invalid) {
      return;
    }

    this.loading = true;
    this.errorMessage = null;

    const { confirmPassword, acceptTerms, ...registerData } = this.registerForm.value;

    this.authService.register(registerData).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/dashboard']);
      },
      error: (error) => {
        this.loading = false;
        this.errorMessage = error.message || 'Registration failed. Please try again.';
      }
    });
  }

  loginWithGoogle(): void {
    window.location.href = 'http://localhost:5000/3dstore/api/v1/auth/google';
  }

  loginWithApple(): void {
    window.location.href = 'http://localhost:5000/3dstore/api/v1/auth/apple';
  }

  private passwordMatchValidator(form: FormGroup): { [key: string]: boolean } | null {
    const password = form.get('password');
    const confirmPassword = form.get('confirmPassword');
    
    if (password && confirmPassword && password.value !== confirmPassword.value) {
      return { passwordMismatch: true };
    }
    
    return null;
  }
}

