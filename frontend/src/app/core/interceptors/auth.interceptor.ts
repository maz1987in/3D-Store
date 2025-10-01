import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { HttpInterceptorFn, HttpRequest } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('access_token');
  let authReq: HttpRequest<unknown> = req;

  if (token) {
    authReq = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }

  return next(authReq);
};

export const AUTH_INTERCEPTOR_PROVIDER = { provide: HTTP_INTERCEPTORS, useValue: authInterceptor, multi: true };
