import { Injectable } from '@angular/core';
import { HttpClient, HttpEventType, HttpHeaders } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';
import { environment } from '../../environments/environment';
import { UploadProgress } from '../models/print-job.model';

@Injectable({
  providedIn: 'root'
})
export class UploadService {
  private uploadUrl = environment.uploadUrl;
  private maxFileSize = environment.maxFileSize;
  private supportedFormats = environment.supportedFormats;

  constructor(private http: HttpClient) {}

  /**
   * Upload 3D model file with progress tracking
   */
  uploadModel(file: File, metadata?: any): Observable<UploadProgress> {
    // Validate file first
    const validation = this.validateFile(file);
    if (!validation.valid) {
      const errorSubject = new Subject<UploadProgress>();
      errorSubject.next({
        progress: 0,
        loaded: 0,
        total: 0,
        status: 'failed',
        error: validation.error
      });
      errorSubject.error(new Error(validation.error));
      return errorSubject.asObservable();
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', this.getFileExtension(file.name).substring(1)); // Remove the dot
    
    if (metadata) {
      Object.keys(metadata).forEach(key => {
        formData.append(key, metadata[key]);
      });
    }

    const progressSubject = new Subject<UploadProgress>();

    this.http.post(`${this.uploadUrl}/model`, formData, {
      reportProgress: true,
      observe: 'events'
    }).subscribe({
      next: (event) => {
        if (event.type === HttpEventType.UploadProgress) {
          const progress = Math.round(100 * event.loaded / (event.total || event.loaded));
          progressSubject.next({
            progress,
            loaded: event.loaded,
            total: event.total || 0,
            status: 'uploading'
          });
        } else if (event.type === HttpEventType.Response) {
          progressSubject.next({
            progress: 100,
            loaded: event.body ? 1 : 0,
            total: 1,
            status: 'completed',
            response: event.body
          });
          progressSubject.complete();
        }
      },
      error: (error) => {
        const errorMessage = error.error?.error?.message || error.error?.message || error.message;
        progressSubject.next({
          progress: 0,
          loaded: 0,
          total: 0,
          status: 'failed',
          error: errorMessage
        });
        progressSubject.error(error);
      }
    });

    return progressSubject.asObservable();
  }

  /**
   * Upload image file
   */
  uploadImage(file: File, productId?: string): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    if (productId) {
      formData.append('product_id', productId);
    }

    return this.http.post(`${this.uploadUrl}/image`, formData);
  }

  /**
   * Upload document file
   */
  uploadDocument(file: File, type: string): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);

    return this.http.post(`${this.uploadUrl}/document`, formData);
  }

  /**
   * Get upload status
   */
  getUploadStatus(uploadId: string): Observable<any> {
    return this.http.get(`${this.uploadUrl}/${uploadId}/status`);
  }

  /**
   * Validate file before upload
   */
  validateFile(file: File): { valid: boolean; error?: string } {
    const extension = this.getFileExtension(file.name);
    
    // Check file extension
    if (!this.supportedFormats.includes(extension)) {
      return {
        valid: false,
        error: `Unsupported file format. Supported formats: ${this.supportedFormats.join(', ')}`
      };
    }
    
    // Check file size
    if (file.size > this.maxFileSize) {
      const maxSizeMB = this.maxFileSize / 1024 / 1024;
      return {
        valid: false,
        error: `File size exceeds maximum allowed size of ${maxSizeMB}MB`
      };
    }
    
    // Check if file is empty
    if (file.size === 0) {
      return {
        valid: false,
        error: 'File is empty'
      };
    }
    
    return { valid: true };
  }

  /**
   * Get file extension
   */
  private getFileExtension(filename: string): string {
    return '.' + filename.split('.').pop()?.toLowerCase();
  }

  /**
   * Format file size
   */
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }

  /**
   * Upload file in chunks (for large files)
   */
  uploadInChunks(file: File, chunkSize: number = 5 * 1024 * 1024): Observable<UploadProgress> {
    const totalChunks = Math.ceil(file.size / chunkSize);
    const uploadId = this.generateUploadId();
    const progressSubject = new Subject<UploadProgress>();

    this.uploadChunksSequentially(file, chunkSize, totalChunks, uploadId, 0, progressSubject);

    return progressSubject.asObservable();
  }

  /**
   * Upload chunks sequentially
   */
  private uploadChunksSequentially(
    file: File,
    chunkSize: number,
    totalChunks: number,
    uploadId: string,
    currentChunk: number,
    progressSubject: Subject<UploadProgress>
  ): void {
    if (currentChunk >= totalChunks) {
      progressSubject.next({
        progress: 100,
        loaded: file.size,
        total: file.size,
        status: 'completed'
      });
      progressSubject.complete();
      return;
    }

    const start = currentChunk * chunkSize;
    const end = Math.min(start + chunkSize, file.size);
    const chunk = file.slice(start, end);

    const formData = new FormData();
    formData.append('chunk', chunk);

    this.http.post(`${this.uploadUrl}/chunk`, formData, {
      headers: new HttpHeaders({
        'X-Chunk-Index': currentChunk.toString(),
        'X-Total-Chunks': totalChunks.toString(),
        'X-Upload-ID': uploadId
      })
    }).subscribe({
      next: () => {
        const progress = Math.round(((currentChunk + 1) / totalChunks) * 100);
        progressSubject.next({
          progress,
          loaded: end,
          total: file.size,
          status: 'uploading'
        });
        
        // Upload next chunk
        this.uploadChunksSequentially(
          file,
          chunkSize,
          totalChunks,
          uploadId,
          currentChunk + 1,
          progressSubject
        );
      },
      error: (error) => {
        progressSubject.next({
          progress: 0,
          loaded: 0,
          total: 0,
          status: 'failed',
          error: error.message
        });
        progressSubject.error(error);
      }
    });
  }

  /**
   * Generate unique upload ID
   */
  private generateUploadId(): string {
    return `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

