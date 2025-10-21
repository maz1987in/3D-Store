import { createReducer, on } from '@ngrx/store';
import { User } from '../../models/user.model';
import * as AuthActions from '../actions/auth.actions';

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

export const initialState: AuthState = {
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  loading: false,
  error: null
};

export const authReducer = createReducer(
  initialState,
  
  // Login
  on(AuthActions.login, (state) => ({
    ...state,
    loading: true,
    error: null
  })),
  
  on(AuthActions.loginSuccess, (state, { response }) => ({
    ...state,
    user: response.user,
    token: response.token,
    refreshToken: response.refresh_token,
    isAuthenticated: true,
    loading: false,
    error: null
  })),
  
  on(AuthActions.loginFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Register
  on(AuthActions.register, (state) => ({
    ...state,
    loading: true,
    error: null
  })),
  
  on(AuthActions.registerSuccess, (state, { response }) => ({
    ...state,
    user: response.user,
    token: response.token,
    refreshToken: response.refresh_token,
    isAuthenticated: true,
    loading: false,
    error: null
  })),
  
  on(AuthActions.registerFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Logout
  on(AuthActions.logout, (state) => ({
    ...state,
    loading: true
  })),
  
  on(AuthActions.logoutSuccess, () => initialState),
  
  // Load Profile
  on(AuthActions.loadProfile, (state) => ({
    ...state,
    loading: true,
    error: null
  })),
  
  on(AuthActions.loadProfileSuccess, (state, { user }) => ({
    ...state,
    user,
    loading: false,
    error: null
  })),
  
  on(AuthActions.loadProfileFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Update Profile
  on(AuthActions.updateProfile, (state) => ({
    ...state,
    loading: true,
    error: null
  })),
  
  on(AuthActions.updateProfileSuccess, (state, { user }) => ({
    ...state,
    user,
    loading: false,
    error: null
  })),
  
  on(AuthActions.updateProfileFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Change Password
  on(AuthActions.changePassword, (state) => ({
    ...state,
    loading: true,
    error: null
  })),
  
  on(AuthActions.changePasswordSuccess, (state) => ({
    ...state,
    loading: false,
    error: null
  })),
  
  on(AuthActions.changePasswordFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  
  // Refresh Token
  on(AuthActions.refreshToken, (state) => ({
    ...state,
    loading: true
  })),
  
  on(AuthActions.refreshTokenSuccess, (state, { response }) => ({
    ...state,
    token: response.token,
    refreshToken: response.refresh_token,
    loading: false
  })),
  
  on(AuthActions.refreshTokenFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  }))
);

