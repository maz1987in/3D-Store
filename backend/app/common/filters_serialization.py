
def get_pagination_serialization(pagination,sort,sort_order,queries):
    data = {}
    if pagination:
         data['page_size'] = pagination.page_size
         data['page_number'] = pagination.page_number
         data['num_pages'] = pagination.num_pages
         data['total_results'] = pagination.total_results
    if sort:
        data['sort'] = sort
    if sort_order:
        data['sort_order'] = sort_order
    if queries:
        data['queries'] = queries
    return data

def get_es_serialization(page_number,page_size,num_pages,total_results,sort,sort_order,queries):
    data = {}
    data['page_number'] = page_number
    data['page_size'] = page_size
    data['num_pages'] = num_pages
    data['total_results'] = total_results
    if sort:
        data['sort'] = sort
    if sort_order:
        data['sort_order'] = sort_order
    if queries:
        data['queries'] = queries
    return data
