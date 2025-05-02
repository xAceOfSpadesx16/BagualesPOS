from locale import setlocale, format_string, LC_ALL


def formatted_integer(integer):
    setlocale(LC_ALL, 'es_AR.UTF-8')
    return format_string("%d", integer, grouping=True)