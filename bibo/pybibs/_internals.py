def split_entries(string):
    depth = 0
    start = 0
    for i, char in enumerate(string):
        if depth == 0 and char == '@':
            start = i
        if char == '{':
            depth += 1
        if char == '}':
            depth -= 1
            if depth == 0:
                yield string[start:i + 1]


def parse_raw_key_values(key_values):
    for line in key_values.splitlines():
        if line:
            key, value = line.split('=', 1)
            key = key.strip().lower()
            value = parse_value(value)
            yield key, value


def parse_value(value):
    delimiters = [
        '{}',
        '""',
    ]
    value = value.strip()
    if value[-1] == ',':
        value = value[:-1]
    for delimiter in delimiters:
        if value[0] == delimiter[0] and value[-1] == delimiter[-1]:
            value = value[1:-1]
            break
    return value


def write_entry(entry):
    parts = []
    parts += ['@', entry['type'], '{', entry['key']]
    for k, v in entry['fields'].items():
        parts += [',\n', '  ', k, ' = {', v, '}']
    parts.append('\n}')
    return ''.join(parts)
