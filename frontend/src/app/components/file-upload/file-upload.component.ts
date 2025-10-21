import { Component, Input, Output, EventEmitter, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../../shared/material.module';
import { UploadService } from '../../services/upload.service';
import { UploadProgress } from '../../models/print-job.model';

interface FileUploadItem {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'completed' | 'failed';
  error?: string;
  response?: any;
}

@Component({
  selector: 'app-file-upload',
  standalone: true,
  imports: [CommonModule, MaterialModule],
  template: `
    <div 
      class="file-upload-container"
      [class.drag-over]="isDragging"
      (dragover)="onDragOver($event)"
      (dragleave)="onDragLeave($event)"
      (drop)="onDrop($event)">
      
      <!-- Upload Area -->
      <div class="upload-area" (click)="fileInput.click()">
        <mat-icon class="upload-icon">cloud_upload</mat-icon>
        <h3>Drag & Drop Files Here</h3>
        <p>or click to browse</p>
        <p class="file-info">
          Supported formats: {{ accept }}
          <br>
          Max file size: {{ formatFileSize(maxSize) }}
        </p>
        
        <input 
          #fileInput
          type="file" 
          [accept]="accept"
          [multiple]="multiple"
          (change)="onFileSelected($event)"
          style="display: none;">
      </div>

      <!-- File List -->
      @if (uploadQueue.length > 0) {
        <div class="file-list">
          <h4>Files ({{ uploadQueue.length }})</h4>
          
          @for (item of uploadQueue; track item.file.name) {
            <mat-card class="file-item" [class.uploading]="item.status === 'uploading'">
              <div class="file-info-row">
                <div class="file-details">
                  <mat-icon class="file-icon">{{ getFileIcon(item.file.name) }}</mat-icon>
                  <div>
                    <p class="file-name">{{ item.file.name }}</p>
                    <p class="file-size">{{ formatFileSize(item.file.size) }}</p>
                  </div>
                </div>
                
                <div class="file-status">
                  @if (item.status === 'pending') {
                    <mat-chip>Pending</mat-chip>
                  } @else if (item.status === 'uploading') {
                    <mat-chip color="primary">Uploading</mat-chip>
                  } @else if (item.status === 'completed') {
                    <mat-chip color="accent">
                      <mat-icon>check_circle</mat-icon>
                      Completed
                    </mat-chip>
                  } @else if (item.status === 'failed') {
                    <mat-chip color="warn">
                      <mat-icon>error</mat-icon>
                      Failed
                    </mat-chip>
                  }
                  
                  @if (item.status !== 'completed') {
                    <button 
                      mat-icon-button 
                      (click)="removeFile(item)"
                      matTooltip="Remove">
                      <mat-icon>close</mat-icon>
                    </button>
                  }
                </div>
              </div>
              
              <!-- Progress Bar -->
              @if (item.status === 'uploading') {
                <mat-progress-bar 
                  mode="determinate" 
                  [value]="item.progress"
                  color="primary">
                </mat-progress-bar>
                <p class="progress-text">{{ item.progress }}%</p>
              }
              
              <!-- Error Message -->
              @if (item.error) {
                <div class="error-message">
                  <mat-icon>error</mat-icon>
                  <span>{{ item.error }}</span>
                </div>
              }
            </mat-card>
          }
        </div>
        
        <!-- Upload Actions -->
        @if (hasP endingFiles()) {
          <div class="upload-actions">
            <button 
              mat-raised-button 
              color="primary"
              (click)="uploadAll()"
              [disabled]="isUploading">
              <mat-icon>upload</mat-icon>
              Upload All
            </button>
            
            <button 
              mat-button 
              (click)="clearAll()"
              [disabled]="isUploading">
              <mat-icon>clear_all</mat-icon>
              Clear All
            </button>
          </div>
        }
      }
    </div>
  `,
  styles: [`
    .file-upload-container {
      border: 2px dashed #ddd;
      border-radius: 8px;
      padding: 2rem;
      transition: all 0.3s;
      
      &.drag-over {
        border-color: #3f51b5;
        background: #f5f7ff;
        transform: scale(1.02);
      }
    }

    .upload-area {
      text-align: center;
      padding: 2rem;
      cursor: pointer;
      transition: background 0.2s;
      border-radius: 4px;
      
      &:hover {
        background: #f5f5f5;
      }
      
      .upload-icon {
        font-size: 64px;
        width: 64px;
        height: 64px;
        color: #3f51b5;
        margin-bottom: 1rem;
      }
      
      h3 {
        margin: 0 0 0.5rem;
        font-size: 1.25rem;
      }
      
      p {
        margin: 0.25rem 0;
        color: #666;
      }
      
      .file-info {
        font-size: 0.875rem;
        margin-top: 1rem;
        color: #999;
      }
    }

    .file-list {
      margin-top: 2rem;
      
      h4 {
        margin: 0 0 1rem;
      }
      
      .file-item {
        margin-bottom: 1rem;
        padding: 1rem;
        
        &.uploading {
          border-left: 4px solid #3f51b5;
        }
        
        .file-info-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }
        
        .file-details {
          display: flex;
          align-items: center;
          gap: 1rem;
          flex: 1;
          
          .file-icon {
            font-size: 36px;
            width: 36px;
            height: 36px;
            color: #3f51b5;
          }
          
          .file-name {
            margin: 0;
            font-weight: 600;
            word-break: break-word;
          }
          
          .file-size {
            margin: 0;
            font-size: 0.875rem;
            color: #666;
          }
        }
        
        .file-status {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          
          mat-chip mat-icon {
            font-size: 16px;
            width: 16px;
            height: 16px;
            margin-right: 0.25rem;
          }
        }
        
        .progress-text {
          text-align: right;
          margin: 0.5rem 0 0;
          font-size: 0.875rem;
          color: #666;
        }
        
        .error-message {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem;
          background: #ffebee;
          border-radius: 4px;
          color: #c62828;
          margin-top: 0.5rem;
          
          mat-icon {
            font-size: 18px;
            width: 18px;
            height: 18px;
          }
        }
      }
    }

    .upload-actions {
      display: flex;
      gap: 1rem;
      margin-top: 1.5rem;
      justify-content: center;
      
      button mat-icon {
        margin-right: 0.5rem;
      }
    }
  `]
})
export class FileUploadComponent {
  @Input() accept: string = '.stl,.obj,.3mf';
  @Input() maxSize: number = 104857600; // 100MB
  @Input() multiple: boolean = false;
  @Output() filesSelected = new EventEmitter<File[]>();
  @Output() uploadProgress = new EventEmitter<UploadProgress>();
  @Output() uploadComplete = new EventEmitter<any>();
  @Output() uploadError = new EventEmitter<string>();

  uploadQueue: FileUploadItem[] = [];
  isDragging = false;
  isUploading = false;

  constructor(private uploadService: UploadService) {}

  @HostListener('dragover', ['$event'])
  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = true;
  }

  @HostListener('dragleave', ['$event'])
  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;
  }

  @HostListener('drop', ['$event'])
  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;

    const files = event.dataTransfer?.files;
    if (files) {
      this.handleFiles(Array.from(files));
    }
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      this.handleFiles(Array.from(input.files));
      input.value = ''; // Reset input
    }
  }

  handleFiles(files: File[]): void {
    const validFiles: File[] = [];

    files.forEach(file => {
      const validation = this.uploadService.validateFile(file);
      
      if (validation.valid) {
        this.uploadQueue.push({
          file,
          progress: 0,
          status: 'pending'
        });
        validFiles.push(file);
      } else {
        this.uploadQueue.push({
          file,
          progress: 0,
          status: 'failed',
          error: validation.error
        });
      }
    });

    if (validFiles.length > 0) {
      this.filesSelected.emit(validFiles);
    }
  }

  uploadAll(): void {
    const pendingFiles = this.uploadQueue.filter(item => item.status === 'pending');
    
    if (pendingFiles.length === 0) return;
    
    this.isUploading = true;

    pendingFiles.forEach(item => {
      item.status = 'uploading';
      
      this.uploadService.uploadModel(item.file).subscribe({
        next: (progress) => {
          item.progress = progress.progress;
          
          if (progress.status === 'completed') {
            item.status = 'completed';
            item.response = progress.response;
            this.uploadComplete.emit(progress.response);
            this.checkUploadComplete();
          }
          
          this.uploadProgress.emit(progress);
        },
        error: (error) => {
          item.status = 'failed';
          item.error = error.message;
          this.uploadError.emit(error.message);
          this.checkUploadComplete();
        }
      });
    });
  }

  removeFile(item: FileUploadItem): void {
    this.uploadQueue = this.uploadQueue.filter(i => i !== item);
  }

  clearAll(): void {
    this.uploadQueue = [];
    this.isUploading = false;
  }

  hasPendingFiles(): boolean {
    return this.uploadQueue.some(item => item.status === 'pending');
  }

  private checkUploadComplete(): void {
    const stillUploading = this.uploadQueue.some(item => item.status === 'uploading');
    if (!stillUploading) {
      this.isUploading = false;
    }
  }

  formatFileSize(bytes: number): string {
    return this.uploadService.formatFileSize(bytes);
  }

  getFileIcon(filename: string): string {
    const ext = filename.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'stl':
      case 'obj':
      case '3mf':
        return 'view_in_ar';
      default:
        return 'insert_drive_file';
    }
  }
}

