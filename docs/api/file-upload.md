# 3D Model File Upload Specifications

This document provides comprehensive information about uploading 3D model files to the 3D Store API, including supported formats, validation, size limits, and best practices.

## Overview

The 3D Store API supports uploading 3D model files for custom printing services. The system validates files, processes them, and generates previews for customer review.

### Supported File Formats

| Format | Extension | Description | Max Size |
|--------|-----------|-------------|----------|
| **STL** | `.stl` | Stereolithography (most common) | 100MB |
| **OBJ** | `.obj` | Wavefront Object | 100MB |
| **3MF** | `.3mf` | 3D Manufacturing Format | 100MB |

---

## Upload Endpoints

### Upload 3D Model File

**Endpoint**: `POST /3dstore/api/v1/upload/model`

**Description**: Upload a 3D model file for print job creation.

**Headers**:
```
x-access-tokens: <jwt_token>
Content-Type: multipart/form-data
```

**Request (Multipart Form Data)**:
```
file: <3d_model_file>
type: "stl" | "obj" | "3mf"
name: "optional_file_name"
description: "optional_description"
```

**cURL Example**:
```bash
curl -X POST http://localhost:5000/3dstore/api/v1/upload/model \
  -H "x-access-tokens: your_jwt_token" \
  -F "file=@/path/to/model.stl" \
  -F "type=stl" \
  -F "name=My Custom Model"
```

**Response** (200 OK):
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "model_1706784000.stl",
    "original_filename": "my_model.stl",
    "type": "stl",
    "size": 15728640,
    "url": "https://s3.amazonaws.com/3dstore/models/model_1706784000.stl",
    "preview_url": "https://s3.amazonaws.com/3dstore/previews/model_1706784000.png",
    "upload_date": "2025-01-21T10:30:00Z",
    "status": "processing",
    "metadata": {
      "vertices": 50000,
      "triangles": 100000,
      "dimensions": {
        "width": 100.5,
        "height": 75.2,
        "depth": 50.8
      },
      "volume": 382650.5,
      "surface_area": 25000.3
    }
  },
  "message": "File uploaded successfully",
  "status": 200
}
```

**Error Responses**:
- `400 Bad Request` - Invalid file format or missing file
- `413 Payload Too Large` - File size exceeds limit
- `422 Unprocessable Entity` - File validation failed
- `500 Internal Server Error` - Server error during upload

---

### Get Upload Status

**Endpoint**: `GET /3dstore/api/v1/upload/{upload_id}/status`

**Description**: Check the processing status of an uploaded file.

**Response** (200 OK):
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "progress": 100,
    "message": "File processing complete",
    "preview_url": "https://s3.amazonaws.com/3dstore/previews/model_1706784000.png"
  },
  "message": "Success",
  "status": 200
}
```

**Status Values**:
- `uploading` - File is being uploaded
- `processing` - File is being processed
- `completed` - Processing complete
- `failed` - Processing failed

---

### Upload Product Image

**Endpoint**: `POST /3dstore/api/v1/upload/image`

**Description**: Upload product images.

**Supported Formats**: JPG, PNG, WebP

**Max Size**: 10MB

**Request (Multipart Form Data)**:
```
file: <image_file>
product_id: "550e8400-e29b-41d4-a716-446655440000"
```

**Response** (200 OK):
```json
{
  "data": {
    "id": "image_id",
    "url": "https://s3.amazonaws.com/3dstore/images/product_image.jpg",
    "thumbnail_url": "https://s3.amazonaws.com/3dstore/thumbnails/product_image.jpg"
  },
  "message": "Image uploaded successfully",
  "status": 200
}
```

---

### Upload Document

**Endpoint**: `POST /3dstore/api/v1/upload/document`

**Description**: Upload documents (receipts, invoices, agreements).

**Supported Formats**: PDF, DOC, DOCX

**Max Size**: 5MB

**Request (Multipart Form Data)**:
```
file: <document_file>
type: "receipt" | "invoice" | "agreement"
```

**Response** (200 OK):
```json
{
  "data": {
    "id": "document_id",
    "filename": "receipt.pdf",
    "url": "https://s3.amazonaws.com/3dstore/documents/receipt.pdf",
    "type": "receipt",
    "size": 524288
  },
  "message": "Document uploaded successfully",
  "status": 200
}
```

---

## File Validation

### Client-Side Validation

Before uploading, validate files on the client side:

```typescript
// Angular Service
export class FileValidationService {
  // Supported formats
  private supportedFormats = ['.stl', '.obj', '.3mf'];
  private maxFileSize = 104857600; // 100MB in bytes

  /**
   * Validate 3D model file
   */
  validateFile(file: File): { valid: boolean; error?: string } {
    // Check file extension
    const extension = this.getFileExtension(file.name);
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

  private getFileExtension(filename: string): string {
    return '.' + filename.split('.').pop()?.toLowerCase();
  }
}
```

