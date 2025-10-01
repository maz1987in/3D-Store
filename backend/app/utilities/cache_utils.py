from extensions import cache

def to_int(value):
    try:
        return int(value)
    except ValueError as ve:
        return 0
    except Exception as e:
        print(e)
        return 0
def key_to_str(key):
    try:
        prefix = 'custem_'
        key = str(key)
        key = key.replace('-', '')
        key = prefix + key
        return key
    except Exception as e:
        print(e)
        return key
