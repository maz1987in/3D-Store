# Medias Module

The Medias module manages file uploads, media storage, and file processing in the 3D Store application, providing comprehensive media management capabilities for 3D models, images, and documents.

## Overview

This module handles:
- File upload and storage management
- 3D model file processing and validation
- Image processing and optimization
- File security and access control
- Media metadata management
- File conversion and format support
- CDN integration and delivery

## Module Structure

```
medias/
├── __init__.py          # Module initialization
├── model.py            # SQLAlchemy models
├── routes.py           # Flask API endpoints
├── service.py          # Business logic layer
├── swagger.yaml        # API documentation
└── README.md           # This documentation
```

## Models

### MediaFile
Main media file entity with the following key attributes:
- **Basic Info**: `file_id`, `filename`, `original_filename`, `file_type`
- **Storage**: `file_path`, `storage_provider`, `bucket_name`, `file_size`
- **Metadata**: `mime_type`, `extension`, `dimensions`, `duration`
- **3D Model**: `is_3d_model`, `model_format`, `vertices_count`, `faces_count`
- **Processing**: `processing_status`, `thumbnail_path`, `preview_path`
- **Security**: `is_public`, `access_token`, `expires_at`
- **Metadata**: `created_at`, `updated_at`, `uploaded_by`

### MediaCategory
Media file categorization:
- **Category Info**: `category_id`, `name`, `description`, `parent_id`
- **File Types**: `allowed_extensions`, `max_file_size`, `mime_types`
- **Processing**: `auto_process`, `processing_rules`, `thumbnail_settings`
- **Access**: `is_public`, `requires_auth`, `access_level`
- **Metadata**: `created_at`, `updated_at`

### MediaProcessing
File processing jobs and status:
- **Processing Info**: `job_id`, `file_id`, `processing_type`, `status`
- **Parameters**: `processing_params`, `output_format`, `quality_settings`
- **Progress**: `progress_percentage`, `current_step`, `total_steps`
- **Results**: `output_files`, `error_message`, `processing_time`
- **Timestamps**: `started_at`, `completed_at`, `created_at`

### MediaAccess
File access control and permissions:
- **Access Info**: `file_id`, `user_id`, `access_type`, `permissions`
- **Sharing**: `share_token`, `share_expires`, `share_password`
- **Download**: `download_count`, `last_downloaded`, `download_limit`
- **Metadata**: `created_at`, `updated_at`

### MediaThumbnail
Thumbnail and preview generation:
- **Thumbnail Info**: `file_id`, `thumbnail_type`, `size`, `format`
- **Storage**: `thumbnail_path`, `storage_provider`, `file_size`
- **Dimensions**: `width`, `height`, `aspect_ratio`
- **Quality**: `quality_level`, `compression_ratio`
- **Metadata**: `created_at`, `updated_at`

## API Endpoints

### File Upload
- `POST /medias/upload` - Upload single file
- `POST /medias/upload/multiple` - Upload multiple files
- `POST /medias/upload/3d-model` - Upload 3D model file
- `POST /medias/upload/image` - Upload image file
- `POST /medias/upload/document` - Upload document file

### File Management
- `GET /medias/files` - List media files
- `GET /medias/files/{id}` - Get file details
- `PUT /medias/files/{id}` - Update file metadata
- `DELETE /medias/files/{id}` - Delete file
- `GET /medias/files/{id}/download` - Download file
- `GET /medias/files/{id}/preview` - Get file preview

### File Processing
- `POST /medias/files/{id}/process` - Process file
- `GET /medias/files/{id}/processing/status` - Get processing status
- `POST /medias/files/{id}/convert` - Convert file format
- `POST /medias/files/{id}/generate-thumbnail` - Generate thumbnail
- `POST /medias/files/{id}/optimize` - Optimize file

### 3D Model Processing
- `POST /medias/3d-models/validate` - Validate 3D model
- `POST /medias/3d-models/{id}/repair` - Repair 3D model
- `POST /medias/3d-models/{id}/simplify` - Simplify 3D model
- `GET /medias/3d-models/{id}/preview` - Get 3D model preview
- `POST /medias/3d-models/{id}/generate-gcode` - Generate G-code

### Image Processing
- `POST /medias/images/{id}/resize` - Resize image
- `POST /medias/images/{id}/crop` - Crop image
- `POST /medias/images/{id}/filter` - Apply image filter
- `POST /medias/images/{id}/watermark` - Add watermark
- `POST /medias/images/{id}/compress` - Compress image