### Server-Side Validation

The server performs additional validation:

1. **File Type Verification**: Verifies actual file type (not just extension)
2. **Malware Scan**: Scans files for malicious content
3. **Model Integrity**: Validates 3D model structure
4. **Size Limits**: Enforces file size limits
5. **Format Validation**: Ensures file matches declared format

**Validation Rules**:

```python
# Backend validation (Python)
ALLOWED_EXTENSIONS = {'.stl', '.obj', '.3mf'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

def validate_model_file(file):
    # Check file extension
    filename = file.filename.lower()
    ext = os.path.splitext(filename)[1]
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"Unsupported file type: {ext}")
    
    # Check file size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        raise ValidationError("File too large")
    
    # Validate file content
    if not is_valid_model_file(file, ext):
        raise ValidationError("Invalid file content")
    
    return True
```

---

## Upload Progress Tracking

### Frontend Implementation

Track upload progress in Angular:

```typescript
import { HttpClient, HttpEventType } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class UploadService {
  constructor(private http: HttpClient) {}

  /**
   * Upload file with progress tracking
   */
  uploadFile(file: File): Observable<UploadProgress> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', this.getFileExtension(file.name));

    const progressSubject = new Subject<UploadProgress>();

    this.http.post(`${environment.apiUrl}/upload/model`, formData, {
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
            loaded: event.body,
            total: 100,
            status: 'completed',
            response: event.body
          });
          progressSubject.complete();
        }
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

    return progressSubject.asObservable();
  }

  private getFileExtension(filename: string): string {
    return filename.split('.').pop()?.toLowerCase() || '';
  }
}

export interface UploadProgress {
  progress: number;
  loaded: number;
  total: number;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  response?: any;
  error?: string;
}
```

### Component Usage

```typescript
export class FileUploadComponent {
  uploadProgress$ = new Subject<UploadProgress>();

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    
    if (!file) return;

    // Validate file
    const validation = this.validationService.validateFile(file);
    if (!validation.valid) {
      this.showError(validation.error);
      return;
    }

    // Upload file
    this.uploadService.uploadFile(file).subscribe({
      next: (progress) => {
        this.uploadProgress$.next(progress);
        
        if (progress.status === 'completed') {
          this.onUploadComplete(progress.response);
        }
      },
      error: (error) => {
        this.showError(error.message);
      }
    });
  }
}
```

---

## Chunked Upload

For large files, use chunked upload:

### Chunked Upload Endpoint

**Endpoint**: `POST /3dstore/api/v1/upload/chunk`

**Description**: Upload file in chunks for large files.

**Request Headers**:
```
x-access-tokens: <jwt_token>
Content-Type: multipart/form-data
X-Chunk-Index: 0
X-Total-Chunks: 10
X-Upload-ID: unique_upload_id
```

**Request Body**:
```
chunk: <file_chunk>
```

**Response** (200 OK):
```json
{
  "data": {
    "upload_id": "unique_upload_id",
    "chunk_index": 0,
    "total_chunks": 10,
    "uploaded_chunks": 1,
    "completed": false
  },
  "message": "Chunk uploaded successfully",
  "status": 200
}
```

**Final Chunk Response** (200 OK):
```json
{
  "data": {
    "upload_id": "unique_upload_id",
    "file_id": "550e8400-e29b-41d4-a716-446655440000",
    "url": "https://s3.amazonaws.com/3dstore/models/model.stl",
    "completed": true
  },
  "message": "Upload completed",
  "status": 200
}
```

### Frontend Chunked Upload

```typescript
async uploadLargeFile(file: File): Promise<void> {
  const chunkSize = 1024 * 1024 * 5; // 5MB chunks
  const totalChunks = Math.ceil(file.size / chunkSize);
  const uploadId = this.generateUploadId();

  for (let i = 0; i < totalChunks; i++) {
    const start = i * chunkSize;
    const end = Math.min(start + chunkSize, file.size);
    const chunk = file.slice(start, end);

    await this.uploadChunk(chunk, i, totalChunks, uploadId);
    
    const progress = Math.round(((i + 1) / totalChunks) * 100);
    this.uploadProgress$.next({ progress, status: 'uploading' });
  }
}

private uploadChunk(chunk: Blob, index: number, total: number, uploadId: string): Promise<any> {
  const formData = new FormData();
  formData.append('chunk', chunk);

  return this.http.post(`${environment.apiUrl}/upload/chunk`, formData, {
    headers: {
      'X-Chunk-Index': index.toString(),
      'X-Total-Chunks': total.toString(),
      'X-Upload-ID': uploadId
    }
  }).toPromise();
}
```

---

## File Processing

After upload, files are processed asynchronously:

### Processing Steps

1. **Validation**: Verify file integrity
2. **Analysis**: Extract model metadata
3. **Preview Generation**: Create 2D preview image
4. **Optimization**: Optimize model if needed
5. **Storage**: Move to permanent storage
6. **Notification**: Notify user of completion

