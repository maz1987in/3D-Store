import { createFeatureSelector, createSelector } from '@ngrx/store';
import { AuthState } from '../reducers/auth.reducer';

export const selectAuthState = createFeatureSelector<AuthState>('auth');

export const selectCurrentUser = createSelector(
  selectAuthState,
  (state) => state.user
);

export const selectIsAuthenticated = createSelector(
  selectAuthState,
  (state) => state.isAuthenticated
);

export const selectAuthToken = createSelector(
  selectAuthState,
  (state) => state.token
);

export const selectAuthLoading = createSelector(
  selectAuthState,
  (state) => state.loading
);

export const selectAuthError = createSelector(
  selectAuthState,
  (state) => state.error
);

export const selectUserRoles = createSelector(
  selectCurrentUser,
  (user) => user?.roles || []
);

export const selectUserPermissions = createSelector(
  selectCurrentUser,
  (user) => user?.permissions || []
);

export const selectIsAdmin = createSelector(
  selectCurrentUser,
  (user) => user?.user_type === 'ADMIN'
);

export const selectIsSeller = createSelector(
  selectUserRoles,
  (roles) => roles.includes('seller')
);

export const selectHasPermission = (permission: string) =>
  createSelector(selectUserPermissions, (permissions) =>
    permissions.includes(permission)
  );

export const selectHasRole = (role: string) =>
  createSelector(selectUserRoles, (roles) => roles.includes(role));

