import uuid
import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from depot.fields.sqlalchemy import UploadedFileField
from sqlalchemy.orm import backref, relationship
from sqlalchemy_i18n import make_translatable, translation_base, Translatable
from config import Config

from database import Base
from datetime import datetime, timezone
from sqlalchemy.sql.schema import ForeignKey


class Supplier(Base):
    __tablename__ = 'supplier'
    
    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    
    # Supplier identification
    supplier_code = sql.Column(sql.String(50), nullable=True, unique=True, index=True)  # Internal supplier code
    name = sql.Column(sql.String(255), nullable=False)
    legal_name = sql.Column(sql.String(255), nullable=True)  # Legal business name
    
    # Contact information
    phone = sql.Column(sql.String(20), nullable=True)
    mobile = sql.Column(sql.String(20), nullable=True)
    email = sql.Column(sql.String(255), nullable=True, unique=True, index=True)
    website = sql.Column(sql.String(255), nullable=True)
    
    # Address information
    address = sql.Column(sql.Text, nullable=True)
    city = sql.Column(sql.String(100), nullable=True)
    state = sql.Column(sql.String(100), nullable=True)
    postal_code = sql.Column(sql.String(20), nullable=True)
    country = sql.Column(sql.String(100), nullable=True)
    
    # Business information
    business_type = sql.Column(sql.String(50), nullable=False, default='material_supplier')  # 'material_supplier', 'service_provider', 'equipment_supplier', 'packaging_supplier'
    tax_id = sql.Column(sql.String(100), nullable=True)  # Tax identification number
    registration_number = sql.Column(sql.String(100), nullable=True)  # Business registration number
    vat_number = sql.Column(sql.String(100), nullable=True)  # VAT number
    
    # Supplier status and rating
    status = sql.Column(sql.String(20), nullable=False, default='active')  # 'active', 'inactive', 'suspended', 'blacklisted'
    rating = sql.Column(sql.Numeric(3, 2), nullable=True, default=0)  # Supplier rating (0-5)
    is_preferred = sql.Column(sql.Boolean, default=False)  # Preferred supplier status
    is_verified = sql.Column(sql.Boolean, default=False)  # Verification status
    
    # Payment and terms
    payment_terms = sql.Column(sql.String(50), nullable=True)  # Payment terms (e.g., 'Net 30', 'COD')
    credit_limit = sql.Column(sql.Numeric(12, 2), nullable=True)  # Credit limit
    currency = sql.Column(sql.String(3), nullable=False, default='USD')  # Preferred currency
    discount_percentage = sql.Column(sql.Numeric(5, 2), nullable=True, default=0)  # Default discount percentage
    
    # 3D Printing specific
    specializes_in = sql.Column(sql.JSON, nullable=True)  # Materials or services they specialize in
    material_types = sql.Column(sql.JSON, nullable=True)  # Types of materials they supply
    equipment_types = sql.Column(sql.JSON, nullable=True)  # Types of equipment they supply
    service_capabilities = sql.Column(sql.JSON, nullable=True)  # Services they can provide
    
    # Quality and compliance
    quality_certifications = sql.Column(sql.JSON, nullable=True)  # Quality certifications
    compliance_standards = sql.Column(sql.JSON, nullable=True)  # Compliance standards met
    minimum_order_value = sql.Column(sql.Numeric(10, 2), nullable=True)  # Minimum order value
    lead_time_days = sql.Column(sql.Integer, nullable=True)  # Average lead time in days
    
    # Contact persons
    primary_contact_name = sql.Column(sql.String(255), nullable=True)
    primary_contact_title = sql.Column(sql.String(100), nullable=True)
    primary_contact_phone = sql.Column(sql.String(20), nullable=True)
    primary_contact_email = sql.Column(sql.String(255), nullable=True)
    
    # Additional information
    details = sql.Column(sql.UnicodeText, nullable=True)  # Additional details
    notes = sql.Column(sql.Text, nullable=True)  # Internal notes
    logo = sql.Column(UploadedFileField(upload_storage='supplier_logos'), nullable=True)
    
    # Timestamps
    create_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    modified_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))
    last_order_date = sql.Column(sql.DateTime, nullable=True)  # Date of last order

    def json(self):
        data = {}
        data['id'] = str(self.id)
        data['supplier_code'] = self.supplier_code
        data['name'] = self.name
        data['legal_name'] = self.legal_name
        data['phone'] = self.phone
        data['mobile'] = self.mobile
        data['email'] = self.email
        data['website'] = self.website
        data['address'] = self.address
        data['city'] = self.city
        data['state'] = self.state
        data['postal_code'] = self.postal_code
        data['country'] = self.country
        data['business_type'] = self.business_type
        data['tax_id'] = self.tax_id
        data['registration_number'] = self.registration_number
        data['vat_number'] = self.vat_number
        data['status'] = self.status
        data['rating'] = float(self.rating) if self.rating else None
        data['is_preferred'] = self.is_preferred
        data['is_verified'] = self.is_verified
        data['payment_terms'] = self.payment_terms
        data['credit_limit'] = float(self.credit_limit) if self.credit_limit else None
        data['currency'] = self.currency
        data['discount_percentage'] = float(self.discount_percentage) if self.discount_percentage else None
        data['specializes_in'] = self.specializes_in
        data['material_types'] = self.material_types
        data['equipment_types'] = self.equipment_types
        data['service_capabilities'] = self.service_capabilities
        data['quality_certifications'] = self.quality_certifications
        data['compliance_standards'] = self.compliance_standards
        data['minimum_order_value'] = float(self.minimum_order_value) if self.minimum_order_value else None
        data['lead_time_days'] = self.lead_time_days
        data['primary_contact_name'] = self.primary_contact_name
        data['primary_contact_title'] = self.primary_contact_title
        data['primary_contact_phone'] = self.primary_contact_phone
        data['primary_contact_email'] = self.primary_contact_email
        data['details'] = self.details
        data['notes'] = self.notes
        data['logo'] = str(self.logo) if self.logo else None
        data['create_date'] = self.create_date.isoformat() if self.create_date else None
        data['modified_date'] = self.modified_date.isoformat() if self.modified_date else None
        data['last_order_date'] = self.last_order_date.isoformat() if self.last_order_date else None
        return data
