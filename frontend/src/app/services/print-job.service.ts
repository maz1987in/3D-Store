import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../core/services/api.service';
import { UploadService } from './upload.service';
import {
  PrintJob,
  CreatePrintJobRequest,
  PrintJobEstimate,
  PrintQueue,
  PrintJobStatus
} from '../models/print-job.model';
import { PaginatedResponse } from '../models/common.model';

@Injectable({
  providedIn: 'root'
})
export class PrintJobService {
  constructor(
    private api: ApiService,
    private uploadService: UploadService
  ) {}

  /**
   * Create new print job
   */
  createPrintJob(request: CreatePrintJobRequest): Observable<PrintJob> {
    // First upload the model file
    return new Observable(observer => {
      this.uploadService.uploadModel(request.model_file, {
        material_id: request.material_id,
        quality: request.quality,
        quantity: request.quantity,
        packaging_id: request.packaging_id,
        notes: request.notes
      }).subscribe({
        next: (progress) => {
          if (progress.status === 'completed' && progress.response) {
            // Create print job with uploaded file
            this.api.post<PrintJob>('print-jobs', {
              model_file_id: progress.response.id,
              model_type: request.model_type,
              material_id: request.material_id,
              quality: request.quality,
              quantity: request.quantity,
              packaging_id: request.packaging_id,
              notes: request.notes
            }).subscribe({
              next: (printJob) => {
                observer.next(printJob);
                observer.complete();
              },
              error: (error) => observer.error(error)
            });
          }
        },
        error: (error) => observer.error(error)
      });
    });
  }

  /**
   * Get print job by ID
   */
  getPrintJob(id: string): Observable<PrintJob> {
    return this.api.get<PrintJob>(`print-jobs/${id}`);
  }

  /**
   * Get user's print jobs
   */
  getUserPrintJobs(params?: {
    page?: number;
    limit?: number;
    status?: PrintJobStatus;
  }): Observable<PaginatedResponse<PrintJob>> {
    return this.api.getPaginated<PrintJob>('print-jobs', params);
  }

  /**
   * Get print job estimate
   */
  getPrintJobEstimate(data: {
    material_id: string;
    quality: string;
    quantity: number;
    model_volume?: number;
  }): Observable<PrintJobEstimate> {
    return this.api.post<PrintJobEstimate>('print-jobs/estimate', data);
  }

  /**
   * Get print queue
   */
  getPrintQueue(): Observable<PrintQueue> {
    return this.api.get<PrintQueue>('print-jobs/queue');
  }

  /**
   * Cancel print job
   */
  cancelPrintJob(id: string, reason?: string): Observable<PrintJob> {
    return this.api.put<PrintJob>(`print-jobs/${id}/cancel`, { reason });
  }

  /**
   * Get print job history
   */
  getPrintJobHistory(params?: {
    page?: number;
    limit?: number;
  }): Observable<PaginatedResponse<PrintJob>> {
    return this.api.getPaginated<PrintJob>('print-jobs/history', params);
  }

  /**
   * Update print job status (admin/staff only)
   */
  updatePrintJobStatus(id: string, status: PrintJobStatus, notes?: string): Observable<PrintJob> {
    return this.api.put<PrintJob>(`print-jobs/${id}/status`, { status, notes });
  }

  /**
   * Get all print jobs (admin/staff only)
   */
  getAllPrintJobs(params?: {
    page?: number;
    limit?: number;
    status?: PrintJobStatus;
    priority?: string;
  }): Observable<PaginatedResponse<PrintJob>> {
    return this.api.getPaginated<PrintJob>('admin/print-jobs', params);
  }

  /**
   * Assign print job to printer (admin/staff only)
   */
  assignToPrinter(jobId: string, printerId: string): Observable<PrintJob> {
    return this.api.put<PrintJob>(`admin/print-jobs/${jobId}/assign`, { printer_id: printerId });
  }

  /**
   * Update print job progress (admin/staff only)
   */
  updateProgress(id: string, progress: number, notes?: string): Observable<PrintJob> {
    return this.api.put<PrintJob>(`admin/print-jobs/${id}/progress`, { progress, notes });
  }
}

