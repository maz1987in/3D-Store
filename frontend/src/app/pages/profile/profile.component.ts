import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from '../../shared/material.module';
import { LoadingComponent } from '../../shared/components/loading/loading.component';
import { AuthService } from '../../core/services/auth.service';
import { User, PasswordChange } from '../../models/user.model';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MaterialModule,
    LoadingComponent
  ],
  template: `
    <div class="profile-container">
      <h1>My Profile</h1>

      @if (loading) {
        <app-loading type="skeleton"></app-loading>
      } @else if (user) {
        <mat-tab-group>
          <!-- Profile Information Tab -->
          <mat-tab label="Profile Information">
            <div class="tab-content">
              <form [formGroup]="profileForm" (ngSubmit)="updateProfile()">
                <div class="form-row two-columns">
                  <mat-form-field appearance="outline">
                    <mat-label>First Name</mat-label>
                    <input matInput formControlName="first_name">
                    <mat-error>First name is required</mat-error>
                  </mat-form-field>

                  <mat-form-field appearance="outline">
                    <mat-label>Last Name</mat-label>
                    <input matInput formControlName="last_name">
                    <mat-error>Last name is required</mat-error>
                  </mat-form-field>
                </div>

                <mat-form-field appearance="outline">
                  <mat-label>Email</mat-label>
                  <input matInput type="email" formControlName="email">
                  <mat-icon matPrefix>email</mat-icon>
                  <mat-error>Please enter a valid email</mat-error>
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>Phone</mat-label>
                  <input matInput type="tel" formControlName="phone">
                  <mat-icon matPrefix>phone</mat-icon>
                  <mat-error>Phone is required</mat-error>
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>Preferred Language</mat-label>
                  <mat-select formControlName="language">
                    <mat-option value="ENGLISH">English</mat-option>
                    <mat-option value="ARABIC">Arabic</mat-option>
                  </mat-select>
                  <mat-icon matPrefix>language</mat-icon>
                </mat-form-field>

                @if (profileUpdateMessage) {
                  <div [class]="profileUpdateSuccess ? 'success-message' : 'error-message'">
                    <mat-icon>{{ profileUpdateSuccess ? 'check_circle' : 'error' }}</mat-icon>
                    <span>{{ profileUpdateMessage }}</span>
                  </div>
                }

                <div class="form-actions">
                  <button 
                    mat-raised-button 
                    color="primary" 
                    type="submit"
                    [disabled]="profileForm.invalid || updatingProfile">
                    @if (updatingProfile) {
                      <mat-spinner diameter="20"></mat-spinner>
                      Updating...
                    } @else {
                      Save Changes
                    }
                  </button>
                </div>
              </form>
            </div>
          </mat-tab>

          <!-- Change Password Tab -->
          <mat-tab label="Change Password">
            <div class="tab-content">
              <form [formGroup]="passwordForm" (ngSubmit)="changePassword()">
                <mat-form-field appearance="outline">
                  <mat-label>Current Password</mat-label>
                  <input 
                    matInput 
                    [type]="hideCurrentPassword ? 'password' : 'text'" 
                    formControlName="current_password">
                  <mat-icon matPrefix>lock</mat-icon>
                  <button 
                    mat-icon-button 
                    matSuffix 
                    type="button"
                    (click)="hideCurrentPassword = !hideCurrentPassword">
                    <mat-icon>{{ hideCurrentPassword ? 'visibility_off' : 'visibility' }}</mat-icon>
                  </button>
                  <mat-error>Current password is required</mat-error>
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>New Password</mat-label>
                  <input 
                    matInput 
                    [type]="hideNewPassword ? 'password' : 'text'" 
                    formControlName="new_password">
                  <mat-icon matPrefix>lock</mat-icon>
                  <button 
                    mat-icon-button 
                    matSuffix 
                    type="button"
                    (click)="hideNewPassword = !hideNewPassword">
                    <mat-icon>{{ hideNewPassword ? 'visibility_off' : 'visibility' }}</mat-icon>
                  </button>
                  <mat-error>
                    @if (passwordForm.get('new_password')?.hasError('required')) {
                      New password is required
                    } @else if (passwordForm.get('new_password')?.hasError('minlength')) {
                      Password must be at least 8 characters
                    }
                  </mat-error>
                  <mat-hint>At least 8 characters with uppercase, lowercase, and number</mat-hint>
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>Confirm New Password</mat-label>
                  <input 
                    matInput 
                    [type]="hideConfirmPassword ? 'password' : 'text'" 
                    formControlName="confirm_password">
                  <mat-icon matPrefix>lock</mat-icon>
                  <button 
                    mat-icon-button 
                    matSuffix 
                    type="button"
                    (click)="hideConfirmPassword = !hideConfirmPassword">
                    <mat-icon>{{ hideConfirmPassword ? 'visibility_off' : 'visibility' }}</mat-icon>
                  </button>
                  <mat-error>
                    @if (passwordForm.get('confirm_password')?.hasError('required')) {
                      Please confirm your password
                    } @else if (passwordForm.hasError('passwordMismatch')) {
                      Passwords do not match
                    }
                  </mat-error>
                </mat-form-field>

                @if (passwordUpdateMessage) {
                  <div [class]="passwordUpdateSuccess ? 'success-message' : 'error-message'">
                    <mat-icon>{{ passwordUpdateSuccess ? 'check_circle' : 'error' }}</mat-icon>
                    <span>{{ passwordUpdateMessage }}</span>
                  </div>
                }

                <div class="form-actions">
                  <button 
                    mat-raised-button 
                    color="primary" 
                    type="submit"
                    [disabled]="passwordForm.invalid || changingPassword">
                    @if (changingPassword) {
                      <mat-spinner diameter="20"></mat-spinner>
                      Changing...
                    } @else {
                      Change Password
                    }
                  </button>
                </div>
              </form>
            </div>
          </mat-tab>

          <!-- Account Settings Tab -->
          <mat-tab label="Settings">
            <div class="tab-content">
              <div class="settings-section">
                <h3>Notifications</h3>
                <mat-checkbox>Email notifications</mat-checkbox>
                <mat-checkbox>SMS notifications</mat-checkbox>
                <mat-checkbox>Order updates</mat-checkbox>
              </div>

              <mat-divider></mat-divider>

              <div class="settings-section">
                <h3>Account</h3>
                <p class="account-info">
                  <strong>Account Type:</strong> {{ user.user_type }}
                </p>
                <p class="account-info">
                  <strong>Member Since:</strong> {{ user.create_date | date:'mediumDate' }}
                </p>
                <p class="account-info">
                  <strong>Status:</strong> 
                  <mat-chip [color]="user.active ? 'accent' : 'warn'">
                    {{ user.active ? 'Active' : 'Inactive' }}
                  </mat-chip>
                </p>
              </div>

              <mat-divider></mat-divider>

              <div class="settings-section danger-zone">
                <h3>Danger Zone</h3>
                <p>Once you delete your account, there is no going back. Please be certain.</p>
                <button mat-raised-button color="warn">
                  Delete Account
                </button>
              </div>
            </div>
          </mat-tab>
        </mat-tab-group>
      }
    </div>
  `,
  styles: [`
    .profile-container {
      max-width: 800px;
      margin: 0 auto;
      padding: 2rem 1rem;
      
      h1 {
        margin-bottom: 2rem;
      }
    }

    .tab-content {
      padding: 2rem;
    }

    form {
      max-width: 600px;
      
      .form-row {
        margin-bottom: 1rem;
        
        &.two-columns {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
        }
      }
      
      mat-form-field {
        width: 100%;
      }
    }

    .success-message,
    .error-message {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.75rem;
      border-radius: 4px;
      margin-bottom: 1rem;
    }

    .success-message {
      background: #e8f5e9;
      color: #2e7d32;
    }

    .error-message {
      background: #ffebee;
      color: #c62828;
    }

    .form-actions {
      margin-top: 1.5rem;
      
      button {
        min-width: 150px;
        
        mat-spinner {
          display: inline-block;
          margin-right: 0.5rem;
        }
      }
    }

    .settings-section {
      padding: 1.5rem 0;
      
      h3 {
        margin: 0 0 1rem;
        font-size: 1.125rem;
      }
      
      mat-checkbox {
        display: block;
        margin-bottom: 0.75rem;
      }
      
      .account-info {
        margin: 0.5rem 0;
        color: #666;
        
        strong {
          color: #333;
        }
        
        mat-chip {
          margin-left: 0.5rem;
        }
      }
      
      &.danger-zone {
        p {
          color: #666;
          margin-bottom: 1rem;
        }
      }
    }
  `]
})
export class ProfileComponent implements OnInit {
  user: User | null = null;
  profileForm: FormGroup;
  passwordForm: FormGroup;
  
