import uuid
import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from depot.fields.sqlalchemy import UploadedFileField
from sqlalchemy.orm import backref, relationship
from sqlalchemy_i18n import make_translatable, translation_base, Translatable
from app.common.enum import ProductUnitEnum
from config import Config

from database import Base
from datetime import datetime, timezone
from sqlalchemy.sql.schema import ForeignKey


class Product(Translatable, Base):
    __tablename__ = 'product'
    __translatable__ = {
        'locales': Config.AVAILABLE_LOCALES,
        #'dynamic_source_locale': True
    }
    locale = Config.DEFAULT_LOCALE

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    
    # Product identification
    code = sql.Column(sql.String(255), nullable=False, index=True, unique=True)
    sku = sql.Column(sql.String(100), nullable=True, unique=True)  # Stock Keeping Unit
    
    # Product type and category
    product_type = sql.Column(sql.String(50), nullable=False, default='service')  # 'service', 'ready_made', 'material'
    category_id = sql.Column(UUIDType(binary=False), ForeignKey('category.id',ondelete='SET NULL', name='fk_product_category_id'), nullable=True, index=True)
    subcategory_id = sql.Column(UUIDType(binary=False), ForeignKey('category.id',ondelete='SET NULL', name='fk_product_subcategory_id'), nullable=True)
    
    # Pricing
    base_price = sql.Column(sql.Numeric(10, 4), nullable=False, default=0)  # Base price in base currency
    currency = sql.Column(sql.String(3), nullable=False, default='USD')
    is_dynamic_pricing = sql.Column(sql.Boolean, default=False)  # For 3D printing services with variable pricing
    
    # 3D Printing specific fields
    print_time_hours = sql.Column(sql.Numeric(6, 2), nullable=True)  # Estimated print time in hours
    material_usage_grams = sql.Column(sql.Numeric(8, 2), nullable=True)  # Estimated material usage in grams
    print_volume_x = sql.Column(sql.Numeric(8, 2), nullable=True)  # Print volume X in mm
    print_volume_y = sql.Column(sql.Numeric(8, 2), nullable=True)  # Print volume Y in mm
    print_volume_z = sql.Column(sql.Numeric(8, 2), nullable=True)  # Print volume Z in mm
    layer_height = sql.Column(sql.Numeric(4, 3), nullable=True)  # Layer height in mm
    infill_percentage = sql.Column(sql.Integer, nullable=True)  # Infill percentage
    
    # Inventory management
    unit = sql.Column('unit_type', sql.Enum(ProductUnitEnum), nullable=False, default='piece')
    quantity = sql.Column(sql.Integer, nullable=False, default=0)
    min_quantity = sql.Column(sql.Integer, nullable=False, default=0)
    max_quantity = sql.Column(sql.Integer, nullable=True)  # Maximum quantity per order
    is_digital = sql.Column(sql.Boolean, default=False)  # For digital products/services
    
    # Media and files
    images = sql.Column(sql.JSON, nullable=True)  # Product images
    model_files = sql.Column(sql.JSON, nullable=True)  # 3D model files (STL, OBJ, 3MF)
    attachments = sql.Column(sql.JSON, nullable=True)  # Additional attachments
    
    # Product status and visibility
    is_active = sql.Column(sql.Boolean, default=True)
    is_featured = sql.Column(sql.Boolean, default=False)
    is_digital_download = sql.Column(sql.Boolean, default=False)  # For downloadable 3D models
    
    # Supplier and sourcing
    supplier_id = sql.Column(UUIDType(binary=False), ForeignKey('supplier.id',ondelete='SET NULL', name='fk_product_supplier_id'), nullable=True)
    manufacturer = sql.Column(sql.String(255), nullable=True)  # For ready-made products
    
    # SEO and marketing
    meta_title = sql.Column(sql.String(255), nullable=True)
    meta_description = sql.Column(sql.Text, nullable=True)
    tags = sql.Column(sql.JSON, nullable=True)  # Product tags for search
    
    # Relationships
    ratings = relationship("Rating", back_populates="product")
    shipping_cities = relationship("ProductShippingCity", back_populates="product", cascade="all, delete-orphan")
    print_materials = relationship("ProductPrintMaterial", back_populates="product", cascade="all, delete-orphan")
    print_settings = relationship("ProductPrintSettings", back_populates="product", cascade="all, delete-orphan")
    packaging_options = relationship("ProductPackagingOption", back_populates="product", cascade="all, delete-orphan")
    cost_breakdown = relationship("ProductCostBreakdown", back_populates="product", cascade="all, delete-orphan")

    create_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    modified_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def average_rating(self):
        if not self.ratings or len(self.ratings) == 0:
            return 0
        return round(sum(r.score for r in self.ratings) / len(self.ratings), 2)

    def json(self):
        data = {}
        data['id'] = str(self.id)
        data['code'] = self.code
        data['sku'] = self.sku
        data['product_type'] = self.product_type
        data['category_id'] = str(self.category_id) if self.category_id else None
        data['subcategory_id'] = str(self.subcategory_id) if self.subcategory_id else None
        data['base_price'] = float(self.base_price)
        data['currency'] = self.currency
        data['is_dynamic_pricing'] = self.is_dynamic_pricing
        data['print_time_hours'] = float(self.print_time_hours) if self.print_time_hours else None
        data['material_usage_grams'] = float(self.material_usage_grams) if self.material_usage_grams else None
        data['print_volume_x'] = float(self.print_volume_x) if self.print_volume_x else None
        data['print_volume_y'] = float(self.print_volume_y) if self.print_volume_y else None
        data['print_volume_z'] = float(self.print_volume_z) if self.print_volume_z else None
        data['layer_height'] = float(self.layer_height) if self.layer_height else None
        data['infill_percentage'] = self.infill_percentage
        data['unit'] = self.unit.value
        data['quantity'] = self.quantity
        data['min_quantity'] = self.min_quantity
        data['max_quantity'] = self.max_quantity
        data['is_digital'] = self.is_digital
        data['images'] = self.images
        data['model_files'] = self.model_files
        data['attachments'] = self.attachments
        data['is_active'] = self.is_active
        data['is_featured'] = self.is_featured
        data['is_digital_download'] = self.is_digital_download
        data['supplier_id'] = str(self.supplier_id) if self.supplier_id else None
        data['manufacturer'] = self.manufacturer
        data['meta_title'] = self.meta_title
        data['meta_description'] = self.meta_description
        data['tags'] = self.tags
        data['create_date'] = self.create_date.isoformat() if self.create_date else None
        data['modified_date'] = self.modified_date.isoformat() if self.modified_date else None
        data['average_rating'] = self.average_rating
        
        # Add shipping cities
        data['shipping_cities'] = [sc.json() for sc in self.shipping_cities if sc.is_active]
        
        # Add 3D printing relationships
        data['print_materials'] = [pm.json() for pm in self.print_materials]
        data['print_settings'] = [ps.json() for ps in self.print_settings]
        data['packaging_options'] = [po.json() for po in self.packaging_options]
        data['cost_breakdown'] = [cb.json() for cb in self.cost_breakdown]
        
        title = {}
        description = {}
        for local in Config().AVAILABLE_LOCALES:
            title[local] = self.translations[local].title
            description[local] = self.translations[local].description
        data['title'] = title
        data['description'] = description
        return data

