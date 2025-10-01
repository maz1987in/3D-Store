from enum import Enum

class PaymentStatusEnum(Enum):
    none = 'none'
    pending = 'pending'
    cancel = 'cancel'
    error = 'error'
    fail = 'fail'
    success = 'success'
    refund = 'refund'

class PaymentOptionEnum(Enum):
    cash = 'cash'
    card = 'card'
    mobile_payment = 'Mobile Payment'
    bank_transfer = 'Bank Transfer'

class UserTypeEnum(Enum):
    ADMIN = 'admin'
    USER = 'user'
    OWNER = 'owner'
    GOVERNMENT = 'government'
    CORPORATE = 'corporate'

class LanguageEnum(Enum):
    ENGLISH = 'en'
    ARABIC = 'ar'
    #PERSIAN = 'persian'

class RoleEnum(Enum):
    ADMIN = 'Admin'
    PUBLIC = 'Public'
    OWNER = 'Owner'
    #GOVERNMENT = 'government'
    CORPORATE = 'Corporate'

class MediaTypeEnum(Enum):
    SMS = 'sms'
    EMAIL = 'email'
    PUSH = 'push'

class PlatformEnum(Enum):
    MOBILE = 'mobile'
    ANDROID = 'android'
    IOS = 'ios'
    WEB = 'web'
    ALL = 'all'

class TransactionType(Enum):
    PURCHASE = 'purchase'
    SALE = 'sale'
    TRANSFER = 'transfer'
    RETURN = 'return'
    DAMAGE = 'damage'
    LOSS = 'loss'
    STOCK_ADJUSTMENT = 'stock_adjustment'
    EXPIRY = 'expiry'
    PROMOTION = 'promotion'
    INTERNAL_USE = 'internal_use'
    VENDOR_RETURN = 'vendor_return'

class ProductUnitEnum(Enum):
    PIECE = 'piece'
    KG = 'kg'
    LITER = 'liter'
    METER = 'meter'
    BOX = 'box'
    BAG = 'bag'
    BUNDLE = 'bundle'
    CARTON = 'carton'
    GALLON = 'gallon'
    BARREL = 'barrel'
    DRUM = 'drum'
    TON = 'ton'
    GRAM = 'gram'
    METER_SQUARE = 'meter_square'
    METER_CUBIC = 'meter_cubic'
    LITER_PER_HOUR = 'liter_per_hour'

class ExpenseStatusEnum(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

class LaborUnitEnum(Enum):
    HOUR = 'hour'
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    YEAR = 'year'
    METER = 'meter'
    METER_SQUARE = 'meter_square'
    METER_CUBIC = 'meter_cubic'
    LITER_PER_HOUR = 'liter_per_hour'
    LITER = 'liter'
    KILOGRAM = 'kilogram'
    GRAM = 'gram'
    PIECE = 'piece'
    BAG = 'bag'
    BOX = 'box'
    BUNDLE = 'bundle'
    CARTON = 'carton'
    GALLON = 'gallon'
    BARREL = 'barrel'
    DRUM = 'drum'
    TON = 'ton'
    

class LaborStatusEnum(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

class FiscalYearStatusEnum(Enum):
    OPEN = 'Open'
    CLOSED = 'Closed'

class OrderStatusEnum(Enum):
    PENDING = 'Pending'
    ORDERED = 'Ordered'
    RECEIVED = 'Received'
    CANCELLED = 'Cancelled'

class QuoteStatusEnum(Enum):
    PENDING = 'Pending'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'
    CANCELLED = 'Cancelled'

class ShippingStatusEnum(Enum):
    PENDING = 'Pending'
    SHIPPED = 'Shipped'
    IN_TRANSIT = 'In Transit'
    DELIVERED = 'Delivered'
    RETURNED = 'Returned'
    FAILED = 'Failed'