### File Sharing
- `POST /medias/files/{id}/share` - Create share link
- `GET /medias/shared/{token}` - Access shared file
- `PUT /medias/files/{id}/share` - Update share settings
- `DELETE /medias/files/{id}/share` - Revoke share link

### Media Categories
- `GET /medias/categories` - List media categories
- `GET /medias/categories/{id}` - Get category details
- `POST /medias/categories` - Create category
- `PUT /medias/categories/{id}` - Update category
- `DELETE /medias/categories/{id}` - Delete category

## Business Logic

### File Upload Process
1. **File Validation**: Validate file type, size, and format
2. **Security Scan**: Scan file for malware and viruses
3. **Storage Selection**: Choose appropriate storage provider
4. **File Processing**: Process file based on type
5. **Metadata Extraction**: Extract file metadata
6. **Thumbnail Generation**: Generate thumbnails and previews
7. **Access Control**: Set appropriate access permissions

### 3D Model Processing
1. **Format Validation**: Validate 3D model format (STL, OBJ, etc.)
2. **Geometry Check**: Check model geometry and topology
3. **Repair Operations**: Repair common model issues
4. **Optimization**: Optimize model for 3D printing
5. **Preview Generation**: Generate 3D preview
6. **G-code Generation**: Generate G-code for printing
7. **Quality Assessment**: Assess printability and quality

### Image Processing
1. **Format Support**: Support various image formats
2. **Resize Operations**: Resize images to different dimensions
3. **Compression**: Compress images for web delivery
4. **Thumbnail Generation**: Generate multiple thumbnail sizes
5. **Watermarking**: Add watermarks for branding
6. **Filter Application**: Apply various image filters
7. **Format Conversion**: Convert between image formats

### File Security
1. **Access Control**: Implement file access permissions
2. **Virus Scanning**: Scan uploaded files for malware
3. **Content Filtering**: Filter inappropriate content
4. **Encryption**: Encrypt sensitive files
5. **Token-based Access**: Use tokens for secure file access
6. **Audit Logging**: Log all file access and modifications

### Storage Management
1. **Multi-provider Support**: Support multiple storage providers
2. **CDN Integration**: Integrate with CDN for fast delivery
3. **Backup Strategy**: Implement file backup and recovery
4. **Storage Optimization**: Optimize storage usage
5. **Lifecycle Management**: Manage file lifecycle and cleanup
6. **Cost Optimization**: Optimize storage costs

## Validation Schemas

### MediaUploadSchema
```python
{
    "file": "file (required)",
    "category_id": "uuid (optional)",
    "is_public": "boolean (optional, default false)",
    "description": "string (optional, max 1000 chars)",
    "tags": "array of strings (optional)",
    "processing_options": {
        "generate_thumbnail": "boolean (optional, default true)",
        "optimize": "boolean (optional, default true)",
        "watermark": "boolean (optional, default false)"
    }
}
```

### Media3DModelSchema
```python
{
    "file": "file (required, 3D model format)",
    "model_format": "string (required, enum: stl|obj|ply|3mf)",
    "processing_options": {
        "repair": "boolean (optional, default true)",
        "simplify": "boolean (optional, default false)",
        "generate_preview": "boolean (optional, default true)",
        "generate_gcode": "boolean (optional, default false)"
    },
    "print_settings": {
        "layer_height": "float (optional, min 0.1, max 0.5)",
        "infill_percentage": "integer (optional, min 0, max 100)",
        "support_enabled": "boolean (optional, default false)"
    }
}
```

### MediaImageSchema
```python
{
    "file": "file (required, image format)",
    "image_format": "string (required, enum: jpg|png|gif|webp)",
    "processing_options": {
        "resize": "object (optional)",
        "crop": "object (optional)",
        "compress": "boolean (optional, default true)",
        "watermark": "boolean (optional, default false)"
    },
    "thumbnail_sizes": "array of objects (optional)"
}
```

### MediaShareSchema
```python
{
    "file_id": "uuid (required)",
    "access_type": "string (required, enum: public|private|password)",
    "expires_at": "datetime (optional)",
    "download_limit": "integer (optional, min 1)",
    "password": "string (optional, min 6 chars)",
    "permissions": "array of strings (optional)"
}
```

