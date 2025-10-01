from alembic.command import upgrade
from alembic.config import Config
import os


def db_migrations():
    # retrieves the directory that *this* file is in
    migrations_dir = os.path.dirname(os.path.realpath(__file__))
    alembic_dir = os.path.join(migrations_dir, 'alembic')
    # this assumes the alembic.ini is also contained in this same directory
    config_file = os.path.join(migrations_dir, "alembic.ini")
    config = Config(file_=config_file)
    config.set_main_option("script_location", alembic_dir)

    # upgrade the database to the latest revision
    upgrade(config, "head")
