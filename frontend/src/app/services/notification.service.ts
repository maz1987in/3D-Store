import { Injectable } from '@angular/core';
import { MatSnackBar, MatSnackBarConfig } from '@angular/material/snack-bar';

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private defaultConfig: MatSnackBarConfig = {
    duration: 3000,
    horizontalPosition: 'right',
    verticalPosition: 'top'
  };

  constructor(private snackBar: MatSnackBar) {}

  /**
   * Show success notification
   */
  success(message: string, duration?: number): void {
    this.snackBar.open(message, 'Close', {
      ...this.defaultConfig,
      duration: duration || this.defaultConfig.duration,
      panelClass: ['snackbar-success']
    });
  }

  /**
   * Show error notification
   */
  error(message: string, duration?: number): void {
    this.snackBar.open(message, 'Close', {
      ...this.defaultConfig,
      duration: duration || this.defaultConfig.duration,
      panelClass: ['snackbar-error']
    });
  }

  /**
   * Show warning notification
   */
  warning(message: string, duration?: number): void {
    this.snackBar.open(message, 'Close', {
      ...this.defaultConfig,
      duration: duration || this.defaultConfig.duration,
      panelClass: ['snackbar-warning']
    });
  }

  /**
   * Show info notification
   */
  info(message: string, duration?: number): void {
    this.snackBar.open(message, 'Close', {
      ...this.defaultConfig,
      duration: duration || this.defaultConfig.duration,
      panelClass: ['snackbar-info']
    });
  }

  /**
   * Show notification with custom action
   */
  showWithAction(
    message: string,
    action: string,
    callback?: () => void,
    duration?: number
  ): void {
    const snackBarRef = this.snackBar.open(message, action, {
      ...this.defaultConfig,
      duration: duration || this.defaultConfig.duration
    });

    if (callback) {
      snackBarRef.onAction().subscribe(callback);
    }
  }

  /**
   * Dismiss all notifications
   */
  dismiss(): void {
    this.snackBar.dismiss();
  }
}

