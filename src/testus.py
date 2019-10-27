import pytz
from util.date import *

my_tz = pytz.UTC

u_tz = 'Europe/Moscow'

h, m = 10, 0

print(convert_hh_mm(h, m, pytz.timezone(u_tz), my_tz))
