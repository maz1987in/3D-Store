import uuid
from depot.fields.sqlalchemy import UploadedFileField
import sqlalchemy as sql
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import backref, relationship
from flask_babel import get_locale
from sqlalchemy_i18n import make_translatable, translation_base, Translatable
from config import Config

from database import Base
from datetime import datetime, timezone
from sqlalchemy.sql.schema import ForeignKey

class Category(Translatable, Base):
    __tablename__ = 'category'
    __translatable__ = {
        'locales': Config().AVAILABLE_LOCALES,
    }
    locale = Config.DEFAULT_LOCALE
 
    id = sql.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    parent_id = sql.Column(UUIDType(binary=False), ForeignKey('category.id', ondelete='SET NULL', name='fk_category_parent_id'), nullable=True, index=True)
    
    # Category identification
    code = sql.Column(sql.String(50), nullable=True, unique=True, index=True)  # Category code
    slug = sql.Column(sql.String(100), nullable=True, unique=True, index=True)  # URL-friendly slug
    
    # Category status and visibility
    is_active = sql.Column(sql.Boolean(), nullable=False, default=True, index=True)
    is_featured = sql.Column(sql.Boolean(), nullable=False, default=True, index=True)
    sort_order = sql.Column(sql.Integer, nullable=False, default=0)  # Display order
    
    # Category type (for 3D printing services)
    category_type = sql.Column(sql.String(50), nullable=False, default='product', index=True)  # 'product', 'service', 'material', 'ready_made'
    
    # Visual elements
    css_class = sql.Column(sql.String(128), nullable=True)
    icon = sql.Column(UploadedFileField(upload_storage='icon'), nullable=True)
    image = sql.Column(UploadedFileField(upload_storage='category_images'), nullable=True)
    banner_image = sql.Column(UploadedFileField(upload_storage='category_banners'), nullable=True)
    
    # SEO and metadata
    meta_title = sql.Column(sql.String(255), nullable=True)
    meta_description = sql.Column(sql.Text, nullable=True)
    meta_keywords = sql.Column(sql.Text, nullable=True)
    
    # 3D Printing specific fields
    default_material_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('print_materials.id'), nullable=True)
    default_settings_id = sql.Column(UUIDType(binary=False), sql.ForeignKey('print_settings.id'), nullable=True)
    min_order_quantity = sql.Column(sql.Integer, nullable=True, default=1)
    max_order_quantity = sql.Column(sql.Integer, nullable=True)
    
    # Pricing and commission
    base_commission_rate = sql.Column(sql.Numeric(5, 2), nullable=True, default=0)  # Base commission rate for sellers
    markup_percentage = sql.Column(sql.Numeric(5, 2), nullable=True, default=0)  # Default markup percentage
    
    # Timestamps
    create_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    modified_date = sql.Column(sql.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    sub_categories = relationship('Category', backref=backref('parent', remote_side='Category.id'), lazy='dynamic')
    products = relationship('Product', foreign_keys='Product.category_id', backref='parent_category', lazy='dynamic')
    subcategory_products = relationship('Product', foreign_keys='Product.subcategory_id', backref='subcategory', lazy='dynamic')
    default_material = relationship('PrintMaterial')
    default_settings = relationship('PrintSettings')

    def json(self):
        data = {}
        data["id"] = str(self.id)
        data["parent_id"] = str(self.parent_id) if self.parent_id else None
        data["code"] = self.code
        data["slug"] = self.slug
        data["is_active"] = self.is_active
        data["is_featured"] = self.is_featured
        data["sort_order"] = self.sort_order
        data["category_type"] = self.category_type
        data["css_class"] = self.css_class
        data["icon"] = str(self.icon) if self.icon else None
        data["image"] = str(self.image) if self.image else None
        data["banner_image"] = str(self.banner_image) if self.banner_image else None
        data["meta_title"] = self.meta_title
        data["meta_description"] = self.meta_description
        data["meta_keywords"] = self.meta_keywords
        data["default_material_id"] = str(self.default_material_id) if self.default_material_id else None
        data["default_settings_id"] = str(self.default_settings_id) if self.default_settings_id else None
        data["min_order_quantity"] = self.min_order_quantity
        data["max_order_quantity"] = self.max_order_quantity
        data["base_commission_rate"] = float(self.base_commission_rate) if self.base_commission_rate else None
        data["markup_percentage"] = float(self.markup_percentage) if self.markup_percentage else None
        data["create_date"] = self.create_date.isoformat() if self.create_date else None
        data["modified_date"] = self.modified_date.isoformat() if self.modified_date else None
        
        # Add translated content
        name = {}
        content = {}
        for local in Config().AVAILABLE_LOCALES:
            name[local] = self.translations[local].name
            content[local] = self.translations[local].content
        data["name"] = name
        data["content"] = content
        
        # Add relationships
        data["sub_categories"] = [cat.json() for cat in self.sub_categories.filter_by(is_active=True)]
        data["products"] = [product.json() for product in self.products.filter_by(is_active=True)]
        data["subcategory_products"] = [product.json() for product in self.subcategory_products.filter_by(is_active=True)]
        data["default_material"] = self.default_material.json() if self.default_material else None
        data["default_settings"] = self.default_settings.json() if self.default_settings else None
        
        return data

    def for_short(self):
        data = {}
        data["id"] = self.id
        data["css_class"] = self.css_class
        data["icon"] = self.icon
        name = {}
        content = {}
        for local in Config().AVAILABLE_LOCALES:
            name[local] = self.translations[local].name
            content[local] = self.translations[local].content
        data["name"] = name
        data["content"] = content
        return data

class CategoryTranslation(translation_base(Category)):
    __tablename__ = 'category_translations'
    name = sql.Column(sql.Unicode(255))
    content = sql.Column(sql.UnicodeText)
   
