# Supplier Module

The Supplier module manages supplier relationships, procurement, and supply chain operations in the 3D Store application, providing comprehensive supplier management capabilities.

## Overview

This module handles:
- Supplier registration and management
- Supplier performance tracking
- Procurement and purchase orders
- Supplier quality management
- Supply chain analytics
- Supplier communication and collaboration
- Supplier compliance and certification

## Module Structure

```
supplier/
├── __init__.py          # Module initialization
├── model.py            # SQLAlchemy models
├── routes.py           # Flask API endpoints
├── service.py          # Business logic layer
├── swagger.yaml        # API documentation
└── README.md           # This documentation
```

## Models

### Supplier
Main supplier entity with the following key attributes:
- **Basic Info**: `supplier_id`, `name`, `legal_name`, `supplier_code`
- **Business**: `business_type`, `industry`, `registration_number`, `tax_id`
- **Contact**: `email`, `phone`, `website`, `contact_person`
- **Address**: `business_address`, `shipping_address`, `billing_address`
- **Status**: `is_active`, `is_verified`, `verification_status`
- **Rating**: `quality_rating`, `delivery_rating`, `overall_rating`
- **Metadata**: `created_at`, `updated_at`, `last_activity`

### SupplierCategory
Supplier categorization:
- **Category Info**: `category_id`, `name`, `description`, `parent_id`
- **Requirements**: `minimum_requirements`, `certification_required`
- **Standards**: `quality_standards`, `compliance_requirements`
- **Status**: `is_active`, `sort_order`
- **Metadata**: `created_at`, `updated_at`

### SupplierProduct
Supplier product catalog:
- **Product Info**: `supplier_id`, `product_id`, `supplier_sku`, `supplier_name`
- **Pricing**: `unit_price`, `minimum_order`, `bulk_pricing`
- **Specifications**: `specifications`, `quality_standards`, `certifications`
- **Availability**: `is_available`, `lead_time`, `stock_quantity`
- **Status**: `is_active`, `last_updated`
- **Metadata**: `created_at`, `updated_at`

### SupplierPerformance
Supplier performance tracking:
- **Performance Info**: `supplier_id`, `period`, `total_orders`, `completed_orders`
- **Metrics**: `on_time_delivery`, `quality_score`, `cost_effectiveness`
- **Rating**: `overall_rating`, `performance_trend`, `improvement_areas`
- **Issues**: `quality_issues`, `delivery_issues`, `communication_issues`
- **Metadata**: `calculated_at`, `created_at`

### SupplierContract
Supplier contracts and agreements:
- **Contract Info**: `contract_id`, `supplier_id`, `contract_type`, `status`
- **Terms**: `start_date`, `end_date`, `renewal_terms`, `termination_clause`
- **Pricing**: `pricing_terms`, `payment_terms`, `discount_terms`
- **Quality**: `quality_requirements`, `delivery_terms`, `warranty_terms`
- **Legal**: `legal_terms`, `liability_terms`, `confidentiality_terms`
- **Metadata**: `created_at`, `updated_at`, `signed_by`

### SupplierDocument
Supplier documentation and certifications:
- **Document Info**: `document_id`, `supplier_id`, `document_type`, `title`
- **File**: `file_url`, `file_name`, `file_size`, `mime_type`
- **Validation**: `is_verified`, `verified_by`, `verified_at`, `expiry_date`
- **Status**: `status`, `is_required`, `renewal_required`
- **Metadata**: `created_at`, `updated_at`

## API Endpoints

### Supplier Management
- `GET /suppliers` - List suppliers
- `GET /suppliers/{id}` - Get supplier details
- `POST /suppliers` - Create supplier
- `PUT /suppliers/{id}` - Update supplier
- `DELETE /suppliers/{id}` - Deactivate supplier
- `POST /suppliers/{id}/verify` - Verify supplier

### Supplier Categories
- `GET /suppliers/categories` - List supplier categories
- `GET /suppliers/categories/{id}` - Get category details
- `POST /suppliers/categories` - Create category
- `PUT /suppliers/categories/{id}` - Update category
- `DELETE /suppliers/categories/{id}` - Delete category

