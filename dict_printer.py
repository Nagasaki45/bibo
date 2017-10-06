import textwrap


def format(dict_, max_width=80, ordered_keys=None):

    if ordered_keys is None:
        ordered_keys = []

    widest_key = max([len(str(key)) for key in dict_])
    values_width = max_width - widest_key - len(': ')
    dict_str = []

    for key in sorted(dict_):
        if key not in ordered_keys:
            ordered_keys.append(key)

    for key in ordered_keys:
        if key not in dict_:
            continue
        dict_str.append(
            _format_key_value_pair(
                str(key),
                dict_[key],
                widest_key,
                values_width,
            )
        )
    return '\n'.join(dict_str)


def _format_key_value_pair(key, value, widest_key, values_width):
    entry_str = []
    if isinstance(value, str) and value.startswith('http'):
        wrapped_value = [value]
    elif isinstance(value, str):
        wrapped_value = textwrap.wrap(value, width=values_width)
    else:
        wrapped_value = [value]
    first_value = wrapped_value.pop(0)
    padding = ' ' * (widest_key - len(key))
    entry_str.append(f'{key}: {padding}{first_value}')
    for w in wrapped_value:
        entry_str.append(' ' * (widest_key + len(': ')) + w)
    return '\n'.join(entry_str)
