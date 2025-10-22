import json
import os
import sqlalchemy as sql
from sqlalchemy import pool
from os import environ, path
from flask_babel import lazy_gettext as _

from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'),override=False)

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    return v.lower() in ('yes', 'true', 't', '1')
class Config:
    __skip__ = ['SECRET_KEY','FLASK_DEBUG','ENV','FLASK_APP','DEFAULT_LOCALE','JSON_AS_ASCII','AVAILABLE_LOCALES']
    '''Configuration from environment variables.'''
    SECRET_KEY = os.getenv('SECRET_KEY','_5m@rT0rLab_1Syyo')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG')
    ENV = os.getenv('ENV')
    FLASK_APP = 'app.py'
    DEFAULT_LOCALE = 'ar'
    JSON_AS_ASCII = str2bool(os.getenv('JSON_AS_ASCII',False))
    AVAILABLE_LOCALES = {
        'en': _('English'),
        'ar': _('Arabic')
    }
    SENTRY = str2bool(os.getenv('SENTRY', False))
    SENTRY_DSN = os.getenv('SENTRY_DSN','')
    SENTRY_TRACES_SAMPLE_RATE = float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', 1.0))
    #SENTRY_ENVIRONMENT = os.getenv('SENTRY_ENVIRONMENT','development')
    

class BaseConfig(object):
    __skip__ = ['DATABASE_URL','DB_TYPE','DB_USERNAME','DB_PASSWORD','DB_DATABASE_NAME','DB_CONNECTION_NAME','DB_HOST','engine','db_common_options','db_specific_options']
    DEBUG = os.getenv('DEBUG','True')
    TIME_ZONE = os.getenv('TIME_ZONE','Asia/Muscat')
    JWT_EXPIRATION_DELTA = int(os.getenv('JWT_EXPIRATION_DELTA', 365))
    WT_EXPIRATION_UNIT = os.getenv('JWT_EXPIRATION_UNIT', 'days')  # 'days', 'hours', or 'seconds'
    HOST_URL = os.getenv('HOST_URL','http://localhost:5000')
    SERVER_NAME = os.getenv('SERVER_NAME',HOST_URL.split('//')[1])
    WEBSITE_URL = os.getenv('WEBSITE_URL','http://localhost:4200')
    # Default to WEBSITE_URL for security. Use '*' only if explicitly set in environment
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', WEBSITE_URL)
    #DATABASE_URL = os.getenv('DATABASE_URL','sqlite:///store3d.sqlite3')
    BASE_URL = os.getenv('BASE_URL','/store3d/api/v1/')
    DATABASE_URL = ''
    DB_TYPE = os.getenv('DB_TYPE','sqlite')
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_DATABASE_NAME = os.getenv('DB_DATABASE_NAME')
    DB_CONNECTION_NAME = os.getenv('DB_CONNECTION_NAME')
    DB_HOST = os.getenv('DB_HOST','127.0.0.1:3306')
    VERSION = os.getenv('VERSION','1.0.0')
    # Database pool configuration - defaults optimized for development
    # For production, set higher values via environment variables
    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 10))  # Lower default for dev
    DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', 20))  # Lower default for dev
    DB_POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', 30))
    DB_POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', 3600))  # 1 hour
    # Common options for all databases
    db_common_options = {
        'pool_pre_ping': True,
        'json_serializer': lambda obj_json: json.dumps(obj_json, ensure_ascii=False),
        #'encoding': 'utf-8',
    }
    db_specific_options = {}

    # When deployed to App Engine, the `GAE_ENV` environment variable will be
    # set to `standard`
    if os.getenv('GAE_ENV') == 'standard':
        # If deployed, use the local socket interface for accessing Cloud SQL
        unix_socket = '/cloudsql/{}'.format(DB_CONNECTION_NAME)
        DATABASE_URL = 'mysql+pymysql://{}:{}@/{}?unix_socket={}&charset={}'.format(
            DB_USERNAME, DB_PASSWORD, DB_DATABASE_NAME, unix_socket,'utf8mb4')
        db_specific_options = {
            'pool_recycle': DB_POOL_RECYCLE,
            'pool_timeout':DB_POOL_TIMEOUT,
            'max_overflow':DB_MAX_OVERFLOW,
            'pool_size':DB_POOL_SIZE,
        }
    else:
        # If running locally, use the TCP connections instead
        # Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
        # so that your application can use 127.0.0.1:3306 to connect to your
        # Cloud SQL instance
        #host = '127.0.0.1'
        if DB_TYPE == 'sqlite':
            from sqlalchemy.pool import StaticPool
            DATABASE_URL = 'sqlite:///{}.sqlite3'.format(DB_DATABASE_NAME)
            db_specific_options = {
                'connect_args': {'check_same_thread': False},
                'poolclass': StaticPool
            }
        
        elif DB_TYPE == 'postgres':
            DATABASE_URL = 'postgresql+psycopg2://{}:{}@{}/{}'.format(
                DB_USERNAME, DB_PASSWORD, DB_HOST, DB_DATABASE_NAME)

        else:
            DATABASE_URL = 'mysql+pymysql://{}:{}@{}/{}?charset={}'.format(
                DB_USERNAME, DB_PASSWORD, DB_HOST, DB_DATABASE_NAME,'utf8mb4')
            db_specific_options = {
                'pool_recycle': DB_POOL_RECYCLE,
                'pool_timeout': DB_POOL_TIMEOUT,
                'max_overflow': DB_MAX_OVERFLOW,
                'pool_size': DB_POOL_SIZE,
            }
    #print(db_specific_options)
    engine = sql.create_engine('%s'%DATABASE_URL,**db_common_options, **db_specific_options)
    


