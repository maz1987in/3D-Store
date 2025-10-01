
import ast
import inspect
import sys

from config import str2bool


# Read all the conf "conf.py" and return a dictionary of all the conf values in each class in the file

def get_conf_dict(config="config"):
    conf_dict = {}
    conf = __import__(config)
    for name, obj in inspect.getmembers(conf):
        if inspect.isclass(obj):
            # skip and key in __skip__ list in obj class
            conf_dict[name] = {}
            skip = []
            if hasattr(obj, '__skip__'):
                skip = obj.__skip__
            for key, value in inspect.getmembers(obj):
                if not key.startswith('__') and key not in skip:
                    conf_dict[name][key] = value
                    #print(name, key, value)
    return conf_dict

# set the conf values in the conf.py file from the dictionary
def set_conf_dict(conf_dict):
    #print(conf_dict)
    config = {}
    conf = __import__("config")
    for name, obj in inspect.getmembers(conf):
        if inspect.isclass(obj):
            skip = []
            if hasattr(obj, '__skip__'):
                skip = obj.__skip__
            # if the class name is in the conf_dict then set the values
            if name in conf_dict:
                for key, value in inspect.getmembers(obj):
                    # skip class members that start with __ and members in the __skip__ list and members of class type
                    if not key.startswith('__') and key not in skip:
                        if key in conf_dict[name]:
                            #print(name, key,value, conf_dict[name][key], type(value))
                            # convert the value to the type of the value in the conf.py file
                            if type(value) == int:
                                conf_dict[name][key] = int(conf_dict[name][key])
                            elif type(value) == float:
                                conf_dict[name][key] = float(conf_dict[name][key])
                            elif type(value) == bool:
                                conf_dict[name][key] = str2bool(conf_dict[name][key])
                            #elif type(value) == list:
                            #    conf_dict[name][key] = list(conf_dict[name][key])
                            elif type(value) == dict:
                                conf_dict[name][key] = ast.literal_eval(conf_dict[name][key])
                            elif type(value) == tuple:
                                conf_dict[name][key] = tuple(conf_dict[name][key])
                            #elif type(value) == set:
                            #    conf_dict[name][key] = set(conf_dict[name][key])
                            config[key] = conf_dict[name][key]
                            #print(conf_dict[name][key])
                            setattr(obj, key, conf_dict[name][key])
    return config
