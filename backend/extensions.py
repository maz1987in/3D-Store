
from flask_logs import LogSetup
logs = LogSetup()

# Scheduler 
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
#from apscheduler.schedulers.blocking import BlockingScheduler
#scheduler = APScheduler()
scheduler = APScheduler(BackgroundScheduler())
#scheduler = APScheduler(BlockingScheduler())
# = BlockingScheduler()


# Caching 
from flask_caching import Cache
cache = Cache()

# EMail 
from flask_mail import Mail
mail = Mail()

# DebugToolbar
#from flask_debugtoolbar import DebugToolbarExtension
#toolbar = DebugToolbarExtension()

# Flask-Limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import LimiterConfig
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    headers_enabled=LimiterConfig.RATELIMIT_HEADERS_ENABLED,
    strategy=LimiterConfig.RATELIMIT_STRATEGY,
    storage_uri=LimiterConfig.RATELIMIT_STORAGE_URL
    )

# Celery
'''
from flask_celeryext import FlaskCeleryExt
from app.utilities.celery_utils import make_celery
ext_celery = FlaskCeleryExt(create_celery_app=make_celery)
'''

# ThreadPools
"""
from app.common.thread_pool import ThreadPool
from config import ThreadConfig
thread_pool = ThreadPool(ThreadConfig.THREAD_POOL_NUMBER)
"""

# Middleware System
from app.middleware.extension import MiddlewareExtension
middleware = MiddlewareExtension()

# Cache System
from app.caching.extension import CacheExtension
cache_extension = CacheExtension()

# Monitoring System
# TODO: Implement monitoring extension module
# from app.monitoring.extension import MonitoringExtension
# monitoring_extension = MonitoringExtension()
monitoring_extension = None  # Placeholder until monitoring module is implemented