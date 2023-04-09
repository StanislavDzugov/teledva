import logging
from datetime import date, datetime


logger = logging.getLogger('__name__')


def none_to_str(data):
    if data is None:
        return ''
    return data


def digit_or_none(obj):
    if isinstance(obj, str) and obj.isnumeric() or isinstance(obj, float):
        return obj
    return None


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


def convert_date(obj):
    if isinstance(obj, str):
        try:
            obj = datetime.strptime(obj, '%d.%m.%Y')
        except Exception as e:
            logging.error("Incorect data format: %s", obj)
            return None
    return obj