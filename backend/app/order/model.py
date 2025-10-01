import uuid
import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from depot.fields.sqlalchemy import UploadedFileField
from sqlalchemy.orm import backref, relationship
from sqlalchemy_i18n import make_translatable, translation_base, Translatable
from app.common.enum import OrderStatusEnum
from config import Config

from database import Base
from datetime import datetime, timezone
from sqlalchemy.sql.schema import ForeignKey


class Order(Base):
    __tablename__ = 'order'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    order_number = sql.Column(sql.String(50), nullable=False, unique=True, index=True)  # Human-readable order number
    
    # Customer information
    customer_id = sql.Column(UUIDType(binary=False), ForeignKey('customer.id', ondelete='CASCADE'), nullable=False)
    
    # Order timing
    order_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    expected_delivery = sql.Column(sql.DateTime, nullable=True)  # When the order is expected to be delivered
    estimated_completion = sql.Column(sql.DateTime, nullable=True)  # When printing is estimated to complete
    
    # Order status and type
    status = sql.Column(sql.Enum(OrderStatusEnum), nullable=False, default=OrderStatusEnum.PENDING)
    order_type = sql.Column(sql.String(50), nullable=False, default='print_service')  # 'print_service', 'ready_made', 'mixed'
    priority = sql.Column(sql.String(20), nullable=False, default='normal')  # 'low', 'normal', 'high', 'urgent'
    
    # Financial information
    subtotal = sql.Column(sql.Numeric(10, 4), nullable=False, default=0.00)  # Subtotal before taxes and fees
    tax_amount = sql.Column(sql.Numeric(10, 4), nullable=False, default=0.00)  # Tax amount
    shipping_cost = sql.Column(sql.Numeric(10, 4), nullable=False, default=0.00)  # Shipping cost
    discount_amount = sql.Column(sql.Numeric(10, 4), nullable=False, default=0.00)  # Discount amount
    total_amount = sql.Column(sql.Numeric(10, 4), nullable=False, default=0.00)  # Final total amount
    currency = sql.Column(sql.String(3), nullable=False, default='USD')  # Currency code
    
    # Payment information
    payment_status = sql.Column(sql.String(20), nullable=False, default='pending')  # 'pending', 'paid', 'partial', 'refunded'
    payment_method = sql.Column(sql.String(50), nullable=True)  # Payment method used
    payment_reference = sql.Column(sql.String(100), nullable=True)  # Payment gateway reference
    
    # Order details
    terms = sql.Column(sql.String(50), nullable=True)  # Payment terms (e.g., Net 30, Prepaid)
    notes = sql.Column(sql.Text, nullable=True)  # Customer notes
    internal_notes = sql.Column(sql.Text, nullable=True)  # Internal staff notes
    
    # 3D Printing specific
    total_print_time_hours = sql.Column(sql.Numeric(8, 2), nullable=True)  # Total estimated print time
    total_material_grams = sql.Column(sql.Numeric(10, 2), nullable=True)  # Total material usage
    requires_post_processing = sql.Column(sql.Boolean, default=False)  # Whether order needs post-processing
    special_instructions = sql.Column(sql.Text, nullable=True)  # Special printing instructions
    
    # Supplier information (for materials/supplies)
    supplier_id = sql.Column(UUIDType(binary=False), ForeignKey('supplier.id', ondelete='SET NULL', name='fk_order_supplier_id'), nullable=True)
    
    # Relationships
    customer = relationship("Customer")
    shipping_info = relationship("Shipping", uselist=False, back_populates="order", cascade="all, delete-orphan")
    print_jobs = relationship("PrintJob", back_populates="order", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    # payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")  # Commented out until Payment model is created

    create_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    modified_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))

    def json(self):
        data = {}
        data['id'] = str(self.id)
        data['order_number'] = self.order_number
        data['customer_id'] = str(self.customer_id) if self.customer_id else None
        data['order_date'] = self.order_date.isoformat() if self.order_date else None
        data['expected_delivery'] = self.expected_delivery.isoformat() if self.expected_delivery else None
        data['estimated_completion'] = self.estimated_completion.isoformat() if self.estimated_completion else None
        data['status'] = self.status.value
        data['order_type'] = self.order_type
        data['priority'] = self.priority
        data['subtotal'] = float(self.subtotal)
        data['tax_amount'] = float(self.tax_amount)
        data['shipping_cost'] = float(self.shipping_cost)
        data['discount_amount'] = float(self.discount_amount)
        data['total_amount'] = float(self.total_amount)
        data['currency'] = self.currency
        data['payment_status'] = self.payment_status
        data['payment_method'] = self.payment_method
        data['payment_reference'] = self.payment_reference
        data['terms'] = self.terms
        data['notes'] = self.notes
        data['internal_notes'] = self.internal_notes
        data['total_print_time_hours'] = float(self.total_print_time_hours) if self.total_print_time_hours else None
        data['total_material_grams'] = float(self.total_material_grams) if self.total_material_grams else None
        data['requires_post_processing'] = self.requires_post_processing
        data['special_instructions'] = self.special_instructions
        data['supplier_id'] = str(self.supplier_id) if self.supplier_id else None
        data['shipping_info'] = self.shipping_info.json() if self.shipping_info else None
        data['print_jobs'] = [job.json() for job in self.print_jobs]
        data['order_items'] = [item.json() for item in self.order_items]
        # data['payments'] = [payment.json() for payment in self.payments]  # Commented out until Payment model is created
        data['create_date'] = self.create_date.isoformat() if self.create_date else None
        data['modified_date'] = self.modified_date.isoformat() if self.modified_date else None
        return data