### Supplier Products
- `GET /suppliers/{id}/products` - List supplier products
- `GET /suppliers/{id}/products/{product_id}` - Get product details
- `POST /suppliers/{id}/products` - Add product to supplier
- `PUT /suppliers/{id}/products/{product_id}` - Update product
- `DELETE /suppliers/{id}/products/{product_id}` - Remove product

### Supplier Performance
- `GET /suppliers/{id}/performance` - Get supplier performance
- `GET /suppliers/{id}/performance/trends` - Get performance trends
- `POST /suppliers/{id}/performance/rate` - Rate supplier performance
- `GET /suppliers/performance/ranking` - Get supplier rankings
- `GET /suppliers/performance/comparison` - Compare supplier performance

### Supplier Contracts
- `GET /suppliers/{id}/contracts` - List supplier contracts
- `GET /suppliers/{id}/contracts/{contract_id}` - Get contract details
- `POST /suppliers/{id}/contracts` - Create contract
- `PUT /suppliers/{id}/contracts/{contract_id}` - Update contract
- `DELETE /suppliers/{id}/contracts/{contract_id}` - Delete contract

### Supplier Documents
- `GET /suppliers/{id}/documents` - List supplier documents
- `GET /suppliers/{id}/documents/{document_id}` - Get document details
- `POST /suppliers/{id}/documents` - Upload document
- `PUT /suppliers/{id}/documents/{document_id}` - Update document
- `DELETE /suppliers/{id}/documents/{document_id}` - Delete document

### Supplier Analytics
- `GET /suppliers/analytics/overview` - Get supplier overview
- `GET /suppliers/analytics/performance` - Get performance analytics
- `GET /suppliers/analytics/costs` - Get cost analytics
- `GET /suppliers/analytics/trends` - Get supplier trends
- `GET /suppliers/reports` - Generate supplier reports

## Business Logic

### Supplier Registration
1. **Application Review**: Review supplier applications
2. **Verification Process**: Verify supplier information and credentials
3. **Category Assignment**: Assign appropriate supplier categories
4. **Document Collection**: Collect required documents and certifications
5. **Contract Negotiation**: Negotiate terms and conditions
6. **Approval Workflow**: Route through approval process
7. **Onboarding**: Complete supplier onboarding

### Supplier Performance Management
1. **Performance Tracking**: Track supplier performance metrics
2. **Quality Assessment**: Assess supplier quality standards
3. **Delivery Monitoring**: Monitor delivery performance
4. **Cost Analysis**: Analyze supplier costs and pricing
5. **Rating System**: Implement supplier rating system
6. **Improvement Planning**: Plan supplier improvements

### Supplier Product Management
1. **Catalog Management**: Manage supplier product catalogs
2. **Pricing Updates**: Handle pricing updates and changes
3. **Availability Tracking**: Track product availability
4. **Quality Standards**: Ensure quality standards compliance
5. **Specification Management**: Manage product specifications
6. **Competitive Analysis**: Analyze competitive positioning

### Supplier Contract Management
1. **Contract Creation**: Create supplier contracts
2. **Terms Negotiation**: Negotiate contract terms
3. **Renewal Management**: Manage contract renewals
4. **Compliance Monitoring**: Monitor contract compliance
5. **Performance Tracking**: Track contract performance
6. **Dispute Resolution**: Handle contract disputes

### Supplier Communication
1. **Communication Channels**: Manage communication channels
2. **Issue Tracking**: Track and resolve supplier issues
3. **Feedback Management**: Manage supplier feedback
4. **Collaboration Tools**: Provide collaboration tools
5. **Notification System**: Implement notification system
6. **Relationship Management**: Manage supplier relationships

## Validation Schemas

### SupplierCreateSchema
```python
{
    "name": "string (required, max 255 chars)",
    "legal_name": "string (required, max 255 chars)",
    "supplier_code": "string (required, max 50 chars, unique)",
    "business_type": "string (required, enum: manufacturer|distributor|service_provider|consultant)",
    "industry": "string (required, max 100 chars)",
    "registration_number": "string (required, max 100 chars)",
    "tax_id": "string (required, max 100 chars)",
    "email": "string (required, valid email)",
    "phone": "string (required, valid phone number)",
    "website": "string (optional, valid URL)",
    "contact_person": "string (required, max 255 chars)",
    "business_address": {
        "street": "string (required)",
        "city": "string (required)",
        "state": "string (optional)",
        "postal_code": "string (required)",
        "country": "string (required)"
    },
    "shipping_address": {
        "street": "string (required)",
        "city": "string (required)",
        "state": "string (optional)",
        "postal_code": "string (required)",
        "country": "string (required)"
    },
    "billing_address": {
        "street": "string (required)",
        "city": "string (required)",
        "state": "string (optional)",
        "postal_code": "string (required)",
        "country": "string (required)"
    }
}
```

