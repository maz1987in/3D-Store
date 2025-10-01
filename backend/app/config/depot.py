import json
import os
from depot.manager import DepotManager
from flask import Flask
from config import FileUploadConfig

FOLDERS_DEPOT = ['avatar', 'media', 'ads', 'user', 'product', 'slider', 'icon', 'logo', 'temp', 'staff', 'expense']
DEPOT_NAMES = {name: {'depot.prefix': f'{name}s/'} for name in FOLDERS_DEPOT}


def init_depots(app: Flask):
    app.config['credentials'] = None
    temp_name = ''
    try:
        setup_credentials(app)
        for (name, special_config) in DEPOT_NAMES.items():
            #app.logger.info('Depot name: ' + name)
            temp_name = name
            config = default_config(app, name)
            if app.config['UPLOAD_STORAGE'] != 'LOCAL':
                config.update(special_config)
            retry = 0
            while retry < 3:
                try:
                    DepotManager.configure(name, config)
                    break
                except Exception as e:
                    #app.logger.error(e)
                    retry += 1
                    #app.logger.info('Depot: {0} - Retry: {1}'.format(name, retry))
            else:
                app.logger.error('DepotManager.configure failed for ' + name)

    except Exception as e:
        app.logger.error(temp_name)
        app.logger.error(e)



def setup_credentials(app: Flask):
    if app.config['UPLOAD_STORAGE'] == 'GCP':
        # set environment variable GOOGLE_APPLICATION_CREDENTIALS to point to a file
        # or set GOOGLE_APPLICATION_CREDENTIALS to a JSON string
        #os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = json.loads(FileUploadConfig.GOOGLE_APPLICATION_CREDENTIALS.replace("'", '"'))
       
        from google.oauth2 import service_account
        if FileUploadConfig.GOOGLE_APPLICATION_CREDENTIALS:
            credentials_path = FileUploadConfig.GOOGLE_APPLICATION_CREDENTIALS
            if credentials_path.endswith('.json'):
                if not os.path.isfile(credentials_path):
                    app.logger.info('GOOGLE_APPLICATION_CREDENTIALS environment variable does not point to a file')
                app.config['credentials'] = service_account.Credentials.from_service_account_file(credentials_path)
            else:
                # Replace single quotes with double quotes before loading JSON data
                credentials_json = credentials_path.replace("'", '"')
                app.config['credentials'] = service_account.Credentials.from_service_account_info(json.loads(credentials_json))
        else:
            app.logger.info('GOOGLE_APPLICATION_CREDENTIALS environment variable not set or empty')
        



def default_config(app: Flask, name):
    #app.logger.info('UPLOAD_STORAGE: ' + app.config['UPLOAD_STORAGE'])

    config_functions = {
        'LOCAL': local_config,
        'GCP': gcp_config,
        'AWS': aws_config,
        'TEST': test_config
    }

    return config_functions.get(app.config['UPLOAD_STORAGE'], test_config)(app, name)


def test_config(app: Flask, name):
    return {'depot.backend': 'depot.io.memory.MemoryFileStorage'}


def local_config(app: Flask, name):
    return {'depot.storage_path': os.path.join(app.config['UPLOAD_FOLDER'], name)}


def gcp_config(app: Flask, name):
    if app.config['credentials'] is None:
        app.logger.error('credentials is None')
    return {
        'depot.backend': 'depot.io.gcs.GCSStorage',
        'depot.credentials': app.config['credentials'],
        'depot.bucket': app.config['CLOUD_STORAGE_BUCKET']
    }


def aws_config(app: Flask, name):
    return {
        'depot.backend': 'depot.io.boto3.S3Storage',
        'depot.access_key_id': app.config['CLOUD_STORAGE_ACCESS_KEY'],
        'depot.secret_access_key': app.config['CLOUD_STORAGE_SECRET_KEY'],
        'depot.bucket': app.config['CLOUD_STORAGE_BUCKET']
    }


def make_middleware(app):
    upload = '/' + app.config['UPLOAD_FOLDER']
    app.wsgi_app = DepotManager.make_middleware(app.wsgi_app, mountpoint=upload, cache_max_age=604800, replace_wsgi_filewrapper=True)

    @app.route(upload + '/<path:text>', methods=['OPTIONS'])
    def options(text):
        return 'ok', 200
