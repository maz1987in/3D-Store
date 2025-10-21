import { Injectable } from '@angular/core';
import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

@Injectable({
  providedIn: 'root'
})
export class ValidationService {
  /**
   * Email validator
   */
  emailValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      if (!control.value) {
        return null;
      }

      const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
      return emailRegex.test(control.value) ? null : { invalidEmail: true };
    };
  }

  /**
   * Phone number validator
   */
  phoneValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      if (!control.value) {
        return null;
      }

      const phoneRegex = /^\+?[1-9]\d{7,14}$/;
      return phoneRegex.test(control.value) ? null : { invalidPhone: true };
    };
  }

  /**
   * Password strength validator
   */
  passwordStrengthValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      if (!control.value) {
        return null;
      }

      const password = control.value;
      const errors: ValidationErrors = {};

      if (password.length < 8) {
        errors['minLength'] = true;
      }

      if (!/[A-Z]/.test(password)) {
        errors['noUppercase'] = true;
      }

      if (!/[a-z]/.test(password)) {
        errors['noLowercase'] = true;
      }

      if (!/[0-9]/.test(password)) {
        errors['noNumber'] = true;
      }

      if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        errors['noSpecialChar'] = true;
      }

      return Object.keys(errors).length > 0 ? errors : null;
    };
  }

  /**
   * Password match validator
   */
  passwordMatchValidator(passwordField: string, confirmPasswordField: string): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      const password = control.get(passwordField);
      const confirmPassword = control.get(confirmPasswordField);

      if (!password || !confirmPassword) {
        return null;
      }

      return password.value === confirmPassword.value ? null : { passwordMismatch: true };
    };
  }

  /**
   * File type validator
   */
  fileTypeValidator(allowedTypes: string[]): (file: File) => boolean {
    return (file: File) => {
      const extension = '.' + file.name.split('.').pop()?.toLowerCase();
      return allowedTypes.includes(extension);
    };
  }

  /**
   * File size validator
   */
  fileSizeValidator(maxSize: number): (file: File) => boolean {
    return (file: File) => file.size <= maxSize;
  }

  /**
   * URL validator
   */
  urlValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      if (!control.value) {
        return null;
      }

      try {
        new URL(control.value);
        return null;
      } catch {
        return { invalidUrl: true };
      }
    };
  }

  /**
   * Number range validator
   */
  rangeValidator(min: number, max: number): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      if (!control.value) {
        return null;
      }

      const value = Number(control.value);
      
      if (value < min || value > max) {
        return { outOfRange: { min, max, actual: value } };
      }

      return null;
    };
  }

  /**
   * Get error message
   */
  getErrorMessage(errors: ValidationErrors | null): string {
    if (!errors) {
      return '';
    }

    if (errors['required']) {
      return 'This field is required';
    }

    if (errors['invalidEmail']) {
      return 'Please enter a valid email address';
    }

    if (errors['invalidPhone']) {
      return 'Please enter a valid phone number';
    }

    if (errors['minLength']) {
      return 'Password must be at least 8 characters';
    }

    if (errors['noUppercase']) {
      return 'Password must contain an uppercase letter';
    }

    if (errors['noLowercase']) {
      return 'Password must contain a lowercase letter';
    }

    if (errors['noNumber']) {
      return 'Password must contain a number';
    }

    if (errors['noSpecialChar']) {
      return 'Password must contain a special character';
    }

    if (errors['passwordMismatch']) {
      return 'Passwords do not match';
    }

    if (errors['invalidUrl']) {
      return 'Please enter a valid URL';
    }

    if (errors['outOfRange']) {
      const { min, max } = errors['outOfRange'];
      return `Value must be between ${min} and ${max}`;
    }

    return 'Invalid input';
  }
}