### SupplierUpdateSchema
```python
{
    "name": "string (optional, max 255 chars)",
    "legal_name": "string (optional, max 255 chars)",
    "business_type": "string (optional, enum: manufacturer|distributor|service_provider|consultant)",
    "industry": "string (optional, max 100 chars)",
    "email": "string (optional, valid email)",
    "phone": "string (optional, valid phone number)",
    "website": "string (optional, valid URL)",
    "contact_person": "string (optional, max 255 chars)",
    "business_address": "object (optional)",
    "shipping_address": "object (optional)",
    "billing_address": "object (optional)"
}
```

### SupplierProductCreateSchema
```python
{
    "supplier_id": "uuid (required)",
    "product_id": "uuid (required)",
    "supplier_sku": "string (required, max 100 chars)",
    "supplier_name": "string (required, max 255 chars)",
    "unit_price": "decimal (required, min 0)",
    "minimum_order": "integer (required, min 1)",
    "bulk_pricing": "object (optional)",
    "specifications": "object (optional)",
    "quality_standards": "array of strings (optional)",
    "certifications": "array of strings (optional)",
    "is_available": "boolean (optional, default true)",
    "lead_time": "integer (optional, days)",
    "stock_quantity": "integer (optional, min 0)"
}
```

### SupplierContractCreateSchema
```python
{
    "supplier_id": "uuid (required)",
    "contract_type": "string (required, enum: supply|service|maintenance|consulting)",
    "start_date": "date (required)",
    "end_date": "date (required)",
    "renewal_terms": "string (optional, max 500 chars)",
    "termination_clause": "string (optional, max 1000 chars)",
    "pricing_terms": "object (required)",
    "payment_terms": "string (required, max 500 chars)",
    "discount_terms": "object (optional)",
    "quality_requirements": "object (required)",
    "delivery_terms": "string (required, max 500 chars)",
    "warranty_terms": "string (optional, max 500 chars)",
    "legal_terms": "object (optional)",
    "liability_terms": "string (optional, max 1000 chars)",
    "confidentiality_terms": "string (optional, max 1000 chars)"
}
```

## Error Handling

The module uses comprehensive error handling:
- **ValidationException**: For input validation errors
- **ResourceNotFoundException**: When supplier not found
- **BusinessLogicException**: For business rule violations
- **ContractException**: For contract-related errors
- **PerformanceException**: For performance-related errors

## Dependencies

- **Product Module**: For product information
- **Order Module**: For purchase orders
- **Financial Module**: For cost analysis
- **Analytics Module**: For supplier analytics
- **Document Module**: For document management
- **Notification Module**: For supplier communications

## Usage Examples

### Creating a Supplier
```python
from app.supplier.service import SupplierService
from app.supplier.schemas import SupplierCreateSchema

service = SupplierService()
supplier_data = {
    "name": "3D Materials Co.",
    "legal_name": "3D Materials Company LLC",
    "supplier_code": "3DMC001",
    "business_type": "manufacturer",
    "industry": "3D Printing Materials",
    "registration_number": "REG123456789",
    "tax_id": "TAX987654321",
    "email": "info@3dmaterials.com",
    "phone": "+96812345678",
    "website": "https://3dmaterials.com",
    "contact_person": "Ahmed Al-Rashid",
    "business_address": {
        "street": "123 Industrial Street",
        "city": "Muscat",
        "state": "Muscat",
        "postal_code": "12345",
        "country": "Oman"
    },
    "shipping_address": {
        "street": "123 Industrial Street",
        "city": "Muscat",
        "state": "Muscat",
        "postal_code": "12345",
        "country": "Oman"
    },
    "billing_address": {
        "street": "123 Industrial Street",
        "city": "Muscat",
        "state": "Muscat",
        "postal_code": "12345",
        "country": "Oman"
    }
}

supplier = service.create_supplier(supplier_data)
```