## Error Handling

The module uses comprehensive error handling:
- **ValidationException**: For file validation errors
- **FileUploadException**: For upload-related errors
- **ProcessingException**: For file processing errors
- **SecurityException**: For security-related errors
- **StorageException**: For storage-related errors

## Dependencies

- **Storage Providers**: AWS S3, Google Cloud Storage, local storage
- **Image Processing**: PIL, OpenCV, ImageMagick
- **3D Processing**: Open3D, MeshLab, Blender
- **Virus Scanning**: ClamAV, VirusTotal API
- **CDN Services**: CloudFlare, AWS CloudFront
- **File Conversion**: FFmpeg, ImageMagick

## Usage Examples

### Uploading Files
```python
from app.medias.service import MediaService
from app.medias.schemas import MediaUploadSchema

service = MediaService()

# Upload single file
upload_data = {
    "file": file_object,
    "category_id": "category-uuid",
    "is_public": False,
    "description": "Product image",
    "tags": ["product", "3d-printing"],
    "processing_options": {
        "generate_thumbnail": True,
        "optimize": True,
        "watermark": False
    }
}

media_file = service.upload_file(upload_data)
```

### 3D Model Processing
```python
# Upload 3D model
model_data = {
    "file": stl_file,
    "model_format": "stl",
    "processing_options": {
        "repair": True,
        "simplify": False,
        "generate_preview": True,
        "generate_gcode": True
    },
    "print_settings": {
        "layer_height": 0.2,
        "infill_percentage": 20,
        "support_enabled": True
    }
}

model_file = service.upload_3d_model(model_data)

# Process 3D model
processing_result = service.process_3d_model(model_file.id, {
    "repair": True,
    "simplify": True,
    "quality": "high"
})
```

### Image Processing
```python
# Upload image
image_data = {
    "file": image_file,
    "image_format": "jpg",
    "processing_options": {
        "resize": {"width": 800, "height": 600},
        "compress": True,
        "watermark": True
    },
    "thumbnail_sizes": [
        {"width": 150, "height": 150},
        {"width": 300, "height": 300}
    ]
}

image_file = service.upload_image(image_data)

# Process image
processed_image = service.process_image(image_file.id, {
    "resize": {"width": 400, "height": 300},
    "crop": {"x": 0, "y": 0, "width": 400, "height": 300},
    "filter": "sharpen"
})
```

### File Sharing
```python
# Create share link
share_data = {
    "file_id": "file-uuid",
    "access_type": "public",
    "expires_at": "2024-12-31T23:59:59Z",
    "download_limit": 100,
    "permissions": ["view", "download"]
}

share_link = service.create_share_link(share_data)

# Access shared file
shared_file = service.access_shared_file(share_token)
```

### File Management
```python
# Get file details
file_details = service.get_file_details(file_id)

# Update file metadata
service.update_file_metadata(file_id, {
    "description": "Updated description",
    "tags": ["updated", "tags"]
})

# Delete file
service.delete_file(file_id)

# Get file download URL
download_url = service.get_download_url(file_id)
```

## Performance Considerations

- **File Compression**: Compress files for storage and delivery
- **CDN Integration**: Use CDN for fast file delivery
- **Caching**: Cache frequently accessed files
- **Background Processing**: Process files in background
- **Storage Optimization**: Optimize storage usage and costs

## Security

- **File Validation**: Validate all uploaded files
- **Virus Scanning**: Scan files for malware
- **Access Control**: Implement proper access permissions
- **Encryption**: Encrypt sensitive files
- **Audit Logging**: Log all file operations

## Integration Points

- **Storage Providers**: AWS S3, Google Cloud Storage
- **CDN Services**: CloudFlare, AWS CloudFront
- **Image Processing**: PIL, OpenCV, ImageMagick
- **3D Processing**: Open3D, MeshLab, Blender
- **Virus Scanning**: ClamAV, VirusTotal
- **File Conversion**: FFmpeg, ImageMagick

## Future Enhancements

- **AI-Powered Processing**: Machine learning file analysis
- **Real-time Processing**: Live file processing
- **Advanced 3D Tools**: Advanced 3D model manipulation
- **Video Processing**: Video file support and processing
- **Blockchain Storage**: Decentralized file storage
- **AR/VR Support**: Augmented and virtual reality file support
