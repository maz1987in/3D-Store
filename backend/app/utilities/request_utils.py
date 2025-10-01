from flask import current_app
from config import BaseConfig, FileUploadConfig
from decimal import Decimal
from datetime import timezone

def is_exisit_in_request(data, param):
    if param not in data or data[param] is None:
        return False
    else :
        return True

def not_exisit_in_request(data, param, default=None):
    try:
        if param not in data or data[param] is None:
            return default
        else:
            # .strip() to remove white space if string
            if isinstance(data[param], str):
                return data[param].strip()
            else:
                return data[param]
    except Exception as e:
        current_app.logger.error(e)
        #print(param)
        #print(e)
        return default

def none_to_empty(value):
    if value is None:
        return None
    elif len(value) == 0:
        return None
    else:
        return value

def str_to_bool(data, param, default=False):
    if param not in data or data[param] is None:
        return default
    else :
        if isinstance(data[param], str):
            return True if data[param].lower() in ['true','1'] else False
        else:
            return True if data[param] == True else False

def str_to_float(data, param, default=0.0):
    try:
        if param not in data or data[param] is None:
            return default
        else :
            return float(data[param])
    except Exception as e:
        #print(param)
        #print(e)
        return default

def get_media_url(file, add_file_name=True):
    if FileUploadConfig.ADD_FILENAME == False:
        add_file_name = False
    files_url = {}
    try:
        if file == None:
            return files_url if files_url else None
        if '_public_url' in file and file['_public_url'] != None:
            files_url.update({'file':file['_public_url']})
        else:
            path = file['path']
            files_url.update({'file':BaseConfig.HOST_URL + FileUploadConfig.UPLOAD_BASE_URL + FileUploadConfig.UPLOAD_FOLDER + '/' + path + ('/' + file['filename'] if add_file_name else '')})
        if '_thumb_public_url' in file and file['_thumb_public_url'] != None:
            files_url.update({'thumb':file['_thumb_public_url']})
        else:
            if 'thumb_path' in file and file['thumb_path'] != None:
                path = file['thumb_path']
                files_url.update({'thumb':BaseConfig.HOST_URL + FileUploadConfig.UPLOAD_BASE_URL + FileUploadConfig.UPLOAD_FOLDER + '/' + path + ('/' + file['filename'] if add_file_name else '')})
        return files_url if files_url else None
    except Exception as e:
        current_app.logger.error(e)
        current_app.logger.error(file)
        return files_url if files_url else None

def amount_with_digits_str(amount,digits=3):
    dec = round(Decimal(amount), digits)
    return str(dec)
def amount_with_digits(amount,digits=3):
    dec = round(Decimal(amount), digits)
    return dec

def date_to_string(dt_time):
    from random import randint
    return str(dt_time.year) + '{:02d}'.format(dt_time.month) + '{:02d}'.format(dt_time.day) + '{:02d}'.format(dt_time.hour) + '{:02d}'.format(dt_time.minute) + '{:02d}'.format(dt_time.second) + str(randint(100, 999)) #+ str(dt_time.microsecond)

# dump request
def dump_request(request):
    import datetime
    req_data = {}
    req_data['timestamp'] = datetime.datetime.now(timezone.utc)
    req_data['endpoint'] = request.endpoint if request.endpoint else None
    req_data['method'] = request.method if request.method else None
    req_data['cookies'] = request.cookies if request.cookies else None
    req_data['data'] = request.data if request.data else None
    req_data['headers'] = dict(request.headers) if request.headers else None
    req_data['headers'].pop('Cookie', None) if req_data['headers'] else None
    req_data['args'] = request.args if request.args else None
    req_data['form'] = request.form if request.form else None
    req_data['remote_addr'] = request.remote_addr if request.remote_addr else None
    req_data['url'] = request.url if request.url else None
    req_data['base_url'] = request.base_url if request.base_url else None
    req_data['path'] = request.path if request.path else None
    req_data['full_path'] = request.full_path if request.full_path else None
    req_data['query_string'] = request.query_string if request.query_string else None
    req_data['host_url'] = request.host_url if request.host_url else None
    req_data['host'] = request.host if request.host else None
    req_data['scheme'] = request.scheme if request.scheme else None
    #req_data['is_xhr'] = request.is_xhr if request.is_xhr else None
    req_data['is_secure'] = request.is_secure if request.is_secure else None
    req_data['is_json'] = request.is_json if request.is_json else None
    req_data['max_content_length'] = request.max_content_length if request.max_content_length else None
    req_data['content_length'] = request.content_length if request.content_length else None
    req_data['content_type'] = request.content_type if request.content_type else None
    req_data['mimetype'] = request.mimetype if request.mimetype else None
    req_data['mimetype_params'] = request.mimetype_params if request.mimetype_params else None
    req_data['json'] = request.json if request.json else None
    req_data['view_args'] = request.view_args if request.view_args else None
    #req_data['environ'] = request.environ if request.environ else None
    return req_data