class SecretKey(object):
    __skip__ = ['SECRET_KEY','SECURITY_PASSWORD_SALT']
    #DEBUG = os.getenv('DEBUG','True')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')
    
    # Validate that secrets are provided
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set. Please configure your .env file.")
    if not SECURITY_PASSWORD_SALT:
        raise ValueError("SECURITY_PASSWORD_SALT environment variable must be set. Please configure your .env file.")

class FileUploadConfig(object):
    UPLOAD_STORAGE = os.getenv('UPLOAD_STORAGE','LOCAL')
    CLOUD_STORAGE_ACCESS_KEY = os.getenv('CLOUD_STORAGE_ACCESS_KEY')
    CLOUD_STORAGE_SECRET_KEY = os.getenv('CLOUD_STORAGE_SECRET_KEY')
    CLOUD_STORAGE_BUCKET = os.getenv('CLOUD_STORAGE_BUCKET')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS',None)
    UPLOAD_FOLDER =  os.getenv('UPLOAD_FOLDER','uploads')
    UPLOAD_BASE_URL = os.getenv('UPLOAD_BASE_URL','/')
    ADD_FILENAME = str2bool(os.getenv('ADD_FILENAME',True))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','svg'])
    ALLOWED_CONTENT_TYPES = set(['text/plain', 'application/pdf', 'image/png', 'image/jpeg', 'image/gif', 'image/svg+xml'])


class MailConfig(object):
    # main config
    BCRYPT_LOG_ROUNDS = int(os.getenv('BCRYPT_LOG_ROUNDS',13))
    WTF_CSRF_ENABLED = str2bool(os.getenv('WTF_CSRF_ENABLED',True))
    DEBUG_TB_ENABLED = str2bool(os.getenv('DEBUG_TB_ENABLED',False))
    MAIL_DEBUG = str2bool(os.getenv('MAIL_DEBUG',False))
    DEBUG_TB_INTERCEPT_REDIRECTS = str2bool(os.getenv('DEBUG_TB_INTERCEPT_REDIRECTS',False))

    # mail settings
    MAIL_ENABLED = str2bool(os.getenv('MAIL_ENABLED',False))
    MAIL_SERVER =  os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT',587))
    MAIL_USE_TLS = str2bool(os.getenv('MAIL_USE_TLS',True))
    MAIL_USE_SSL = str2bool(os.getenv('MAIL_USE_SSL',False))
    MAIL_MAX_EMAILS = int(os.getenv('MAIL_MAX_EMAILS',10))

    # email authentication
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

    # mail accounts
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')


class OtherConfig(object):
    SWAGGER_ENABLED = str2bool(os.getenv('SWAGGER_ENABLED', True))
    

