import uuid
import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from depot.fields.sqlalchemy import UploadedFileField
from sqlalchemy.orm import backref, relationship
from database import Base
from datetime import datetime, timezone
from sqlalchemy.sql.schema import ForeignKey
from enum import Enum


class SellerStatusEnum(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    SUSPENDED = "suspended"
    REJECTED = "rejected"
    INACTIVE = "inactive"


class CommissionTypeEnum(Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"
    TIERED = "tiered"


class PaymentStatusEnum(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Seller(Base):
    """Seller profiles and business information"""
    __tablename__ = 'sellers'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    user_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    
    # Business information
    business_name = sql.Column(sql.String(255), nullable=False)
    business_type = sql.Column(sql.String(100), nullable=False)  # individual, company, partnership
    tax_id = sql.Column(sql.String(100), nullable=True)
    business_license = sql.Column(sql.String(100), nullable=True)
    business_address = sql.Column(sql.Text, nullable=False)
    business_phone = sql.Column(sql.String(20), nullable=True)
    business_email = sql.Column(sql.String(255), nullable=True)
    
    # Bank information
    bank_name = sql.Column(sql.String(100), nullable=True)
    bank_account_number = sql.Column(sql.String(50), nullable=True)
    bank_routing_number = sql.Column(sql.String(20), nullable=True)
    bank_swift_code = sql.Column(sql.String(20), nullable=True)
    
    # Status and verification
    status = sql.Column(sql.Enum(SellerStatusEnum), default=SellerStatusEnum.PENDING, index=True)
    verification_status = sql.Column(sql.String(20), default='pending')  # pending, verified, rejected
    verification_notes = sql.Column(sql.Text, nullable=True)
    verified_at = sql.Column(sql.DateTime, nullable=True)
    verified_by = sql.Column(UUIDType(binary=False), sql.ForeignKey('users.id'), nullable=True)
    
    # Commission settings
    commission_type = sql.Column(sql.Enum(CommissionTypeEnum), default=CommissionTypeEnum.PERCENTAGE)
    commission_rate = sql.Column(sql.Numeric(5, 2), nullable=False, default=5.0)  # Percentage or fixed amount
    minimum_payout = sql.Column(sql.Numeric(10, 2), nullable=False, default=50.0)
    payment_frequency = sql.Column(sql.String(20), nullable=False, default='monthly')  # weekly, bi_weekly, monthly, quarterly
    
    # Performance tracking
    total_sales = sql.Column(sql.Numeric(12, 2), default=0)
    total_commission_earned = sql.Column(sql.Numeric(12, 2), default=0)
    total_commission_paid = sql.Column(sql.Numeric(12, 2), default=0)
    total_orders = sql.Column(sql.Integer, default=0)
    average_order_value = sql.Column(sql.Numeric(10, 2), default=0)
    
    # Contact information
    contact_person = sql.Column(sql.String(100), nullable=True)
    contact_phone = sql.Column(sql.String(20), nullable=True)
    contact_email = sql.Column(sql.String(255), nullable=True)
    
    # Additional information
    description = sql.Column(sql.Text, nullable=True)
    website = sql.Column(sql.String(255), nullable=True)
    social_media = sql.Column(sql.JSON, nullable=True)  # Store social media links
    
    # Settings
    is_active = sql.Column(sql.Boolean, default=True, index=True)
    auto_approve_orders = sql.Column(sql.Boolean, default=False)
    notification_preferences = sql.Column(sql.JSON, nullable=True)
    
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    verifier = relationship("User", foreign_keys=[verified_by])
    commissions = relationship("SellerCommission", back_populates="seller", cascade="all, delete-orphan")
    payments = relationship("SellerPayment", back_populates="seller", cascade="all, delete-orphan")
    performance = relationship("SellerPerformance", back_populates="seller", cascade="all, delete-orphan")
    documents = relationship("SellerDocument", back_populates="seller", cascade="all, delete-orphan")

    def json(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'business_name': self.business_name,
            'business_type': self.business_type,
            'tax_id': self.tax_id,
            'business_license': self.business_license,
            'business_address': self.business_address,
            'business_phone': self.business_phone,
            'business_email': self.business_email,
            'bank_name': self.bank_name,
            'bank_account_number': self.bank_account_number,
            'bank_routing_number': self.bank_routing_number,
            'bank_swift_code': self.bank_swift_code,
            'status': self.status.value,
            'verification_status': self.verification_status,
            'verification_notes': self.verification_notes,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'verified_by': str(self.verified_by) if self.verified_by else None,
            'commission_type': self.commission_type.value,
            'commission_rate': float(self.commission_rate),
            'minimum_payout': float(self.minimum_payout),
            'payment_frequency': self.payment_frequency,
            'total_sales': float(self.total_sales),
            'total_commission_earned': float(self.total_commission_earned),
            'total_commission_paid': float(self.total_commission_paid),
            'total_orders': self.total_orders,
            'average_order_value': float(self.average_order_value),
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'description': self.description,
            'website': self.website,
            'social_media': self.social_media,
            'is_active': self.is_active,
            'auto_approve_orders': self.auto_approve_orders,
            'notification_preferences': self.notification_preferences,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'modified_date': self.modified_date.isoformat() if self.modified_date else None
        }


class SellerCommission(Base):
    """Commission rates and agreements per seller"""
    __tablename__ = 'seller_commissions'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    seller_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('sellers.id', ondelete='CASCADE'), nullable=False)
    
    # Commission details
    commission_type = sql.Column(sql.Enum(CommissionTypeEnum), nullable=False)
    base_rate = sql.Column(sql.Numeric(5, 2), nullable=False)  # Base commission rate
    tier_1_rate = sql.Column(sql.Numeric(5, 2), nullable=True)  # Tier 1 rate (e.g., 0-1000 sales)
    tier_1_threshold = sql.Column(sql.Numeric(12, 2), nullable=True)  # Tier 1 threshold
    tier_2_rate = sql.Column(sql.Numeric(5, 2), nullable=True)  # Tier 2 rate (e.g., 1000-5000 sales)
    tier_2_threshold = sql.Column(sql.Numeric(12, 2), nullable=True)  # Tier 2 threshold
    tier_3_rate = sql.Column(sql.Numeric(5, 2), nullable=True)  # Tier 3 rate (e.g., 5000+ sales)
    
    # Validity period
    effective_from = sql.Column(sql.DateTime, nullable=False)
    effective_to = sql.Column(sql.DateTime, nullable=True)
    
    # Additional settings
    minimum_commission = sql.Column(sql.Numeric(10, 2), nullable=True)
    maximum_commission = sql.Column(sql.Numeric(10, 2), nullable=True)
    is_active = sql.Column(sql.Boolean, default=True)
    
    # Agreement details
    agreement_terms = sql.Column(sql.Text, nullable=True)
    signed_at = sql.Column(sql.DateTime, nullable=True)
    signed_by = sql.Column(UUIDType(binary=False), sql.ForeignKey('users.id'), nullable=True)
    
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))

    # Relationships
    seller = relationship("Seller", back_populates="commissions")
    signer = relationship("User", foreign_keys=[signed_by])

    def json(self):
        return {
            'id': str(self.id),
            'seller_id': str(self.seller_id),
            'commission_type': self.commission_type.value,
            'base_rate': float(self.base_rate),
            'tier_1_rate': float(self.tier_1_rate) if self.tier_1_rate else None,
            'tier_1_threshold': float(self.tier_1_threshold) if self.tier_1_threshold else None,
            'tier_2_rate': float(self.tier_2_rate) if self.tier_2_rate else None,
            'tier_2_threshold': float(self.tier_2_threshold) if self.tier_2_threshold else None,
            'tier_3_rate': float(self.tier_3_rate) if self.tier_3_rate else None,
            'effective_from': self.effective_from.isoformat() if self.effective_from else None,
            'effective_to': self.effective_to.isoformat() if self.effective_to else None,
            'minimum_commission': float(self.minimum_commission) if self.minimum_commission else None,
            'maximum_commission': float(self.maximum_commission) if self.maximum_commission else None,
            'is_active': self.is_active,
            'agreement_terms': self.agreement_terms,
            'signed_at': self.signed_at.isoformat() if self.signed_at else None,
            'signed_by': str(self.signed_by) if self.signed_by else None,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'modified_date': self.modified_date.isoformat() if self.modified_date else None
        }


