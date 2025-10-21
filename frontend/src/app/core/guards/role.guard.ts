import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { map, take } from 'rxjs/operators';

export const roleGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  const requiredRole = route.data['role'] as string;
  const requiredPermission = route.data['permission'] as string;

  if (!authService.isAuthenticated()) {
    router.navigate(['/login'], { queryParams: { returnUrl: state.url } });
    return false;
  }

  // Check role if specified
  if (requiredRole) {
    return authService.hasRole(requiredRole).pipe(
      take(1),
      map(hasRole => {
        if (hasRole) {
          return true;
        } else {
          router.navigate(['/unauthorized']);
          return false;
        }
      })
    );
  }

  // Check permission if specified
  if (requiredPermission) {
    return authService.hasPermission(requiredPermission).pipe(
      take(1),
      map(hasPermission => {
        if (hasPermission) {
          return true;
        } else {
          router.navigate(['/unauthorized']);
          return false;
        }
      })
    );
  }

  // If no role or permission specified, just check authentication
  return true;
};