### Processing Status

Check processing status:

```typescript
pollUploadStatus(uploadId: string): Observable<UploadStatus> {
  return interval(2000).pipe(
    switchMap(() => this.http.get<UploadStatus>(
      `${environment.apiUrl}/upload/${uploadId}/status`
    )),
    takeWhile(status => status.status !== 'completed' && status.status !== 'failed', true)
  );
}
```

---

## File Metadata

### Model Metadata

After processing, the following metadata is available:

```json
{
  "metadata": {
    "vertices": 50000,
    "triangles": 100000,
    "dimensions": {
      "width": 100.5,
      "height": 75.2,
      "depth": 50.8,
      "unit": "mm"
    },
    "volume": 382650.5,
    "surface_area": 25000.3,
    "bounding_box": {
      "min": { "x": 0, "y": 0, "z": 0 },
      "max": { "x": 100.5, "y": 75.2, "z": 50.8 }
    },
    "manifold": true,
    "watertight": true,
    "self_intersecting": false
  }
}
```

### Retrieving Metadata

**Endpoint**: `GET /3dstore/api/v1/upload/{upload_id}/metadata`

**Response**:
```json
{
  "data": {
    "metadata": { /* metadata object */ }
  },
  "message": "Success",
  "status": 200
}
```

---

## Error Handling

### Common Upload Errors

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `FILE_TOO_LARGE` | File exceeds size limit | Reduce file size or use chunked upload |
| `INVALID_FORMAT` | Unsupported file format | Use STL, OBJ, or 3MF format |
| `CORRUPT_FILE` | File is corrupted | Re-export model from 3D software |
| `INVALID_MODEL` | Model has errors | Repair model in 3D software |
| `UPLOAD_FAILED` | Upload failed | Retry upload |
| `PROCESSING_FAILED` | Processing failed | Check model integrity |

### Error Response Example

```json
{
  "error": {
    "code": "INVALID_MODEL",
    "message": "Model contains non-manifold edges",
    "details": {
      "issues": [
        "Non-manifold edges detected",
        "Model is not watertight"
      ]
    }
  },
  "status": 422
}
```

---

## Best Practices

### 1. File Preparation

Before uploading:
- **Export correctly**: Use "Export as STL/OBJ" from 3D software
- **Check scale**: Ensure model is in correct units (mm)
- **Repair model**: Fix errors using mesh repair tools
- **Optimize**: Reduce unnecessary vertices/triangles
- **Test**: Preview model in 3D viewer before uploading

### 2. Upload Optimization

- **Compress files**: Use appropriate compression
- **Chunked upload**: For files > 50MB
- **Progress tracking**: Show upload progress to users
- **Error recovery**: Implement retry logic
- **Validate first**: Validate before uploading

### 3. User Experience

- **Show preview**: Display 3D preview after upload
- **Provide feedback**: Show upload and processing status
- **Error messages**: Display clear error messages
- **Help**: Provide help for common issues
- **Examples**: Show example models

### 4. Security

- **Validate file type**: Check actual file content, not just extension
- **Scan for malware**: Scan all uploaded files
- **Size limits**: Enforce file size limits
- **Rate limiting**: Limit upload frequency
- **Authentication**: Require authentication for uploads

---

## Testing File Upload

### Using cURL

```bash
# Upload STL file
curl -X POST http://localhost:5000/3dstore/api/v1/upload/model \
  -H "x-access-tokens: your_token_here" \
  -F "file=@model.stl" \
  -F "type=stl" \
  -F "name=Test Model"

# Check upload status
curl -X GET http://localhost:5000/3dstore/api/v1/upload/upload_id/status \
  -H "x-access-tokens: your_token_here"
```

### Using Postman

1. Set method to **POST**
2. URL: `http://localhost:5000/3dstore/api/v1/upload/model`
3. Headers: `x-access-tokens: your_token_here`
4. Body: Select "form-data"
   - Key: `file`, Type: File, Value: Select file
   - Key: `type`, Type: Text, Value: `stl`
5. Send request

---

## File Storage

### Storage Locations

- **Development**: Local file system
- **Production**: AWS S3 or similar cloud storage

### S3 Configuration

```python
# Backend configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET', '3dstore-files')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
```

### File URLs

**Format**: `https://s3.amazonaws.com/{bucket}/{folder}/{filename}`

**Example**: `https://s3.amazonaws.com/3dstore-files/models/model_1706784000.stl`

---

## Additional Resources

- [STL Format Specification](https://en.wikipedia.org/wiki/STL_(file_format))
- [OBJ Format Specification](https://en.wikipedia.org/wiki/Wavefront_.obj_file)
- [3MF Format Specification](https://3mf.io/specification/)
- [Mesh Repair Tools](https://www.meshlab.net/)

---

**Last Updated**: January 2025  
**Version**: 1.0.0

