
def get_limit(request):
    limit = request.REQUEST.get('limit', 0)
    start = request.REQUEST.get('start', 0)
    
    try:
        return (int(start), int(limit))
    except:
        return (0, 50)
    
def get_sort(request):
    dir = request.REQUEST.get('dir')
    field = request.REQUEST.get('sort')
    if dir == 'DESC':
        field = '-%s' % (field)
    return field

def generate_grid_rows_json(request, grid, qs, filters=[]):
    """
    generate a filtered & limited queryset
    example filters: 
        filters = [('unit_name', 'unit__name'), 'username']
    """
    (start, limit) = get_limit(request)
    for item in filters:
        if type(item) == type((1,1)):
            param, new_param = item
            value = request.REQUEST.get(param, None)
            if value:
                kwargs = {'%s__%s' % (str(new_param), 'icontains'): value,}
                qs = qs.filter(**kwargs)
        else:
            value = request.REQUEST.get(item, None)
            if value:
                kwargs = {'%s__%s' % (str(item), 'icontains'): value,}
                qs = qs.filter(**kwargs)
    # Sort time
    if 'sort' in request.REQUEST:
        dj_sort = 'id'
        sort = request.REQUEST.get('sort')
        for item in filters:
            if type(item) == type((1,1)):
                param, new_param = item
                if param == sort:
                    dj_sort = new_param
                value = request.REQUEST.get(param, None)
                if value:
                    kwargs = {'%s__%s' % (str(new_param), 'icontains'): value,}
                    qs = qs.filter(**kwargs)
            else:
                if item == sort:
                    dj_sort = item
        if 'dir' in request.REQUEST:
            direction = request.REQUEST.get('dir')
            if direction == 'DESC':
                dj_sort = '-%s' % (dj_sort)
        qs = qs.order_by(dj_sort)

    return grid.get_rows_json(qs, start=start, limit=limit)
    