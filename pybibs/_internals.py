import re


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


def is_before_key(char, previous):
    return re.match(r'\s', char)


def is_key(char, previous):
    return char.isalpha()


def is_between(char, previous):
    together = ''.join(previous + [char])
    if re.match(r'^\s*=?\s*$', together):
        return True


def is_value(char, previous):
    if previous and previous[0] == '{' and previous[-1] == '}':
        depth = 0
        for x in previous:
            if x == '{':
                depth += 1
            elif x == '}':
                depth -= 1
        if depth == 0:
            return False
    if len(previous) > 1 and previous[0] == previous[-1] == '"':
        return False
    if previous and previous[0] not in '{"' and char == ',':
        return False
    return True


def is_separator(char, previous):
    if char == ',':
        return True


def parse_raw_key_values(string):
    string = re.sub(r'\s+', ' ', string)
    checks =   [is_before_key, is_key, is_between, is_value, is_separator]
    contents = [[],            [],     [],         [],       []]
    current = 0
    char_index = 0
    while char_index < len(string):
        char = string[char_index]
        if checks[current](char, contents[current]):
            contents[current].append(char)
            char_index += 1
        else:
            current += 1
            if current == len(checks):
                key = parse_key(''.join(contents[1]))
                value = parse_value(''.join(contents[3]))
                yield key, value
                contents = [[], [], [], [], []]
                current = 0


def parse_key(key):
    return key.lower()


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
