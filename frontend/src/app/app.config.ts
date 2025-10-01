import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { withInterceptorsFromDi, provideHttpClient } from '@angular/common/http';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { AUTH_INTERCEPTOR_PROVIDER } from './core/interceptors/auth.interceptor';

import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';

export const appConfig: ApplicationConfig = {
  providers: [provideZoneChangeDetection({ eventCoalescing: true }), provideRouter(routes), provideHttpClient(withInterceptorsFromDi()), AUTH_INTERCEPTOR_PROVIDER, provideAnimationsAsync()]
};
