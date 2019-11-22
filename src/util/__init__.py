import secrets


def try_parse_int(o, default_value=None):
    try:
        return int(o)
    except (ValueError, TypeError):
        return default_value


def try_parse_float(o, default_value=None):
    try:
        return float(o)
    except (ValueError, TypeError):
        return default_value


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def gen_id(n=8):
    return secrets.token_hex(n)