class LogConfig(object):
    # Logging Setup
    LOG_TYPE = os.getenv('LOG_TYPE', 'stream')  # Default is a Stream handler
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', 'text')  # Options: "json" or "text"

    # File Logging Setup
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    WWW_LOG_ENABLE = str2bool(os.getenv('WWW_LOG_ENABLE', True))
    APP_LOG_NAME = os.getenv('APP_LOG_NAME', 'app.log')
    WWW_LOG_NAME = os.getenv('WWW_LOG_NAME', 'www.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10 * 1024 * 1024))  # 10MB max log file size before rotation
    LOG_COPIES = int(os.getenv('LOG_COPIES', 5)) # Keep last 5 rotated logs

class SchedulerConfig(object):
    __skip__ = ['SCHEDULER_JOBSTORES','MemoryJobStore','RedisJobStore','SQLAlchemyJobStore', 'SCHEDULER_REDUIS_CLIENT','scheduler_redis_client','scheduler_job_store']
    #from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
    try:
        from apscheduler.jobstores.memory import MemoryJobStore
        SCHEDULER_ENABLED = str2bool(os.getenv('SCHEDULER_ENABLED', False))
        #SCHEDULER_JOBSTORES = {'default': SQLAlchemyJobStore(url=BaseConfig().DATABASE_URL)}
        SCHEDULER_REDIS_HOST = os.getenv('SCHEDULER_REDIS_HOST', 'localhost')
        SCHEDULER_REDIS_PORT = int(os.getenv('SCHEDULER_REDIS_PORT', 6379))
        SCHEDULER_REDIS_DB = int(os.getenv('SCHEDULER_REDIS_DB', 0))
        SCHEDULER_REDIS_PASSWORD = os.getenv('SCHEDULER_REDIS_PASSWORD', None)
        SCHEDULER_MODE = os.getenv('SCHEDULER_MODE', 'memory')
        
        SCHEDULER_JOBSTORES = {'default': MemoryJobStore()}

        SCHEDULER_EXECUTORS = {'default': {'type': 'threadpool', 'max_workers': 2}}
        SCHEDULER_JOB_DEFAULTS = {'coalesce': False, 'max_instances': 3}
        SCHEDULER_TIMEZONE = os.getenv('SCHEDULER_TIMEZONE', 'Asia/Muscat')
        SCHEDULER_REDUIS_CLIENT = None
        def scheduler_job_store(self):
            if self.SCHEDULER_MODE == 'redis':
                from apscheduler.jobstores.redis import RedisJobStore
                return {'default': RedisJobStore(
                    jobs_key='store3d.jobs', 
                    run_times_key='store3d.run_times', 
                    host=self.SCHEDULER_REDIS_HOST, 
                    port=self.SCHEDULER_REDIS_PORT, 
                    db=self.SCHEDULER_REDIS_DB, 
                    password=self.SCHEDULER_REDIS_PASSWORD, 
                    #prefix='apscheduler'
                    )}
            else:
                from apscheduler.jobstores.memory import MemoryJobStore
                return {'default': MemoryJobStore()}
        
        def scheduler_redis_client(self):
            import redis
            #print('------------------- create scheduler_redis_client')
            return redis.Redis(
                host=self.SCHEDULER_REDIS_HOST, 
                port=self.SCHEDULER_REDIS_PORT, 
                db=self.SCHEDULER_REDIS_DB, 
                password=self.SCHEDULER_REDIS_PASSWORD
                ) if self.SCHEDULER_MODE == 'redis' else None
        
        #SCHEDULER_API_ENABLED = True
        #SCHEDULER_API_PREFIX = '/scheduler'
        #SCHEDULER_ENDPOINT_PREFIX = 'scheduler.'
    except Exception as e:
        print(e)


class CachingConfig(object):
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'SimpleCache') # SimpleCache, RedisCache, MemcachedCache
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
    CACHE_IGNORE_ERRORS = str2bool(os.getenv('CACHE_IGNORE_ERRORS', True))
    CACHE_THRESHOLD = int(os.getenv('CACHE_THRESHOLD', 500))
    #CACHE_MEMCACHED_SERVERS = os.getenv('CACHE_MEMCACHED_SERVERS', '')
    #CACHE_MEMCACHED_USERNAME = os.getenv('CACHE_MEMCACHED_USERNAME', '')
    #CACHE_MEMCACHED_PASSWORD = os.getenv('CACHE_MEMCACHED_PASSWORD', '')
    CACHE_REDIS_HOST = os.getenv('CACHE_REDIS_HOST', 'localhost')
    CACHE_REDIS_PORT = int(os.getenv('CACHE_REDIS_PORT', 6379))
    CACHE_REDIS_PASSWORD = os.getenv('CACHE_REDIS_PASSWORD', None)
    CACHE_REDIS_DB = int(os.getenv('CACHE_REDIS_DB', 0))
    #CACHE_REDIS_SENTINELS = os.getenv('CACHE_REDIS_SENTINELS', '')
    #CACHE_REDIS_SENTINEL_MASTER = os.getenv('CACHE_REDIS_SENTINEL_MASTER', '')
    #CACHE_REDIS_CLUSTER = os.getenv('CACHE_REDIS_CLUSTER', '')
    #CACHE_REDIS_URL = os.getenv('CACHE_REDIS_URL', 'redis://localhost:6379/0')
    CACHE_KEY_PREFIX = os.getenv('CACHE_KEY_PREFIX', 'cache_')

