import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { tap, map } from 'rxjs/operators';
import { Router } from '@angular/router';
import { environment } from '../../../environments/environment';
import {
  User,
  LoginCredentials,
  RegisterData,
  AuthResponse,
  PasswordChange,
  PasswordReset,
  PasswordResetConfirm
} from '../../models/user.model';
import { ApiResponse } from '../../models/common.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  private tokenKey = environment.tokenKey;
  private refreshTokenKey = environment.refreshTokenKey;
  private userKey = environment.userKey;

  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  private isAuthenticatedSubject = new BehaviorSubject<boolean>(false);
  public isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    this.loadUserFromStorage();
  }

  /**
   * Login user
   */
  login(credentials: LoginCredentials): Observable<AuthResponse> {
    return this.http.post<ApiResponse<AuthResponse>>(`${this.apiUrl}/auth/login`, credentials)
      .pipe(
        map(response => response.data),
        tap(authData => {
          this.setSession(authData);
        })
      );
  }

  /**
   * Register new user
   */
  register(userData: RegisterData): Observable<AuthResponse> {
    return this.http.post<ApiResponse<AuthResponse>>(`${this.apiUrl}/auth/register`, userData)
      .pipe(
        map(response => response.data),
        tap(authData => {
          this.setSession(authData);
        })
      );
  }

  /**
   * Logout user
   */
  logout(): void {
    // Call logout endpoint
    this.http.post(`${this.apiUrl}/auth/logout`, {}).subscribe();

    // Clear local storage
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.refreshTokenKey);
    localStorage.removeItem(this.userKey);
    
    // Clear state
    this.currentUserSubject.next(null);
    this.isAuthenticatedSubject.next(false);
    
    // Navigate to login
    this.router.navigate(['/login']);
  }

  /**
   * Get current user profile
   */
  getProfile(): Observable<User> {
    return this.http.get<ApiResponse<User>>(`${this.apiUrl}/auth/profile`)
      .pipe(
        map(response => response.data),
        tap(user => {
          this.currentUserSubject.next(user);
          localStorage.setItem(this.userKey, JSON.stringify(user));
        })
      );
  }

  /**
   * Change password
   */
  changePassword(data: PasswordChange): Observable<void> {
    return this.http.post<ApiResponse<void>>(`${this.apiUrl}/auth/change-password`, data)
      .pipe(
        map(response => response.data)
      );
  }

  /**
   * Request password reset
   */
  requestPasswordReset(data: PasswordReset): Observable<void> {
    return this.http.post<ApiResponse<void>>(`${this.apiUrl}/auth/password-reset-request`, data)
      .pipe(
        map(response => response.data)
      );
  }

  /**
   * Confirm password reset
   */
  confirmPasswordReset(data: PasswordResetConfirm): Observable<void> {
    return this.http.post<ApiResponse<void>>(`${this.apiUrl}/auth/password-reset`, data)
      .pipe(
        map(response => response.data)
      );
  }

  /**
   * Refresh access token
   */
  refreshToken(): Observable<AuthResponse> {
    const refreshToken = this.getRefreshToken();
    return this.http.post<ApiResponse<AuthResponse>>(`${this.apiUrl}/auth/refresh`, {
      refresh_token: refreshToken
    }).pipe(
      map(response => response.data),
      tap(authData => {
        this.setSession(authData);
      })
    );
  }

  /**
   * Get JWT token
   */
  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  /**
   * Get refresh token
   */
  getRefreshToken(): string | null {
    return localStorage.getItem(this.refreshTokenKey);
  }

  /**
   * Get current user
   */
  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = this.getToken();
    return !!token && !this.isTokenExpired(token);
  }

  /**
   * Check if user has permission
   */
  hasPermission(permission: string): Observable<boolean> {
    return this.currentUser$.pipe(
      map(user => user?.permissions?.includes(permission) || false)
    );
  }

  /**
   * Check if user has role
   */
  hasRole(role: string): Observable<boolean> {
    return this.currentUser$.pipe(
      map(user => user?.roles?.includes(role) || false)
    );
  }

  /**
   * Check if user is admin
   */
  isAdmin(): Observable<boolean> {
    return this.currentUser$.pipe(
      map(user => user?.user_type === 'ADMIN' || false)
    );
  }

  /**
   * Set authentication session
   */
  private setSession(authData: AuthResponse): void {
    localStorage.setItem(this.tokenKey, authData.token);
    localStorage.setItem(this.refreshTokenKey, authData.refresh_token);
    localStorage.setItem(this.userKey, JSON.stringify(authData.user));
    
    this.currentUserSubject.next(authData.user);
    this.isAuthenticatedSubject.next(true);
  }

  /**
   * Load user from local storage
   */
  private loadUserFromStorage(): void {
    const userJson = localStorage.getItem(this.userKey);
    const token = this.getToken();
    
    if (userJson && token && !this.isTokenExpired(token)) {
      try {
        const user = JSON.parse(userJson);
        this.currentUserSubject.next(user);
        this.isAuthenticatedSubject.next(true);
      } catch (error) {
        console.error('Error parsing user data:', error);
        this.logout();
      }
    }
  }

  /**
   * Check if token is expired
   */
  private isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expirationDate = payload.exp * 1000; // Convert to milliseconds
      return Date.now() >= expirationDate;
    } catch (error) {
      console.error('Error checking token expiration:', error);
      return true;
    }
  }
}
