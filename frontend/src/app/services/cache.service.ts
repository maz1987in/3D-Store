import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { tap } from 'rxjs/operators';

interface CacheEntry {
  data: any;
  timestamp: number;
  ttl: number;
}

@Injectable({
  providedIn: 'root'
})
export class CacheService {
  private memoryCache = new Map<string, CacheEntry>();
  private defaultTTL = 5 * 60 * 1000; // 5 minutes

  /**
   * Get item from cache
   */
  get<T>(key: string): T | null {
    const entry = this.memoryCache.get(key);
    
    if (!entry) {
      return null;
    }

    // Check if expired
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.memoryCache.delete(key);
      return null;
    }

    return entry.data as T;
  }

  /**
   * Set item in cache
   */
  set(key: string, data: any, ttl?: number): void {
    this.memoryCache.set(key, {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.defaultTTL
    });
  }

  /**
   * Delete item from cache
   */
  delete(key: string): void {
    this.memoryCache.delete(key);
  }

  /**
   * Clear all cache
   */
  clear(): void {
    this.memoryCache.clear();
    localStorage.clear();
  }

  /**
   * Clear expired entries
   */
  clearExpired(): void {
    const now = Date.now();
    
    for (const [key, entry] of this.memoryCache.entries()) {
      if (now - entry.timestamp > entry.ttl) {
        this.memoryCache.delete(key);
      }
    }
  }

  /**
   * Get from localStorage
   */
  getFromLocalStorage<T>(key: string): T | null {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch {
      return null;
    }
  }

  /**
   * Save to localStorage
   */
  saveToLocalStorage(key: string, data: any): void {
    try {
      localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
      console.error('Failed to save to localStorage:', error);
    }
  }

  /**
   * Remove from localStorage
   */
  removeFromLocalStorage(key: string): void {
    localStorage.removeItem(key);
  }

  /**
   * Cache observable result
   */
  cacheObservable<T>(
    key: string,
    observable: Observable<T>,
    ttl?: number
  ): Observable<T> {
    const cached = this.get<T>(key);
    
    if (cached) {
      return of(cached);
    }

    return observable.pipe(
      tap(data => this.set(key, data, ttl))
    );
  }

  /**
   * Get cache statistics
   */
  getStats(): { size: number; keys: string[] } {
    return {
      size: this.memoryCache.size,
      keys: Array.from(this.memoryCache.keys())
    };
  }
}