class ProductTranslation(translation_base(Product)):
    __tablename__ = 'product_translations'
    title = sql.Column(sql.String(255))
    description = sql.Column(sql.UnicodeText)


class ProductShippingCity(Base):
    __tablename__ = 'product_shipping_cities'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    product_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    city_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('city.id', ondelete='CASCADE'), nullable=False)
    shipping_cost = sql.Column(sql.Numeric(10, 3), nullable=True)  # Optional: different shipping cost per city
    is_active = sql.Column(sql.Boolean, default=True)
    create_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    product = relationship("Product", back_populates="shipping_cities")
    city = relationship("City", back_populates="product_shipping_cities")

    # Unique constraint to prevent duplicate entries
    __table_args__ = (sql.UniqueConstraint('product_id', 'city_id', name='unique_product_city'),)

    def json(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'city_id': self.city_id,
            'shipping_cost': float(self.shipping_cost) if self.shipping_cost else None,
            'is_active': self.is_active,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'city': self.city.json() if self.city else None
        }


# 3D Printing Models
from enum import Enum

class PrintMaterialTypeEnum(Enum):
    PLA = "pla"
    ABS = "abs"
    PETG = "petg"
    TPU = "tpu"
    WOOD_FILLED = "wood_filled"
    METAL_FILLED = "metal_filled"
    CARBON_FIBER = "carbon_fiber"
    NYLON = "nylon"


