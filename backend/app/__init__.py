import logging
from flask import Flask, request, jsonify
from datetime import datetime, timezone
from app.utilities.config_utils import set_conf_dict
from database import init_db
from app.utilities.db_utils import get_session_with_retries
from extensions import logs, cache, mail, limiter, scheduler, middleware, cache_extension, monitoring_extension # ext_celery
from sqlalchemy_i18n import make_translatable
from flask_cors import CORS, cross_origin
import os
import importlib
from app.exceptions import register_error_handlers
from app.middleware.extension import MiddlewareExtension
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


def create_app():
    app = Flask(__name__)

    

    app.json.ensure_ascii = False  # <-- this line saves the day
    app.json.mimetype = "application/json; charset=utf-8"  # <-- this could be also useful
    setup_config(app)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)    

    make_translatable(options={
        'locales': list(app.config['AVAILABLE_LOCALES'].keys()),
    })

    app.debug = bool(app.config['DEBUG'])
    init_db()
    app.logger.info('Database initialized.')
    setup_db_session(app)
    #setup_setting_from_db(app)
    setup_config_from_db(app)
    # Initialize Sentry
    if app.config['SENTRY']:
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            traces_sample_rate=app.config['SENTRY_TRACES_SAMPLE_RATE'],
            send_default_pii=True,
            profile_session_sample_rate=1.0,
            profile_lifecycle="trace",
            integrations=[FlaskIntegration()]
        )
    set_logger_lib_level(app)
    register_extensions(app)
    app.logger.info('Extensions initialized.')
    errorhandler(app)
    app.logger.info('Error handlers registered.')

    # logging
    if app.config['WWW_LOG_ENABLE']:
        setup_log(app)
        app.logger.info('Logging initialized.')
    
    

    with app.app_context():
        register_blueprints_dynamic(app)
        register_blueprints(app)
        if app.config['SCHEDULER_ENABLED'] == True:
            scheduler.start() #scheduler start
            app.logger.info('Scheduler Started')

    setup_depots(app)
    app.logger.info('Depots initialized.')

    # swagger
    if app.config['SWAGGER_ENABLED']:
        setup_swagger(app)
        app.logger.info('Swagger initialized.')

    # Register error handlers
    register_error_handlers(app)

    return app

def setup_db_session(self):
    @self.teardown_appcontext
    def cleanup(resp_or_exc):
        """
        Cleanup database sessions after each request.
        """
        try:
            session = get_session_with_retries()
            if session.is_active:
                session.close()
        except Exception as e:
            print(f"Error during session cleanup: {e}")
    
    @self.teardown_request
    def session_clear(exception=None):
        #Session.remove()
        #if exception and Session.is_active:
        #    Session.rollback()
        if get_session_with_retries().is_active:
            get_session_with_retries().close()
        #Session.remove()
        #print('(session_clear) Session removed')
        


def setup_log(app):
    """Setup request logging if enabled."""
    if not app.config.get("WWW_LOG_ENABLE", True):  # Default to True if not set
        return

    @app.after_request
    def after_request(response):
        """Logging after every request."""
        logger = logging.getLogger("access-log")
        log_format = app.config.get("LOG_FORMAT").lower()
        if "/admins/log" not in request.path:
            log_data = {
                "remote_addr": request.remote_addr,
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "method": request.method,
                "path": request.path,
                "scheme": request.scheme,
                "status": response.status,
                "content_length": response.content_length,
                "referrer": request.referrer,
                "user_agent": request.user_agent.string,
            }
            if log_format == "json":
                logger.info("HTTP Request", **log_data)
            else:
                log_text = " | ".join([f"{key}={value}" for key, value in log_data.items()])
                logger.info(log_text)
        return response
    
def register_blueprints(self):
    """Register all blueprints"""
    from .security.login import login, signup
    from .security.auth import auth
    from .utilities.email import mails
    from .common.health import common

    self.register_blueprint(common, url_prefix=self.config['BASE_URL'])#+ "common"
    self.register_blueprint(auth, url_prefix=self.config['BASE_URL'] + "auth")
    self.register_blueprint(signup, url_prefix=self.config['BASE_URL'] + "signup")
    self.register_blueprint(login, url_prefix=self.config['BASE_URL'] + "login")  
    self.register_blueprint(mails, url_prefix=self.config['BASE_URL'] + "email")
    #print(f"BASE_URL: {self.config['BASE_URL']}")
    # prtint all registered blueprints
    #print(f"Registered blueprints: {self.url_map._rules}")
    #print(f"Registered blueprints: {self.url_map._rules_by_endpoint}")