class LimiterConfig(object):
    RATELIMIT_ENABLED = str2bool(os.getenv('RATELIMIT_ENABLED', True))
    RATELIMIT_HEADERS_ENABLED = str2bool(os.getenv('RATELIMIT_HEADERS_ENABLED', False))
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://') #'redis://localhost:6379/0'
    RATELIMIT_STRATEGY = os.getenv('RATELIMIT_STRATEGY', 'moving-window')
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '') #1000 per day
    RATELIMIT_KEY_PREFIX = os.getenv('RATELIMIT_KEY_PREFIX', 'rl_')


class OAuthConfig(object):
    # TWITTER
    OAUTH_TWITTER_CONSUMER_KEY = os.getenv('OAUTH_TWITTER_CONSUMER_KEY','******')
    OAUTH_TWITTER_CONSUMER_SECRET = os.getenv('OAUTH_TWITTER_CONSUMER_SECRET','******')
    OAUTH_TWITTER_CALLBACK = os.getenv('OAUTH_TWITTER_CALLBACK','http://localhost:4200/auth/twitter')
    #APPLE_CLIENT_ID = os.getenv('APPLE_CLIENT_ID','com.ryad.client')

    OAUTHLIB_INSECURE_TRANSPORT = os.getenv('OAUTHLIB_INSECURE_TRANSPORT', '1')
    OAUTH_LOGIN_ENABLED = os.getenv('OAUTH_LOGIN_ENABLED', True)
    # GOOGLE
    OAUTH_GOOGLE_CLIENT_ID = os.getenv('OAUTH_GOOGLE_CLIENT_ID', '----')
    OAUTH_GOOGLE_CLIENT_SECRET = os.getenv('OAUTH_GOOGLE_CLIENT_SECRET', '----')
    OAUTH_GOOGLE_AUTH_URI = os.getenv('OAUTH_GOOGLE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth')
    OAUTH_GOOGLE_TOKEN_URI = os.getenv('OAUTH_GOOGLE_TOKEN_URI', 'https://accounts.google.com/o/oauth2/token')
    OAUTH_GOOGLE_SCOPE = os.getenv('OAUTH_GOOGLE_SCOPE', ['openid','https://www.googleapis.com/auth/userinfo.profile','https://www.googleapis.com/auth/userinfo.email'])
    # APPLE
    OAUTH_APPLE_CLIENT_ID = os.getenv('OAUTH_APPLE_CLIENT_ID', '----')
    OAUTH_APPLE_CLIENT_SECRET = os.getenv('OAUTH_APPLE_CLIENT_SECRET', '----')

class ThawaniConfig(object):
    THAWANI_API_KEY = os.getenv('THAWANI_API_KEY','*****')
    THAWANI_PUBLISHABLE_KEY = os.getenv('THAWANI_PUBLISHABLE_KEY','*****')
    THAWANI_BASE_URL = os.getenv('THAWANI_BASE_URL','https://uatcheckout.thawani.om/api/v1')
    THAWANI_CHECKOUT_URL = os.getenv('THAWANI_CHECKOUT_URL','https://uatcheckout.thawani.om')
    WEBSITE_URL = os.getenv('WEBSITE_URL','https://store3d.example.com/')
    THAWANI_HEADERS = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'thawani-api-key': THAWANI_API_KEY
    }

class OMPayConfig(object):
    OMPAY_API_KEY = os.getenv('OMPAY_API_KEY','******')
    OMPAY_PUBLISHABLE_KEY = os.getenv('OMPAY_PUBLISHABLE_KEY','*****')
    OMPAY_BASE_URL = os.getenv('OMPAY_BASE_URL','https://api.uat.gateway.ompay.com')
    OMPAY_CHECKOUT_URL = os.getenv('OMPAY_CHECKOUT_URL','https://api.uat.gateway.ompay.com')
    WEBSITE_URL = os.getenv('WEBSITE_URL','https://store3d.example.com/')
    WEBHOOK_URL = os.getenv('WEBHOOK_URL','https://store3d.example.com/')
    OMPAY_HEADERS = {
        'Content-Type': 'application/json',
    }
    OMPAY_CLIENT_ID = '******'
    OMPAY_CLIENT_SECRET = '******'

class ThreadConfig(BaseConfig):
    """Thread-specific configuration"""
    pass