  loading = false;
  updatingProfile = false;
  changingPassword = false;
  
  profileUpdateMessage: string | null = null;
  profileUpdateSuccess = false;
  passwordUpdateMessage: string | null = null;
  passwordUpdateSuccess = false;
  
  hideCurrentPassword = true;
  hideNewPassword = true;
  hideConfirmPassword = true;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService
  ) {
    this.profileForm = this.fb.group({
      first_name: ['', Validators.required],
      last_name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      phone: ['', Validators.required],
      language: ['ENGLISH']
    });

    this.passwordForm = this.fb.group({
      current_password: ['', Validators.required],
      new_password: ['', [Validators.required, Validators.minLength(8)]],
      confirm_password: ['', Validators.required]
    }, { validators: this.passwordMatchValidator });
  }

  ngOnInit(): void {
    this.loadProfile();
  }

  loadProfile(): void {
    this.loading = true;

    this.authService.getProfile().subscribe({
      next: (user) => {
        this.user = user;
        this.profileForm.patchValue(user);
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  updateProfile(): void {
    if (this.profileForm.invalid) return;

    this.updatingProfile = true;
    this.profileUpdateMessage = null;

    // API call would go here
    setTimeout(() => {
      this.updatingProfile = false;
      this.profileUpdateSuccess = true;
      this.profileUpdateMessage = 'Profile updated successfully';
      
      setTimeout(() => {
        this.profileUpdateMessage = null;
      }, 3000);
    }, 1000);
  }

  changePassword(): void {
    if (this.passwordForm.invalid) return;

    this.changingPassword = true;
    this.passwordUpdateMessage = null;

    const { current_password, new_password } = this.passwordForm.value;

    this.authService.changePassword({ current_password, new_password }).subscribe({
      next: () => {
        this.changingPassword = false;
        this.passwordUpdateSuccess = true;
        this.passwordUpdateMessage = 'Password changed successfully';
        this.passwordForm.reset();
        
        setTimeout(() => {
          this.passwordUpdateMessage = null;
        }, 3000);
      },
      error: (error) => {
        this.changingPassword = false;
        this.passwordUpdateSuccess = false;
        this.passwordUpdateMessage = error.message || 'Failed to change password';
      }
    });
  }

  private passwordMatchValidator(form: FormGroup): { [key: string]: boolean } | null {
    const newPassword = form.get('new_password');
    const confirmPassword = form.get('confirm_password');
    
    if (newPassword && confirmPassword && newPassword.value !== confirmPassword.value) {
      return { passwordMismatch: true };
    }
    
    return null;
  }
}

