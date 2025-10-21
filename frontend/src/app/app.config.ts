import { ApplicationConfig, importProvidersFrom } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideStore } from '@ngrx/store';
import { provideEffects } from '@ngrx/effects';
import { provideStoreDevtools } from '@ngrx/store-devtools';

import { routes } from './app.routes';
import { authInterceptor } from './core/interceptors/auth.interceptor';
import { errorInterceptor } from './core/interceptors/error.interceptor';
import { MaterialModule } from './shared/material.module';
import { environment } from '../environments/environment';
import { reducers, metaReducers } from './store/reducers';
import { AuthEffects } from './store/effects/auth.effects';
import { CartEffects } from './store/effects/cart.effects';
import { ProductEffects } from './store/effects/product.effects';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(
      withInterceptors([authInterceptor, errorInterceptor])
    ),
    provideAnimations(),
    provideStore(reducers, { metaReducers }),
    provideEffects([AuthEffects, CartEffects, ProductEffects]),
    provideStoreDevtools({
      maxAge: 25,
      logOnly: environment.production,
      trace: !environment.production,
      traceLimit: 75
    }),
    importProvidersFrom(MaterialModule)
  ]
};
