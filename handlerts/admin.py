import json
import pymorphy2
morph = pymorphy2.MorphAnalyzer()

def create_sql_query(text, columns_names, table_name):
    from nltk.tokenize import word_tokenize

    tokens = word_tokenize(text, language="russian")

    names_list = []

    for token in tokens:
        if token in columns_names:
            names_list.append(token)

    lemma_tokens = []
    grammems = []
    for word in tokens:
        p = morph.parse(word)[0]
        lemma_tokens.append(p.normal_form)
        grammems.append(p.tag.POS)


    sql_count = ['сколько', 'количество']
    sql_max = ['максимальный', 'максимум', 'наибольший']
    sql_min = ['минимальный','минимум','наименьший']
    sql_distinct = ['уникальный']
    sql_avg = ['средний']
    sql_date_part = {'день': 'day','месяц': 'month','год': 'year'}
    sql_order = {'desc': ['популярный', 'частый', 'новый'], 'asc': ["непопулярный", "редкий", "нечастый", 'старый']}
    sql_where = {'=': ['=', 'равно', 'равный'], '<': ['меньше', "ниже"], '>': ['выше', "больше"]}
    sql_limit = ['топ']
    sql_all = ['все', "всего"]


    names_dict = {}
    names_dict['default'] = None
    names_dict['count'] = None
    names_dict["minmax"] = None
    names_dict['date_part'] = None
    names_dict['order'] = None
    names_dict['where'] = None
    names_dict['distinct'] = None

    copy_lemma_tokens = lemma_tokens

    for name in names_list:
        name = name.lower()
        index = copy_lemma_tokens.index(name)
        if copy_lemma_tokens[index - 1] in sql_date_part and names_dict['date_part'] is None:
            names_dict['date_part'] = name
        elif copy_lemma_tokens[index - 1] in sql_order['desc'] and names_dict['order'] is None:
            names_dict['order'] = name
        elif copy_lemma_tokens[index - 1] in sql_order['asc'] and names_dict['order'] is None:
            names_dict['order'] = name
        elif index + 1 < len(copy_lemma_tokens) and copy_lemma_tokens[index + 1] in sql_where['='] and names_dict['where'] is None:
            names_dict['where'] = name
        elif index + 1 < len(copy_lemma_tokens) and copy_lemma_tokens[index + 1] in sql_where['<'] and names_dict['where'] is None:
            names_dict['where'] = name
        elif index + 1 < len(copy_lemma_tokens) and copy_lemma_tokens[index + 1] in sql_where['>'] and names_dict['where'] is None:
            names_dict['where'] = name
        elif copy_lemma_tokens[index - 1] in sql_count and names_dict['count'] is None:
            names_dict['count'] = name
        elif copy_lemma_tokens[index - 1] in sql_distinct and names_dict['distinct'] is None:
            names_dict['distinct'] = name
        elif copy_lemma_tokens[index - 1] in sql_max and names_dict['minmax'] is None:
            names_dict['minmax'] = name
        elif copy_lemma_tokens[index - 1] in sql_min and names_dict['minmax'] is None:
            names_dict['minmax'] = name
        elif copy_lemma_tokens[index - 1] in sql_avg and names_dict['minmax'] is None:
            names_dict['minmax'] = name
        else:
            names_dict['default'] = name
        del copy_lemma_tokens[index]

    symbol_all = ''
    date_part = ''
    count = ''
    group_by = ''
    count_part = ''
    distinct_value = ''
    minmax = ''
    limit = ''
    where = ''
    order = ''

    txt = "select {symbol_all}{date_part}{count_part}{count}{distinct_value}{minmax} from {table_name}{group_by}{order}{where}{limit}"

    for index, i in enumerate(lemma_tokens):
        if i in sql_date_part:
            date_part = f'date_part("{sql_date_part.get(i)}", {names_dict["date_part"]}) as y'
            count_part = ', count({})'
            group_by = f' group by y'
            count = ''
        elif i in sql_count:
            count = 'count({})'
        elif i in sql_max:
            if names_dict["minmax"] is not None:
                count = f'max({names_dict["minmax"]})'
            else:
                count = f'max({names_dict["default"]})'

        if i in sql_min:
            if names_dict["minmax"] is not None:
                count = f'min({names_dict["minmax"]})'
            else:
                count = f'min({names_dict["default"]})'

        if i in sql_avg:
            if names_dict["minmax"] is not None:
                count = f'avg({names_dict["minmax"]})'
            else:
                count = f'avg({names_dict["default"]})'

        if i in sql_limit:
            limit = f' limit {lemma_tokens[index+1]}'
        if i in sql_order['desc']:
            order = f' order by {names_dict["order"]} desc'
        elif i in sql_order['asc']:
            order = f' order by {names_dict["order"]} asc'
        if i in sql_where['=']:
            where = f' where {names_dict["where"]} = {lemma_tokens[index + 1]}'
        elif i in sql_where['>']:
            where = f' where {names_dict["where"]} > {lemma_tokens[index + 1]}'
        elif i in sql_where['<']:
            where = f' where {names_dict["where"]} < {lemma_tokens[index + 1]}'
        if i in sql_distinct:
            distinct = f'distinct {names_dict["distinct"]}'
            if '{}' in count:
                count = count.format(distinct)
            else:
                distinct_value = distinct
    if "{}" in count:
        if names_dict['count'] is not None:
            count = count.format(names_dict['count'])
        elif names_dict['default'] is not None:
            count = count.format(names_dict['default'])
        else:
            count = count.format('*')
    if count_part != '':
        if names_dict['count'] is not None:
            count_part = count_part.format(names_dict['count'])
        else:
            count_part = count_part.format('*')
    if date_part == '' and count == '' and minmax == '' and distinct_value == '':
        symbol_all = '*'

    return txt.format(symbol_all=symbol_all, date_part=date_part, count_part=count_part, count=count, distinct_value=distinct_value, minmax=minmax, table_name=table_name, group_by=group_by, order=order, where=where, limit=limit)
