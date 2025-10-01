#For read logs of the application 
import json
from flask_cors import CORS, cross_origin
from flask import Blueprint, current_app, request, jsonify, abort, make_response, Response

from app.security import roles, permissions
from app.common import filters
from time import sleep
from flask.templating import render_template
from pygtail import Pygtail
import time
from config import FileUploadConfig, LogConfig
from .service import AdminService



__uri__ = 'admins'
__blueprint__ = 'admins'

admins = Blueprint(__uri__, __name__)

service = AdminService()

@admins.route('/log', methods=['GET'])
@permissions.has_permission(["admin.log"])
def logs(self):
    """log page"""
    return render_template("logs.html",log_config = LogConfig())

@admins.route('/local/log_stream/<log_type>')
@permissions.has_permission(["admin.log"])
def get_log_stream(self,log_type=None):
    path = LogConfig().LOG_DIR
    if log_type == None:
            log_type = path+'/'+LogConfig().WWW_LOG_NAME
    else:
        log_type = path+'/'+log_type
    
    def generate(log_type):
        pygtail = Pygtail(str(log_type), every_n=5,read_from_end=True)
        for line in pygtail:
            if 'log_stream' not in line:
                yield "data:" + str(line) + "\n\n"
                time.sleep(0.5)
    return Response(generate(log_type), mimetype= 'text/event-stream')


@admins.route('/jobs', methods=['GET'])
@permissions.has_permission(["admin.monitors"])
def jobs(self):
    jobs, status = service.get_jobs()
    return jsonify({'jobs': jobs}), status

