import { Injectable, inject } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { Router } from '@angular/router';
import { of } from 'rxjs';
import { map, catchError, exhaustMap, tap } from 'rxjs/operators';
import { AuthService } from '../../core/services/auth.service';
import * as AuthActions from '../actions/auth.actions';

@Injectable()
export class AuthEffects {
  
  private actions$ = inject(Actions);
  private authService = inject(AuthService);
  private router = inject(Router);
  
  login$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AuthActions.login),
      exhaustMap(({ credentials }) =>
        this.authService.login(credentials).pipe(
          map(response => AuthActions.loginSuccess({ response })),
          catchError(error => of(AuthActions.loginFailure({ error: error.message })))
        )
      )
    )
  );

  loginSuccess$ = createEffect(
    () =>
      this.actions$.pipe(
        ofType(AuthActions.loginSuccess),
        tap(() => {
          this.router.navigate(['/dashboard']);
        })
      ),
    { dispatch: false }
  );

  register$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AuthActions.register),
      exhaustMap(({ userData }) =>
        this.authService.register(userData).pipe(
          map(response => AuthActions.registerSuccess({ response })),
          catchError(error => of(AuthActions.registerFailure({ error: error.message })))
        )
      )
    )
  );

  registerSuccess$ = createEffect(
    () =>
      this.actions$.pipe(
        ofType(AuthActions.registerSuccess),
        tap(() => {
          this.router.navigate(['/dashboard']);
        })
      ),
    { dispatch: false }
  );

  logout$ = createEffect(
    () =>
      this.actions$.pipe(
        ofType(AuthActions.logout),
        tap(() => {
          this.authService.logout();
        }),
        map(() => AuthActions.logoutSuccess())
      )
  );

  loadProfile$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AuthActions.loadProfile),
      exhaustMap(() =>
        this.authService.getProfile().pipe(
          map(user => AuthActions.loadProfileSuccess({ user })),
          catchError(error => of(AuthActions.loadProfileFailure({ error: error.message })))
        )
      )
    )
  );

  updateProfile$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AuthActions.updateProfile),
      exhaustMap(({ userData }) =>
        // Service call would go here
        of(AuthActions.updateProfileSuccess({ user: userData as any }))
      )
    )
  );

  changePassword$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AuthActions.changePassword),
      exhaustMap(({ currentPassword, newPassword }) =>
        this.authService.changePassword({ current_password: currentPassword, new_password: newPassword }).pipe(
          map(() => AuthActions.changePasswordSuccess()),
          catchError(error => of(AuthActions.changePasswordFailure({ error: error.message })))
        )
      )
    )
  );

  refreshToken$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AuthActions.refreshToken),
      exhaustMap(() =>
        this.authService.refreshToken().pipe(
          map(response => AuthActions.refreshTokenSuccess({ response })),
          catchError(error => of(AuthActions.refreshTokenFailure({ error: error.message })))
        )
      )
    )
  );
}

