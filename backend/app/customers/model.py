import uuid
import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from depot.fields.sqlalchemy import UploadedFileField
from sqlalchemy.orm import backref, relationship
from sqlalchemy_i18n import make_translatable, translation_base, Translatable
from config import Config

from database import Base
from datetime import datetime, timezone


class Customer(Translatable, Base):
    __tablename__ = 'customer'
    __translatable__ = {
        'locales': Config.AVAILABLE_LOCALES,
        #'dynamic_source_locale': True
    }
    locale = Config.DEFAULT_LOCALE

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    
    # Customer identification
    customer_code = sql.Column(sql.String(50), nullable=True, unique=True, index=True)  # Internal customer code
    user_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)  # Link to user account
    
    # Contact information
    email = sql.Column(sql.String(255), nullable=True, unique=True, index=True)
    mobile = sql.Column(sql.String(20), nullable=True, index=True)
    phone = sql.Column(sql.String(20), nullable=True)
    
    # Address information
    address = sql.Column(sql.Text, nullable=True)
    city = sql.Column(sql.String(100), nullable=True)
    state = sql.Column(sql.String(100), nullable=True)
    postal_code = sql.Column(sql.String(20), nullable=True)
    country = sql.Column(sql.String(100), nullable=True)
    location = sql.Column(sql.String(255), nullable=True)  # Legacy field for compatibility
    
    # Customer type and status
    customer_type = sql.Column(sql.String(50), nullable=False, default='individual')  # 'individual', 'business', 'wholesale'
    status = sql.Column(sql.String(20), nullable=False, default='active')  # 'active', 'inactive', 'suspended'
    is_verified = sql.Column(sql.Boolean, default=False)  # Email/phone verification status
    
    # Business information (for business customers)
    business_name = sql.Column(sql.String(255), nullable=True)
    business_registration = sql.Column(sql.String(100), nullable=True)  # Business registration number
    tax_id = sql.Column(sql.String(100), nullable=True)  # Tax identification number
    
    # Preferences and settings
    preferred_language = sql.Column(sql.String(10), nullable=False, default='en')
    currency_preference = sql.Column(sql.String(3), nullable=False, default='USD')
    timezone = sql.Column(sql.String(50), nullable=True)
    
    # 3D Printing specific preferences
    preferred_materials = sql.Column(sql.JSON, nullable=True)  # Preferred print materials
    quality_preference = sql.Column(sql.String(20), nullable=True)  # 'draft', 'standard', 'high', 'ultra_high'
    color_preferences = sql.Column(sql.JSON, nullable=True)  # Preferred colors
    special_requirements = sql.Column(sql.Text, nullable=True)  # Special printing requirements
    
    # Financial information
    credit_limit = sql.Column(sql.Numeric(10, 2), nullable=True)  # Credit limit for the customer
    payment_terms = sql.Column(sql.String(50), nullable=True)  # Payment terms (e.g., 'Net 30', 'COD')
    discount_percentage = sql.Column(sql.Numeric(5, 2), nullable=True, default=0)  # Customer-specific discount
    
    # Marketing and communication
    marketing_consent = sql.Column(sql.Boolean, default=False)  # Marketing communication consent
    newsletter_subscription = sql.Column(sql.Boolean, default=False)  # Newsletter subscription
    sms_notifications = sql.Column(sql.Boolean, default=True)  # SMS notifications
    email_notifications = sql.Column(sql.Boolean, default=True)  # Email notifications
    
    # Additional information
    notes = sql.Column(sql.Text, nullable=True)  # Internal notes about the customer
    source = sql.Column(sql.String(50), nullable=True)  # How the customer found us
    referral_code = sql.Column(sql.String(50), nullable=True)  # Referral code used
    
    # Timestamps
    create_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    modified_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = sql.Column(sql.DateTime, nullable=True)  # Last login date
    last_order_date = sql.Column(sql.DateTime, nullable=True)  # Date of last order

    def json(self):
        data = {}
        data['id'] = str(self.id)
        data['customer_code'] = self.customer_code
        data['user_id'] = str(self.user_id) if self.user_id else None
        data['email'] = self.email
        data['mobile'] = self.mobile
        data['phone'] = self.phone
        data['address'] = self.address
        data['city'] = self.city
        data['state'] = self.state
        data['postal_code'] = self.postal_code
        data['country'] = self.country
        data['location'] = self.location  # Legacy field
        data['customer_type'] = self.customer_type
        data['status'] = self.status
        data['is_verified'] = self.is_verified
        data['business_name'] = self.business_name
        data['business_registration'] = self.business_registration
        data['tax_id'] = self.tax_id
        data['preferred_language'] = self.preferred_language
        data['currency_preference'] = self.currency_preference
        data['timezone'] = self.timezone
        data['preferred_materials'] = self.preferred_materials
        data['quality_preference'] = self.quality_preference
        data['color_preferences'] = self.color_preferences
        data['special_requirements'] = self.special_requirements
        data['credit_limit'] = float(self.credit_limit) if self.credit_limit else None
        data['payment_terms'] = self.payment_terms
        data['discount_percentage'] = float(self.discount_percentage) if self.discount_percentage else None
        data['marketing_consent'] = self.marketing_consent
        data['newsletter_subscription'] = self.newsletter_subscription
        data['sms_notifications'] = self.sms_notifications
        data['email_notifications'] = self.email_notifications
        data['notes'] = self.notes
        data['source'] = self.source
        data['referral_code'] = self.referral_code
        data['create_date'] = self.create_date.isoformat() if self.create_date else None
        data['modified_date'] = self.modified_date.isoformat() if self.modified_date else None
        data['last_login'] = self.last_login.isoformat() if self.last_login else None
        data['last_order_date'] = self.last_order_date.isoformat() if self.last_order_date else None
        
        # Add translated name
        name = {}
        for local in Config().AVAILABLE_LOCALES:
            name[local] = self.translations[local].name
        data['name'] = name
        return data

class CustomerTranslation(translation_base(Customer)):
    __tablename__ = 'customer_translations'
    name = sql.Column(sql.String(255))