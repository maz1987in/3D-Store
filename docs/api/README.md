# API Documentation

This document provides comprehensive information about the 3D Store REST API endpoints and integration guidelines.

## 🚀 Base URL

```
Development: http://localhost:5000/3dstore/api/v1/
Production: https://api.3dstore.com/3dstore/api/v1/
```

## 🔐 Authentication

All API endpoints require JWT authentication. Include the token in the request header:

```http
x-access-tokens: your_jwt_token_here
```

### Getting a Token

```http
POST /3dstore/api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "role": "customer"
    }
  },
  "message": "Login successful",
  "status": 200
}
```

## 📚 API Endpoints

### Products

#### Get All Products
```http
GET /3dstore/api/v1/products/
```

#### Get Product by ID
```http
GET /3dstore/api/v1/products/{id}
```

#### Create Product
```http
POST /3dstore/api/v1/products/
Content-Type: application/json

{
  "name": "Custom 3D Print",
  "description": "High quality 3D printing service",
  "price": 25.99,
  "category_id": 1,
  "material_id": 1
}
```

### Print Jobs

#### Create Print Job
```http
POST /3dstore/api/v1/print-jobs/
Content-Type: multipart/form-data

{
  "model_file": <file>,
  "material_id": 1,
  "quality": "high",
  "packaging_id": 1,
  "quantity": 1
}
```

#### Get Print Job Status
```http
GET /3dstore/api/v1/print-jobs/{id}
```

#### Update Print Job
```http
PUT /3dstore/api/v1/print-jobs/{id}
Content-Type: application/json

{
  "status": "printing",
  "progress": 45
}
```

### Orders

#### Create Order
```http
POST /3dstore/api/v1/orders/
Content-Type: application/json

{
  "items": [
    {
      "type": "print_job",
      "print_job_id": 1,
      "quantity": 1
    }
  ],
  "shipping_address": {
    "street": "123 Main St",
    "city": "New York",
    "zip_code": "10001"
  }
}
```

#### Get User Orders
```http
GET /3dstore/api/v1/orders/
```

### File Upload

#### Upload 3D Model
```http
POST /3dstore/api/v1/upload/model/
Content-Type: multipart/form-data

{
  "file": <3d_model_file>,
  "type": "stl"
}
```

**Supported Formats:**
- STL (.stl)
- OBJ (.obj)
- 3MF (.3mf)

### Sellers

#### Get Seller Dashboard
```http
GET /3dstore/api/v1/sellers/dashboard/
```

#### Get Commission History
```http
GET /3dstore/api/v1/sellers/commissions/
```

### Expenses

#### Create Expense
```http
POST /3dstore/api/v1/expenses/
Content-Type: application/json

{
  "amount": 150.00,
  "category": "equipment",
  "description": "New 3D printer nozzle",
  "vendor": "Printer Parts Co",
  "receipt": <file>
}
```

#### Get Expenses
```http
GET /3dstore/api/v1/expenses/
```

## 📊 Response Format

All API responses follow this standard format:

### Success Response
```json
{
  "data": {
    // Response data
  },
  "message": "Success",
  "status": 200
}
```

### Error Response
```json
{
  "error": {
    "message": "Error description",
    "code": "ERROR_CODE"
  },
  "status": 400
}
```

## 🔍 Query Parameters

### Pagination
```http
GET /3dstore/api/v1/products/?page=1&limit=10
```

### Filtering
```http
GET /3dstore/api/v1/products/?category=prototyping&material=pla
```

### Sorting
```http
GET /3dstore/api/v1/products/?sort=price&order=asc
```

## 📁 File Upload

### 3D Model Files
- **Max Size**: 100MB
- **Formats**: STL, OBJ, 3MF
- **Validation**: Automatic mesh validation

### Images
- **Max Size**: 10MB
- **Formats**: JPG, PNG, WebP
- **Dimensions**: Auto-resize to 1920x1080

### Documents
- **Max Size**: 5MB
- **Formats**: PDF, DOC, DOCX

## 🔄 WebSocket Events

Real-time updates for print jobs:

```javascript
const ws = new WebSocket('ws://localhost:5000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'print_progress':
      updatePrintProgress(data.job_id, data.progress);
      break;
    case 'print_completed':
      notifyPrintCompleted(data.job_id);
      break;
    case 'print_failed':
      notifyPrintFailed(data.job_id, data.error);
      break;
  }
};
```

## 🚨 Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

## 📝 Rate Limiting

- **General API**: 1000 requests per hour
- **File Upload**: 10 requests per hour
- **Authentication**: 5 attempts per minute

## 🔧 Testing

### Using cURL

```bash
# Login
curl -X POST http://localhost:5000/3dstore/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Get products
curl -X GET http://localhost:5000/3dstore/api/v1/products/ \
  -H "x-access-tokens: your_token_here"
```

### Using Postman

Import the API collection from `docs/api/postman-collection.json`

## 📚 Interactive Documentation

Visit the Swagger UI at:
- **Development**: http://localhost:5000/api/docs
- **Production**: https://api.3dstore.com/api/docs

## 🔗 SDKs and Libraries

### JavaScript/TypeScript
```bash
npm install @3dstore/api-client
```

### Python
```bash
pip install 3dstore-api-client
```

## 📞 Support

For API-related questions:
- Check the Swagger documentation
- Review the error codes
- Create an issue in the repository
