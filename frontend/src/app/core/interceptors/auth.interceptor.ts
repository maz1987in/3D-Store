import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Get the auth token from the service
  const authToken = authService.getToken();

  // Clone the request and add the authorization header if token exists
  if (authToken) {
    req = req.clone({
      setHeaders: {
        'x-access-tokens': authToken
      }
    });
  }

  // Handle the request
  return next(req).pipe(
    catchError((error) => {
      // Handle 401 Unauthorized errors
      if (error.status === 401) {
        authService.logout();
        router.navigate(['/login']);
      }
      return throwError(() => error);
    })
  );
};
