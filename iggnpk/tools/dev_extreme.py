import simplejson as json
from datetime import datetime
from django.db.models import Q


def filtered_query(request, query, distinct_field=None):

    if 'skip' in request.GET:
        start = int(request.GET['skip'])
    else:
        start = 0
    if 'take' in request.GET:
        end = int(request.GET['skip']) + int(request.GET['take'])
    else:
        end = query.count()
    if 'filter' in request.GET:
        """"[["id","=",1],"and",["!",["doc_number","=","+2664Л-1"]]]"""
        q = build_q_object(json.loads(request.GET['filter']))
        query = query.filter(q)
    if 'searchValue' in request.GET:
        field = request.GET['searchExpr'].replace("\"", "")
        value = request.GET['searchValue'].replace("\"", "")
        query = query.filter(Q(**{field+'__icontains': value}))
    if 'sort' in request.GET:
        sort = json.loads(request.GET['sort'])[0]
        order_by = sort['selector']
        desc = sort['desc']
        if desc:
            order_by = '-' + order_by
    else:
        order_by = 'id'
    if distinct_field:
        distinct_field = distinct_field.replace('.', '__')
        query = query.distinct(distinct_field)
    return query.order_by(order_by)[start:end], query, query.count()


def build_q_object(filter_request):
    """
    :param query: QuerySet
    :param filter_request: [
                            ["id","=",1],
                            "and",
                            ["!",["doc_number","="," 2664Л-1"]],
                            "and",
                            [
                                [
                                    ["doc_date",">=","2015/09/29"],
                                    "and",
                                    ["doc_date","<","2015/09/30"]
                                ],
                                "or",
                                [
                                    ["doc_date",">=","2017/01/01"],
                                    "and",
                                    ["doc_date","<","2018/01/01"]
                                ]
                            ]
                            ]
    :return: Q object
    """
    result = None
    a = None
    operator = None
    for i in range(0, len(filter_request)):
        if type(filter_request[i]) is list:
            temp = build_q_object(filter_request[i])
            if result is None:
                if operator == '!':
                    temp = ~temp
                a = result = temp
                continue
        else:
            temp = filter_request[i]

        if temp == '!':
            operator = temp
        elif a is None:
            a = temp
        elif operator is None:
            operator = temp
        else:
            if type(a) is str:
                a = a.replace('.', '__')
                try:
                    temp = datetime.strptime(str(temp), '%Y/%m/%d').strftime('%Y-%m-%d')
                except ValueError:
                    pass
                if operator == 'contains':
                    a = a + '__icontains'
                elif operator == '<':
                    a = a + '__lt'
                elif operator == '<=':
                    a = a + '__lte'
                elif operator == '>':
                    a = a + '__gt'
                elif operator == '>=':
                    a = a + '__gte'
                return Q(**{a: temp})
            else:
                if operator == 'and':
                    result = result & temp
                elif operator == 'or':
                    result = result | temp
                operator = None
    return result


def populate_group_category(request, queryset):
    """

    :param groups: [{'selector': 'doc_date', 'groupInterval': 'year', 'isExpanded': True},
    {'selector': 'doc_date', 'groupInterval': 'month', 'isExpanded': True},
    {'selector': 'doc_date', 'groupInterval': 'day', 'isExpanded': False}]
    :param query: QuerySet
    :return:
        {'key': 'group1',
        'items': {
            'key': 'subgroup1',
            items: None,
            count: 22}
        }
    """
    groups = json.loads(request.GET['group'])
    result = []
    selector = groups[0]['selector']
    selector = selector.replace('.', '__')
    items, totalItems, count = filtered_query(request, queryset, selector)
    if 'groupInterval' in groups[0]:
        if groups[0]['groupInterval'] == 'year':
            for item in items:
                year = -1
                month = -1
                if hasattr(item, selector) and item.__getattribute__(selector):
                    for y in range(0, len(result)):
                        if result[y]['key'] == item.__getattribute__(selector).year:
                            year = y
                            break
                    if year == -1:
                        year = len(result)
                        result.append({'key': item.__getattribute__(selector).year, 'items': []})
                    for m in range(0, len(result[year]['items'])):
                        if result[year]['items'][m]['key'] == item.__getattribute__(selector).month:
                            month = m
                            break
                    if month == -1:
                        month = len(result[year]['items'])
                        result[year]['items'].append({'key': item.__getattribute__(selector).month, 'items': []})

                    result[year]['items'][month]['items'].append(
                        {'key': item.__getattribute__(selector).day, 'items': None})
    else:
        for item in items.values(selector):
            result.append({'key': item[selector], 'items': None, 'count': 1})
    return result, count
