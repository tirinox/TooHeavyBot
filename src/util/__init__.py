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
