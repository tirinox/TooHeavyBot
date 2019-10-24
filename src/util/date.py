from datetime import datetime, timedelta
import time
import pytz
import locale

locale.setlocale(locale.LC_TIME, 'ru_RU')


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


def get_zone_time_shift(tz: pytz.timezone) -> timedelta:
    null_delta = timedelta(0, 0)
    non_dst_offset = getattr(tz, '_transition_info', [[null_delta]])[-1]
    return non_dst_offset[0]


def possible_timezones(tz_offset_min, common_only=True):
    timezones = pytz.common_timezones if common_only else pytz.all_timezones

    # convert the float hours offset to a timedelta
    offset_days, offset_seconds = 0, int(tz_offset_min * 60)
    if offset_seconds < 0:
        offset_days = -1
        offset_seconds += 24 * 3600
    desired_delta = timedelta(offset_days, offset_seconds)

    # Loop through the timezones and find any with matching offsets
    results = []
    for tz_name in timezones:
        tz = pytz.timezone(tz_name)
        if desired_delta == get_zone_time_shift(tz):
            results.append(tz_name)

    return results


def get_possible_shifts(common_only=True):
    timezones = pytz.common_timezones if common_only else pytz.all_timezones

    shifts = set()

    for tz_name in timezones:
        tz = pytz.timezone(tz_name)
        shift = get_zone_time_shift(tz)
        minutes = int(shift.total_seconds() / 60)
        shifts.add(minutes)

    shifts_list = list(shifts)
    shifts_list.sort()
    return shifts_list


POSSIBLE_TIMEZONE_SHIFTS = get_possible_shifts()


def date_shift(d: datetime, tz_shift_minutes):
    timezones_names = possible_timezones(tz_shift_minutes)
    if not timezones_names:
        raise ValueError(f'invalid time shift {tz_shift_minutes}; must be one of {POSSIBLE_TIMEZONE_SHIFTS}')

    zone = pytz.timezone(timezones_names[0])
    their_date = d.astimezone(zone)
    return their_date


DATETIME_FORMAT_TO_SETTING = '%A %H:%M'


def format_date_for_tz_selector(d: datetime):
    return d.strftime(DATETIME_FORMAT_TO_SETTING)
