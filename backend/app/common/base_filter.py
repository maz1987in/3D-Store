
class Filter(object):
    def __init__(self):
        self.reset()
    def reset(self):
        page = 1
        per_page = 10
        sort = None
        sort_order = None #asc
        queries = None
    
    page = 1
    per_page = 10
    sort = None
    sort_order = None #asc
    queries = None
    sorters = []
    filters = []

    from_record = page * per_page - per_page
    to_record = page * per_page