class SellerPayment(Base):
    """Commission payments and settlements"""
    __tablename__ = 'seller_payments'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    seller_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('sellers.id', ondelete='CASCADE'), nullable=False)
    
    # Payment details
    amount = sql.Column(sql.Numeric(12, 2), nullable=False)
    commission_period_start = sql.Column(sql.DateTime, nullable=False)
    commission_period_end = sql.Column(sql.DateTime, nullable=False)
    payment_method = sql.Column(sql.String(50), nullable=False)  # bank_transfer, paypal, check, etc.
    
    # Status and tracking
    status = sql.Column(sql.Enum(PaymentStatusEnum), default=PaymentStatusEnum.PENDING)
    payment_reference = sql.Column(sql.String(100), nullable=True)
    transaction_id = sql.Column(sql.String(100), nullable=True)
    
    # Processing details
    processed_at = sql.Column(sql.DateTime, nullable=True)
    processed_by = sql.Column(UUIDType(binary=False), sql.ForeignKey('users.id'), nullable=True)
    failure_reason = sql.Column(sql.Text, nullable=True)
    
    # Additional information
    notes = sql.Column(sql.Text, nullable=True)
    payment_metadata = sql.Column(sql.JSON, nullable=True)  # Additional payment data
    
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))

    # Relationships
    seller = relationship("Seller", back_populates="payments")
    processor = relationship("User", foreign_keys=[processed_by])

    def json(self):
        return {
            'id': str(self.id),
            'seller_id': str(self.seller_id),
            'amount': float(self.amount),
            'commission_period_start': self.commission_period_start.isoformat() if self.commission_period_start else None,
            'commission_period_end': self.commission_period_end.isoformat() if self.commission_period_end else None,
            'payment_method': self.payment_method,
            'status': self.status.value,
            'payment_reference': self.payment_reference,
            'transaction_id': self.transaction_id,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'processed_by': str(self.processed_by) if self.processed_by else None,
            'failure_reason': self.failure_reason,
            'notes': self.notes,
            'payment_metadata': self.payment_metadata,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'modified_date': self.modified_date.isoformat() if self.modified_date else None
        }


