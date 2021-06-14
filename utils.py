from datetime import datetime

import pytz

def convert_to_timezone_with_offset(date_val: datetime, tz: str, converted: bool = False, isoformat: bool = True,
                                    no_offset: bool = True):
    """
    Converting tz-aware datetime object to local tz string with offset
    Args:
        date: tz-aware datetime object
        tz:   local timezone
    Returns: local naive datetime string with offset
    """
    try:
        if not isinstance(date_val, datetime):
            date_val = datetime.strptime(date_val, '%Y-%m-%dT%H:%M:%S.%f%z')
        if not isinstance(date_val, datetime) and type(date_val) is not str:
            date_val = datetime.combine(date_val, datetime.min.time())

        if converted:
            res = date_val.replace(tzinfo=pytz.timezone(tz))
        else:
            res = date_val.astimezone(pytz.timezone(tz))

        if isoformat:
            if no_offset:
                res = res.replace(tzinfo=None)
            return res.isoformat()
        return res
    except Exception as e:
        print('%s: (%s)' % (type(e), e))