def register_blueprints_dynamic(self):
    #: The base path to search for additional applications.
    # pylint: disable=invalid-name
    base_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '.'
        )
    )

    for candidate in os.listdir(base_path):
        # Must be a directory.
        if not os.path.isdir(os.path.join(base_path, candidate)):
            continue

        if os.path.exists(os.path.join(base_path, candidate,'routes.py')):
            mod_name = f'app.{candidate}.routes'

            module = importlib.import_module(mod_name)
            mod = __import__(mod_name, fromlist=[getattr(module,'__blueprint__')])
            klass = getattr(mod, getattr(module,'__blueprint__'))
            if hasattr(module, '__blueprint__'):
                self.register_blueprint(klass, url_prefix=self.config['BASE_URL']+module.__uri__)
        
        if os.path.exists(os.path.join(base_path, candidate,'tasks.py')):
            mod_name = 'app.'+candidate + '.tasks'
            module = importlib.import_module(mod_name)
            
def register_extensions(app):
    try:
        logs.init_app(app) #logs
        if app.config['SCHEDULER_ENABLED']:
            from config import SchedulerConfig
            SchedulerConfig.SCHEDULER_JOBSTORES = SchedulerConfig().scheduler_job_store()
            app.config['SCHEDULER_JOBSTORES'] = SchedulerConfig.SCHEDULER_JOBSTORES
            SchedulerConfig.SCHEDULER_REDUIS_CLIENT = SchedulerConfig().scheduler_redis_client()
            app.config['SCHEDULER_REDUIS_CLIENT'] = SchedulerConfig.SCHEDULER_REDUIS_CLIENT
            scheduler.init_app(app)
            #scheduler.app = self
            app.logger.info('scheduler initialized')

            #logging.getLogger("apscheduler").setLevel(logging.INFO) #scheduler log level
            #scheduler.start() #scheduler start
        cache.init_app(app) # Cache
        app.logger.info('cache initialized')
        mail.init_app(app)# Initialize Flask-Mail
        app.logger.info('mail initialized')
        limiter.init_app(app)
        app.logger.info('limiter initialized')
        middleware.init_app(app) # Initialize middleware system
        app.logger.info('middleware system initialized')
        cache_extension.init_app(app) # Initialize cache extension
        app.logger.info('cache extension initialized')
        
        monitoring_extension.init_app(app) # Initialize monitoring extension
        app.logger.info('monitoring extension initialized')
        #thread_pool.start()
    except Exception as e:
        app.logger.error(e)
        pass
    

def setup_depots(self):
    """Setup the file depots"""
    try:
        from .config import depot
        depot.init_depots(self)
        depot.make_middleware(self)
    except Exception as e:
        self.logger.error(e)
        pass

def setup_swagger(self):
    from flask_swagger_ui import get_swaggerui_blueprint

    SWAGGER_URL = '/api/docs'  # URL for exstore3ding Swagger UI (without trailing '/')
    API_URL = '/static/swagger.yaml'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
        API_URL,
        config={  # Swagger UI config overrides
            'app_name': "Store3d API"
        },
    )
    #self.register_blueprint(swagger, url_prefix="/project/swagger")
    self.register_blueprint(swaggerui_blueprint)
    

def setup_config(self):
    self.config.from_object('config.Config')
    self.config.from_object('config.BaseConfig')
    self.config.from_object('config.SecretKey')
    self.config.from_object('config.LogConfig')
    self.config.from_object('config.MailConfig')
    self.config.from_object('config.FileUploadConfig')
    self.config.from_object('config.OtherConfig')
    self.config.from_object('config.SchedulerConfig')
    self.config.from_object('config.CachingConfig')
    self.config.from_object('config.ThreadConfig')
    self.config.from_object('config.OAuthConfig')
    self.logger.info('Done setting up config from config.py file.')

def setup_config_from_db(app):
    """
    Load configuration from the database and set it in the Flask app config.
    """
    from .setting.service import SettingService
    service = SettingService()

    # Use app.app_context() to ensure current_app is available
    with app.app_context():
        config = service.get_setting_for_config()
        config_dict = set_conf_dict(config)

        for key in config_dict:
            app.config[key] = config_dict[key]


def errorhandler(app):
    from app.common.error_handling import QueryValidationError

    @app.errorhandler(QueryValidationError)
    def handle_query_validation_error(err):
        app.logger.error(f"QueryValidationError: {err}")
        return jsonify(dict(
            errors=[dict(
                title="Invalid filter",
                details=str(err),
                status="400")
            ]
        )), 400

    @app.errorhandler(429)
    def ratelimit_handler(e):
        app.logger.warning("Rate limit exceeded")
        return jsonify({'message': 'Too many requests, please try again later.'}), 429

def set_logger_lib_level(self):
    logging.getLogger('socketio').setLevel(logging.ERROR)
    logging.getLogger('engineio').setLevel(logging.ERROR)
    #logging.getLogger("apscheduler").setLevel(logging.ERROR) #scheduler log level
    logging.getLogger('twilio.http_client').setLevel(logging.ERROR)

    if self.debug:
        logging.getLogger('flask_cors').setLevel(logging.ERROR)