class SellerPerformance(Base):
    """Sales performance and statistics"""
    __tablename__ = 'seller_performance'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    seller_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('sellers.id', ondelete='CASCADE'), nullable=False)
    
    # Time period
    period_start = sql.Column(sql.DateTime, nullable=False)
    period_end = sql.Column(sql.DateTime, nullable=False)
    period_type = sql.Column(sql.String(20), nullable=False)  # daily, weekly, monthly, quarterly, yearly
    
    # Performance metrics
    total_orders = sql.Column(sql.Integer, default=0)
    total_sales = sql.Column(sql.Numeric(12, 2), default=0)
    total_commission = sql.Column(sql.Numeric(12, 2), default=0)
    average_order_value = sql.Column(sql.Numeric(10, 2), default=0)
    conversion_rate = sql.Column(sql.Numeric(5, 2), default=0)  # Percentage
    
    # Customer metrics
    new_customers = sql.Column(sql.Integer, default=0)
    returning_customers = sql.Column(sql.Integer, default=0)
    customer_retention_rate = sql.Column(sql.Numeric(5, 2), default=0)
    
    # Product metrics
    top_selling_product = sql.Column(sql.String(255), nullable=True)
    total_products_sold = sql.Column(sql.Integer, default=0)
    
    # Rankings and comparisons
    rank_in_period = sql.Column(sql.Integer, nullable=True)
    performance_score = sql.Column(sql.Numeric(5, 2), default=0)  # 0-100 score
    
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))

    # Relationships
    seller = relationship("Seller", back_populates="performance")

    def json(self):
        return {
            'id': str(self.id),
            'seller_id': str(self.seller_id),
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'period_type': self.period_type,
            'total_orders': self.total_orders,
            'total_sales': float(self.total_sales),
            'total_commission': float(self.total_commission),
            'average_order_value': float(self.average_order_value),
            'conversion_rate': float(self.conversion_rate),
            'new_customers': self.new_customers,
            'returning_customers': self.returning_customers,
            'customer_retention_rate': float(self.customer_retention_rate),
            'top_selling_product': self.top_selling_product,
            'total_products_sold': self.total_products_sold,
            'rank_in_period': self.rank_in_period,
            'performance_score': float(self.performance_score),
            'create_date': self.create_date.isoformat() if self.create_date else None
        }


class SellerDocument(Base):
    """Business documents and agreements"""
    __tablename__ = 'seller_documents'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    seller_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('sellers.id', ondelete='CASCADE'), nullable=False)
    
    # Document details
    document_type = sql.Column(sql.String(50), nullable=False)  # business_license, tax_certificate, agreement, etc.
    document_name = sql.Column(sql.String(255), nullable=False)
    document_file = sql.Column(UploadedFileField, nullable=False)
    file_size = sql.Column(sql.BigInteger, nullable=False)
    file_type = sql.Column(sql.String(50), nullable=False)
    
    # Document status
    is_verified = sql.Column(sql.Boolean, default=False)
    verified_at = sql.Column(sql.DateTime, nullable=True)
    verified_by = sql.Column(UUIDType(binary=False), sql.ForeignKey('users.id'), nullable=True)
    verification_notes = sql.Column(sql.Text, nullable=True)
    
    # Expiry and renewal
    expiry_date = sql.Column(sql.DateTime, nullable=True)
    is_expired = sql.Column(sql.Boolean, default=False)
    renewal_reminder_sent = sql.Column(sql.Boolean, default=False)
    
    # Additional information
    description = sql.Column(sql.Text, nullable=True)
    document_metadata = sql.Column(sql.JSON, nullable=True)
    
    is_active = sql.Column(sql.Boolean, default=True)
    create_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))
    modified_date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))

    # Relationships
    seller = relationship("Seller", back_populates="documents")
    verifier = relationship("User", foreign_keys=[verified_by])

    def json(self):
        return {
            'id': str(self.id),
            'seller_id': str(self.seller_id),
            'document_type': self.document_type,
            'document_name': self.document_name,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'is_verified': self.is_verified,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'verified_by': str(self.verified_by) if self.verified_by else None,
            'verification_notes': self.verification_notes,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'is_expired': self.is_expired,
            'renewal_reminder_sent': self.renewal_reminder_sent,
            'description': self.description,
            'payment_metadata': self.payment_metadata,
            'is_active': self.is_active,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'modified_date': self.modified_date.isoformat() if self.modified_date else None
        }
