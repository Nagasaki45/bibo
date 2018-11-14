class QueryException(Exception):
    pass


def search(data, search_term):
    for key, fields in data.items():
        for field in fields.values():
            if search_term.lower() in field.lower():
                yield fields
                break


def get(data, search_term):
    search_results = search(data, search_term)

    try:
        entry = next(search_results)
    except StopIteration:
        raise QueryException('No results found')

    try:
        next(search_results)
    except StopIteration:
        pass
    else:
        raise QueryException('Multiple results found')

    return entry