class PrintQualityEnum(Enum):
    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    ULTRA_HIGH = "ultra_high"


class PackagingTypeEnum(Enum):
    KEYCHAIN = "keychain"
    WRAPPER = "wrapper"
    TAG = "tag"
    BOX = "box"
    CUSTOM = "custom"


class PrintMaterial(Base):
    """3D printing materials available for use"""
    __tablename__ = 'print_materials'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = sql.Column(sql.String(100), nullable=False)
    type = sql.Column(sql.Enum(PrintMaterialTypeEnum), nullable=False)
    color = sql.Column(sql.String(50), nullable=True)
    cost_per_gram = sql.Column(sql.Numeric(10, 4), nullable=False)  # Cost per gram in base currency
    density = sql.Column(sql.Numeric(8, 4), nullable=False)  # Density in g/cm³
    print_temperature = sql.Column(sql.Integer, nullable=True)  # Recommended print temperature
    bed_temperature = sql.Column(sql.Integer, nullable=True)  # Recommended bed temperature
    is_active = sql.Column(sql.Boolean, default=True)
    create_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))
    modified_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    product_materials = relationship("ProductPrintMaterial", back_populates="material")

    def json(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'type': self.type.value,
            'color': self.color,
            'cost_per_gram': float(self.cost_per_gram),
            'density': float(self.density),
            'print_temperature': self.print_temperature,
            'bed_temperature': self.bed_temperature,
            'is_active': self.is_active,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'modified_date': self.modified_date.isoformat() if self.modified_date else None
        }


class PrintSettings(Base):
    """Print quality and settings configurations"""
    __tablename__ = 'print_settings'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = sql.Column(sql.String(100), nullable=False)
    quality = sql.Column(sql.Enum(PrintQualityEnum), nullable=False)
    layer_height = sql.Column(sql.Numeric(4, 3), nullable=False)  # Layer height in mm
    infill_percentage = sql.Column(sql.Integer, nullable=False)  # Infill percentage
    print_speed = sql.Column(sql.Integer, nullable=False)  # Print speed in mm/s
    support_enabled = sql.Column(sql.Boolean, default=False)
    raft_enabled = sql.Column(sql.Boolean, default=False)
    brim_enabled = sql.Column(sql.Boolean, default=False)
    estimated_time_multiplier = sql.Column(sql.Numeric(4, 2), default=1.0)  # Time multiplier for estimation
    is_active = sql.Column(sql.Boolean, default=True)
    create_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    product_settings = relationship("ProductPrintSettings", back_populates="print_settings")

    def json(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'quality': self.quality.value,
            'layer_height': float(self.layer_height),
            'infill_percentage': self.infill_percentage,
            'print_speed': self.print_speed,
            'support_enabled': self.support_enabled,
            'raft_enabled': self.raft_enabled,
            'brim_enabled': self.brim_enabled,
            'estimated_time_multiplier': float(self.estimated_time_multiplier),
            'is_active': self.is_active,
            'create_date': self.create_date.isoformat() if self.create_date else None
        }


class ProductPackaging(Base):
    """Packaging options for products"""
    __tablename__ = 'product_packaging'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = sql.Column(sql.String(100), nullable=False)
    type = sql.Column(sql.Enum(PackagingTypeEnum), nullable=False)
    cost = sql.Column(sql.Numeric(10, 4), nullable=False)  # Cost per unit
    description = sql.Column(sql.Text, nullable=True)
    is_active = sql.Column(sql.Boolean, default=True)
    create_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    product_packaging = relationship("ProductPackagingOption", back_populates="packaging")

    def json(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'type': self.type.value,
            'cost': float(self.cost),
            'description': self.description,
            'is_active': self.is_active,
            'create_date': self.create_date.isoformat() if self.create_date else None
        }


class ProductPrintMaterial(Base):
    """Many-to-many relationship between products and print materials"""
    __tablename__ = 'product_print_materials'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    product_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    material_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('print_materials.id', ondelete='CASCADE'), nullable=False)
    is_default = sql.Column(sql.Boolean, default=False)
    additional_cost = sql.Column(sql.Numeric(10, 4), default=0)  # Additional cost for this material
    create_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    product = relationship("Product")
    material = relationship("PrintMaterial", back_populates="product_materials")

    # Unique constraint
    __table_args__ = (sql.UniqueConstraint('product_id', 'material_id', name='unique_product_material'),)

    def json(self):
        return {
            'id': str(self.id),
            'product_id': str(self.product_id),
            'material_id': str(self.material_id),
            'is_default': self.is_default,
            'additional_cost': float(self.additional_cost),
            'material': self.material.json() if self.material else None
        }


