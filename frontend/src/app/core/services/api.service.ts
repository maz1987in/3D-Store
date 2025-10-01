import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);
  private baseUrl = environment.apiBaseUrl;

  get<T>(path: string, params?: Record<string, string | number | boolean>) {
    const httpParams = new HttpParams({ fromObject: params as any });
    return this.http.get<T>(`${this.baseUrl}${path}`, { params: httpParams });
  }

  post<T>(path: string, body: unknown, headers?: Record<string, string>) {
    const httpHeaders = new HttpHeaders(headers ?? {});
    return this.http.post<T>(`${this.baseUrl}${path}`, body, { headers: httpHeaders });
  }

  put<T>(path: string, body: unknown, headers?: Record<string, string>) {
    const httpHeaders = new HttpHeaders(headers ?? {});
    return this.http.put<T>(`${this.baseUrl}${path}`, body, { headers: httpHeaders });
  }

  delete<T>(path: string, params?: Record<string, string | number | boolean>) {
    const httpParams = new HttpParams({ fromObject: params as any });
    return this.http.delete<T>(`${this.baseUrl}${path}`, { params: httpParams });
  }
}