class OrderItem(Base):
    """Individual items within an order"""
    __tablename__ = 'order_items'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    order_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('order.id', ondelete='CASCADE'), nullable=False)
    product_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    
    # Item details
    quantity = sql.Column(sql.Integer, nullable=False, default=1)
    unit_price = sql.Column(sql.Numeric(10, 4), nullable=False)  # Price per unit
    total_price = sql.Column(sql.Numeric(10, 4), nullable=False)  # Total price for this item
    
    # 3D Printing specific
    material_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('print_materials.id'), nullable=True)
    settings_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('print_settings.id'), nullable=True)
    packaging_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('product_packaging.id'), nullable=True)
    
    # Customization options
    custom_instructions = sql.Column(sql.Text, nullable=True)  # Custom printing instructions
    color_preference = sql.Column(sql.String(50), nullable=True)  # Preferred color
    finish_type = sql.Column(sql.String(50), nullable=True)  # Surface finish preference
    
    # File information (for 3D printing services)
    model_file_name = sql.Column(sql.String(255), nullable=True)  # Original file name
    model_file_size = sql.Column(sql.Integer, nullable=True)  # File size in bytes
    
    create_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))
    modified_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product")
    material = relationship("PrintMaterial")
    settings = relationship("PrintSettings")
    packaging = relationship("ProductPackaging")

    def json(self):
        return {
            'id': str(self.id),
            'order_id': str(self.order_id),
            'product_id': str(self.product_id),
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price),
            'material_id': str(self.material_id) if self.material_id else None,
            'settings_id': str(self.settings_id) if self.settings_id else None,
            'packaging_id': str(self.packaging_id) if self.packaging_id else None,
            'custom_instructions': self.custom_instructions,
            'color_preference': self.color_preference,
            'finish_type': self.finish_type,
            'model_file_name': self.model_file_name,
            'model_file_size': self.model_file_size,
            'product': self.product.json() if self.product else None,
            'material': self.material.json() if self.material else None,
            'settings': self.settings.json() if self.settings else None,
            'packaging': self.packaging.json() if self.packaging else None,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'modified_date': self.modified_date.isoformat() if self.modified_date else None
        }