class ProductPrintSettings(Base):
    """Many-to-many relationship between products and print settings"""
    __tablename__ = 'product_print_settings'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    product_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    settings_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('print_settings.id', ondelete='CASCADE'), nullable=False)
    is_default = sql.Column(sql.Boolean, default=False)
    additional_cost = sql.Column(sql.Numeric(10, 4), default=0)  # Additional cost for this setting
    create_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    product = relationship("Product")
    print_settings = relationship("PrintSettings", back_populates="product_settings")

    # Unique constraint
    __table_args__ = (sql.UniqueConstraint('product_id', 'settings_id', name='unique_product_settings'),)

    def json(self):
        return {
            'id': str(self.id),
            'product_id': str(self.product_id),
            'settings_id': str(self.settings_id),
            'is_default': self.is_default,
            'additional_cost': float(self.additional_cost),
            'print_settings': self.print_settings.json() if self.print_settings else None
        }


class ProductPackagingOption(Base):
    """Many-to-many relationship between products and packaging options"""
    __tablename__ = 'product_packaging_options'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    product_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    packaging_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('product_packaging.id', ondelete='CASCADE'), nullable=False)
    is_default = sql.Column(sql.Boolean, default=False)
    create_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    product = relationship("Product")
    packaging = relationship("ProductPackaging", back_populates="product_packaging")

    # Unique constraint
    __table_args__ = (sql.UniqueConstraint('product_id', 'packaging_id', name='unique_product_packaging'),)

    def json(self):
        return {
            'id': str(self.id),
            'product_id': str(self.product_id),
            'packaging_id': str(self.packaging_id),
            'is_default': self.is_default,
            'packaging': self.packaging.json() if self.packaging else None
        }


class ProductCostBreakdown(Base):
    """Cost breakdown for products including materials, labor, overhead, etc."""
    __tablename__ = 'product_cost_breakdown'

    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    product_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    
    # Cost components
    material_cost = sql.Column(sql.Numeric(10, 4), nullable=False, default=0)
    labor_cost = sql.Column(sql.Numeric(10, 4), nullable=False, default=0)
    overhead_cost = sql.Column(sql.Numeric(10, 4), nullable=False, default=0)
    packaging_cost = sql.Column(sql.Numeric(10, 4), nullable=False, default=0)
    shipping_cost = sql.Column(sql.Numeric(10, 4), nullable=False, default=0)
    markup_percentage = sql.Column(sql.Numeric(5, 2), nullable=False, default=0)  # Markup percentage
    total_cost = sql.Column(sql.Numeric(10, 4), nullable=False, default=0)
    
    # Cost calculation method
    calculation_method = sql.Column(sql.String(50), nullable=False, default='manual')  # 'manual', 'auto', 'formula'
    formula = sql.Column(sql.Text, nullable=True)  # For automated cost calculation
    
    # Validity period
    effective_from = sql.Column(sql.DateTime, nullable=False, default=datetime.now(timezone.utc))
    effective_to = sql.Column(sql.DateTime, nullable=True)
    is_active = sql.Column(sql.Boolean, default=True)
    
    create_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))
    modified_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    product = relationship("Product", back_populates="cost_breakdown")

    def json(self):
        return {
            'id': str(self.id),
            'product_id': str(self.product_id),
            'material_cost': float(self.material_cost),
            'labor_cost': float(self.labor_cost),
            'overhead_cost': float(self.overhead_cost),
            'packaging_cost': float(self.packaging_cost),
            'shipping_cost': float(self.shipping_cost),
            'markup_percentage': float(self.markup_percentage),
            'total_cost': float(self.total_cost),
            'calculation_method': self.calculation_method,
            'formula': self.formula,
            'effective_from': self.effective_from.isoformat() if self.effective_from else None,
            'effective_to': self.effective_to.isoformat() if self.effective_to else None,
            'is_active': self.is_active,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'modified_date': self.modified_date.isoformat() if self.modified_date else None
        }