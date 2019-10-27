from datetime import datetime, timedelta
import time
import pytz
from tzlocal import get_localzone


MINUTE = 60
HOUR = 60 * 60
DAY = 24 * 60 * 60
MONTH = 30 * 24 * 60 * 60


def parse_date(date_string: str):
    try:
        return int(datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S").timestamp())
    except ValueError:
        try:
            return int(datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f").timestamp())
        except ValueError:
            return None
    except TypeError:
        return None


def now_ts() -> float:
    return datetime.now().timestamp()   # don't use utcnow() since timestamp() does this conversion


def now_tsi() -> int:
    return int(now_ts())


def seconds_diff(t1: datetime, t2: datetime) -> float:
    return (t1 - t2).total_seconds()


def seconds_human(seconds, equal_str='same time') -> str:
    seconds = int(seconds)

    def append_if_not_zero(acc, val, time_type):
        return acc if val == 0 else "{} {} {}".format(acc, val, time_type)

    if seconds == 0:
        return equal_str
    else:
        minutes = seconds // 60
        hours = minutes // 60
        days = hours // 24

        s = ''
        s = append_if_not_zero(s, days, 'd')
        if days <= 31:
            s = append_if_not_zero(s, hours % 24, 'h')
        if not days:
            s = append_if_not_zero(s, minutes % 60, 'min')
        if not hours:
            s = append_if_not_zero(s, seconds % 60, 'sec')
        return s.strip()


def utc2local(utc):
    epoch = time.mktime(utc.timetuple())
    offset = datetime.fromtimestamp(epoch) - datetime.utcfromtimestamp(epoch)
    return utc + offset


def ts_format(timestamp, local=True, for_file=False):
    dt = datetime.fromtimestamp(int(timestamp))
    if local:
        dt = utc2local(dt)

    if for_file:
        return dt.strftime('%d-%m-%Y_%H-%M-%S')
    else:
        return dt.strftime('%d-%m-%Y %H:%M:%S')


def now_local_dt():
    return datetime.now(tz=get_localzone())


LONG_AGO = datetime(1980, 1, 1)


def parse_timespan_to_seconds(span: str):
    try:
        return int(span)
    except ValueError:
        result = 0
        str_for_number = ''
        for symbol in span:
            symbol = symbol.lower()
            if symbol in ['d', 'h', 'm', 's']:
                if str_for_number:
                    try:
                        number = int(str_for_number)
                    except ValueError:
                        return 'Error! Invalid number: {}'.format(str_for_number)
                    else:
                        multipliers = {
                            's': 1,
                            'm': 60,
                            'h': 3600,
                            'd': 3600 * 24
                        }
                        result += multipliers[symbol] * number
                    finally:
                        str_for_number = ''
                else:
                    raise ValueError('Error! Must be some digits before!')
            elif symbol in [chr(i + ord('0')) for i in range(10)]:
                str_for_number += symbol
            elif symbol in [' ', ',', ';', ':', '\t', '/', '.']:
                pass
            else:
                raise ValueError('Error! Unexpected symbol: {}'.format(symbol))

        if str_for_number:
            raise ValueError('Error! Unfinished component in the end: {}'.format(str_for_number))

        return result


def format_time_ago(d):
    if d is None or d == 0:
        return 'never'
    else:
        return f'{seconds_human(now_ts() - d)} ago'


def hour_and_min_from_str(s):
    s = s.strip()
    try:
        hh, mm = s.split(':')
    except TypeError:
        hh, mm = filter(lambda x: x.strip(), s.split(' '))

    hh, mm = int(hh), int(mm)

    assert 0 <= hh < 24
    assert 0 <= mm < 60

    return hh, mm


def estimate_time_shift_from_server_to_user(hh, mm):
    """
    If it's negative means usually server is west of user
    :param hh: hours
    :param mm: minutes
    :return: minutes of shift (rounded to 30)
    """
    now = datetime.now()
    my_hh, my_mm = now.hour, now.minute

    diff = ((my_hh - hh) * 60 + my_mm - mm) / 30.0
    return int(round(diff) * 30.0)


def time_of_user(time_shift_minutes):
    return datetime.now() + timedelta(time_shift_minutes)


DATETIME_FORMAT_TO_SETTING = '%A %H:%M'


def format_date_for_tz_selector(d: datetime):
    return d.strftime(DATETIME_FORMAT_TO_SETTING)


def get_possible_tz_names(common_only=True):
    timezones = pytz.common_timezones if common_only else pytz.all_timezones

    names = {}

    now = now_local_dt()
    for tz_name in timezones:
        tz = pytz.timezone(tz_name)
        unique_key = format_date_for_tz_selector(now.astimezone(tz))
        names[unique_key] = tz_name

    for k in sorted(names.keys()):
        yield names[k]


DIFFERENT_TIMEZONE_NAMES = list(get_possible_tz_names())


def convert_hh_mm(hh, mm, from_tz, to_tz):
    their_dt = datetime.now(tz=from_tz).replace(hour=hh, minute=mm)
    out_dt = their_dt.astimezone(to_tz)
    return out_dt.hour, out_dt.minute


def convert_time_hh_mm_to_local(hh, mm, tz_name):
    their_tz = pytz.timezone(tz_name)
    return convert_hh_mm(hh, mm, their_tz, get_localzone())


def convert_time_hh_mm_to_their(hh, mm, tz_name):
    their_tz = pytz.timezone(tz_name)
    return convert_hh_mm(hh, mm, get_localzone(), their_tz)


def delta_to_next_hh_mm(hh, mm):
    today_dt = now_local_dt()
    that_dt = today_dt.replace(hour=hh, minute=mm)
    if that_dt >= today_dt:
        return that_dt - today_dt
    else:
        return (that_dt + timedelta(days=1)) - today_dt


def hh_mm_from_timedelta(delta: timedelta) -> (int, int):
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _s = divmod(remainder, 60)
    return hours, minutes

