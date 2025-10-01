from datetime import datetime, timedelta, timezone
import uuid
from config import BaseConfig
from flask import g

def debug_return(value, name=None):
    if BaseConfig.DEBUG:
        return value
    return {'error': f"Failed to retrieve '{name}'"} if name else {'error': 'Failed to retrieve value'}

def get_weekdays(from_date, to_date):
    from datetime import datetime, timezone, timedelta
    
    # printing dates
   # print("The original range : " + str(from_date) + " " + str(to_date))
    
    # generating dates
    dates = (from_date + timedelta(idx + 1)
            for idx in range((to_date - from_date).days))
    
    # summing all weekdays (as Friday and Saturday are not business days)
    res = sum(1 for day in dates if not 4 <= day.weekday() <= 5)
    
    # printing
    #print("Total business days in range : " + str(res))
    
    return int(res)

def get_weekenddays(from_date, to_date):  
    from datetime import datetime, timezone, timedelta
    from_date = change_string_to_time(from_date)
    to_date = change_string_to_time(to_date)
    week_days = get_weekdays(from_date, to_date)
    
    fill_days = (from_date - to_date).days

    weekenddays = fill_days - week_days
    return weekenddays

def get_owner_id():
    from flask import g
    if hasattr(g, 'owner'):
        return g.owner

def get_user_id():
    from flask import g
    if hasattr(g, 'user'):
        return g.user.id


def has_permission(permissions):
    from flask import g
    if hasattr(g, 'permission') and any(permission in permissions for permission in g.permission):
        return True
    return False

def get_random_value(length):
    import secrets
    import string
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

def get_random_digits_value(length):
    import secrets
    import string
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def change_string_to_time(value, validate_sql=True,tz_name='UTC'):
    #import pytz
    from dateutil.parser import parse
    from dateutil import tz
    if value is None:
        return value
    if type(value) is str:
        #if not validate_sql or BaseConfig.DB_TYPE == 'sqlite':
        value = parse(value)
    if value.tzinfo is None:
        value = value.replace(tzinfo=tz.gettz(tz_name))
    else:
        value = value.astimezone(tz.gettz(tz_name))
    return value

def get_local_datetime(datetime=datetime.now(timezone.utc)):
    from dateutil import tz
    return datetime.astimezone(tz.gettz(BaseConfig.TIME_ZONE))

def to_json(data):
    import json
    json_data = json.dumps(data, ensure_ascii=False) if data is not None else None
    return json_data
# remove leading pluss signs and trailing whitespaces and leading zeros
def remove_leading_plus(value):
    return str(value).lstrip('+').lstrip('0').strip()

# remove leading zeros and trailing whitespaces
def remove_leading_zeros(value):
    return str(value).lstrip('0').strip()

# change str to lower case and whitespace to underscore
def change_to_lowercase(value):
    return value.lower().replace(' ','_')


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    return v.lower() in ("yes", "true", "t", "1")

def equal_to(value, compare_value):
    if value is None or compare_value is None:
        return False
    if type(value) is not str:
        value = str(value)
    if type(compare_value) is not str:
        compare_value = str(compare_value)
    
    return value.lower() == compare_value.lower() 

def to_dict(row):
    try:
        if row is None:
            return None

        rtn_dict = dict()
        keys = row.__table__.columns.keys()
        #print(keys)
        for key in keys:
            rtn_dict[key] = getattr(row, key)
        return rtn_dict
    except Exception as e:
        print('to_dict: ', e)
        return None

try:
    import magic
except ImportError:
    magic = None
    print("Warning: The 'libmagic1' library is not installed. Content type validation will not be available.")
def validate_file_content(file, allowed_content_types):
    if magic is None:
        return True  # Accept the file if libmagic1 is not installed
    if file == None:
        return False
    file_content_type = magic.from_buffer(file.read(), mime=True)
    file.seek(0)
    return file_content_type in allowed_content_types

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val).strip())
        return True
    except ValueError:
        return False

# uuid to string if uuid is valid
def uuid_to_string(val):
    if is_valid_uuid(val):
        return str(val)
    return None

def ensure_utc(end_date, timezone_str='UTC'):
    import pytz
    """
    Ensure that the end_date is a timezone-aware datetime object in UTC.

    :param end_date: The datetime object to check and convert.
    :param timezone_str: The string representation of the timezone of end_date if it's naive.
                         Defaults to 'UTC' if the timezone is unknown.
    :return: The datetime object in UTC.
    """
    try:
        # If end_date is naive (no timezone info), assume it's in the provided timezone
        if end_date.tzinfo is None or end_date.tzinfo.utcoffset(end_date) is None:
            timezone = pytz.timezone(timezone_str)
            end_date = timezone.localize(end_date)

        # Convert to UTC
        utc_end_date = end_date.astimezone(pytz.utc)
        return utc_end_date
    except Exception as e:
        print('ensure_utc: ', e)
        return end_date

def print_dict_items(d, indent=0, parent_key=""):
    output = ""
    for key, value in d.items():
        # Determine if the current value is the last in its container
        is_last = key == list(d.keys())[-1]
        # Prefix for nested structures or terminal values
        prefix = "└── " if is_last else "├── "
        # Handling for nested dictionaries
        if isinstance(value, dict):
            output += f"{' ' * (indent-4) + prefix if indent else ''}{key} <type: dict>:\n"
            output += print_dict_items(value, indent + 4, key)
        else:
            output += f"{' ' * (indent-4) + prefix if indent else ''}{key}: {value} (Type: {type(value).__name__})\n"
    return output

def get_fiscal_year_id():
    from app.financial.service import FiscalYearService
    fiscal_year_id = g.get('fy_id', None)
    if not fiscal_year_id:
        fiscal_year_service = FiscalYearService()
        result, status = fiscal_year_service.get_current_open_unlocked_fiscal_year()
        if status == 200:
            fiscal_year_id = result['id']
            g.fy_id = fiscal_year_id
    return fiscal_year_id

def get_jwt_exp_delta():
    unit = getattr(BaseConfig, 'JWT_EXPIRATION_UNIT', 'days')
    value = getattr(BaseConfig, 'JWT_EXPIRATION_VALUE', 365)
    if unit == 'days':
        return timedelta(days=value)
    elif unit == 'hours':
        return timedelta(hours=value)
    elif unit == 'seconds':
        return timedelta(seconds=value)
    else:
        return timedelta(hours=5)  # default fallback

def format_mobile(number: str) -> str:
    # Remove spaces, dashes, etc.
    number = number.strip().replace(" ", "").replace("-", "")
    
    # If starts with Oman country code
    if number.startswith("968"):
        number = number[3:]
    
    return number