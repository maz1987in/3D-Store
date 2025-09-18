from ._common import build_service_paths

def build_paths(schema_name: str, coll: str, id_param: str):
    return build_service_paths(schema_name, "sales", coll, id_param)
