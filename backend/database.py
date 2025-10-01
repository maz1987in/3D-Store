#from sqlalchemy import create_engine
import os
import importlib
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import BaseConfig

try:
    from greenlet import getcurrent as _get_ident  # type: ignore
except ImportError:
    from threading import get_ident as _get_ident  # type: ignore


engine = BaseConfig().engine
session_factory = sessionmaker(bind=engine)#autocommit=False, autoflush=False, 
Session = scoped_session(session_factory, scopefunc=_get_ident)
Base = declarative_base()
Base.query = Session.query_property()

def init_model():
    #: The base path to search for additional applications.
    # pylint: disable=invalid-name
    base_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            'app'
        )
    )

    for candidate in os.listdir(base_path):

        # Must be a directory.
        if not os.path.isdir(os.path.join(base_path, candidate)):
            continue

        if os.path.exists(os.path.join(base_path, candidate,'model.py')):
            mod_name = 'app.' + candidate + '.model'
            importlib.import_module(mod_name)

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    init_model()
    Base.metadata.create_all(bind=engine, checkfirst=True)