### Managing Supplier Products
```python
# Add product to supplier
product_data = {
    "supplier_id": "supplier-uuid",
    "product_id": "product-uuid",
    "supplier_sku": "PLA-WH-001",
    "supplier_name": "PLA White 1.75mm",
    "unit_price": 25.00,
    "minimum_order": 100,
    "bulk_pricing": {
        "100-499": 23.00,
        "500-999": 21.00,
        "1000+": 19.00
    },
    "specifications": {
        "diameter": "1.75mm",
        "color": "White",
        "material": "PLA",
        "weight": "1kg"
    },
    "quality_standards": ["ISO 9001", "CE"],
    "certifications": ["Food Safe", "Biodegradable"],
    "is_available": True,
    "lead_time": 7,
    "stock_quantity": 1000
}

supplier_product = service.add_supplier_product(product_data)

# Update supplier product
service.update_supplier_product(supplier_id, product_id, {
    "unit_price": 24.00,
    "stock_quantity": 1200
})
```

### Supplier Performance Management
```python
# Rate supplier performance
performance_data = {
    "supplier_id": "supplier-uuid",
    "period": "2024-01",
    "on_time_delivery": 0.95,
    "quality_score": 8.5,
    "cost_effectiveness": 7.8,
    "overall_rating": 8.2,
    "quality_issues": 2,
    "delivery_issues": 1,
    "communication_issues": 0
}

service.rate_supplier_performance(performance_data)

# Get supplier performance
performance = service.get_supplier_performance(supplier_id, period="monthly")

# Get supplier rankings
rankings = service.get_supplier_rankings()
```

### Supplier Contract Management
```python
# Create supplier contract
contract_data = {
    "supplier_id": "supplier-uuid",
    "contract_type": "supply",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "renewal_terms": "Automatic renewal for 1 year",
    "termination_clause": "30 days notice required",
    "pricing_terms": {
        "base_price": 25.00,
        "discount_tiers": {
            "100-499": 0.08,
            "500-999": 0.12,
            "1000+": 0.16
        }
    },
    "payment_terms": "Net 30 days",
    "discount_terms": {
        "early_payment": 0.02,
        "volume_discount": True
    },
    "quality_requirements": {
        "iso_9001": True,
        "ce_certification": True,
        "quality_audit": "Quarterly"
    },
    "delivery_terms": "FOB destination, 7 days lead time",
    "warranty_terms": "12 months from delivery",
    "legal_terms": {
        "governing_law": "Omani Law",
        "dispute_resolution": "Arbitration"
    },
    "liability_terms": "Limited to contract value",
    "confidentiality_terms": "5 years confidentiality period"
}

contract = service.create_supplier_contract(contract_data)

# Update contract
service.update_supplier_contract(supplier_id, contract_id, {
    "end_date": "2025-12-31",
    "payment_terms": "Net 45 days"
})
```

### Supplier Analytics
```python
# Get supplier overview
overview = service.get_supplier_overview()

# Get performance analytics
performance_analytics = service.get_performance_analytics(
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Get cost analytics
cost_analytics = service.get_cost_analytics(period="monthly")

# Generate supplier report
report = service.generate_supplier_report(
    report_type="performance",
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

## Performance Considerations

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Cache frequently accessed supplier data
- **Performance Tracking**: Efficient performance calculation
- **Document Management**: Optimize document storage and retrieval
- **Analytics Processing**: Process analytics in background

## Security

- **Access Control**: Role-based permissions for supplier management
- **Data Privacy**: Protect supplier confidential information
- **Audit Logging**: Log all supplier operations
- **Document Security**: Secure document storage and access
- **Contract Security**: Secure contract management

## Integration Points

- **Procurement Systems**: Integration with procurement platforms
- **ERP Systems**: Enterprise resource planning integration
- **Quality Management**: Quality assurance systems
- **Financial Systems**: Cost and payment integration
- **Analytics Platforms**: Supplier analytics and reporting
- **Communication Tools**: Supplier communication platforms

## Future Enhancements

- **AI-Powered Analytics**: Machine learning supplier insights
- **Predictive Analytics**: Supplier performance prediction
- **Automated Procurement**: Automated procurement processes
- **Blockchain Integration**: Secure contract and document management
- **IoT Integration**: Real-time supplier monitoring
- **Advanced Collaboration**: Enhanced supplier collaboration tools
