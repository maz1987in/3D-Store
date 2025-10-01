from flask import request
from functools import wraps
from app.common.base_filter import Filter
from app.common.queries import create_filters, create_sorters


def filters(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        # Filter filter
        _filter = Filter()
        if request.args:
            request_args = request.args

            if "page" in request_args:
                _filter.page = request_args["page"]
            if "per_page" in request_args:
                _filter.per_page = request_args["per_page"] if int(request_args["per_page"]) > 0 else 10
            if "sort_order" in request_args:
                _filter.sort_order = request_args["sort_order"]
            if "sort" in request_args:
                sorters = create_sorters(request_args["sort"], request_args.get("sort_order", 'asc'))
                _filter.sorters = sorters
                _filter.sort = request_args["sort"]
                if "sort_order" not in request_args:
                    _filter.sort_order = 'desc'
            if "queries" in request_args:
                filters = create_filters(request_args.getlist("queries"))
                _filter.filters = filters
                _filter.queries = request_args.getlist("queries")

        return f(_filter, *args, **kwargs)
    return decorator
