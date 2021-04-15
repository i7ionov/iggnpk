from datetime import datetime

MONTH_NAMES = [
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря"]


def russian_date(date):
    format = "%d !B %Y"
    result = date.strftime(format)
    result = result.replace('!B', MONTH_NAMES[date.month - 1]) + ' г.'
    return result


def normalize_date(date):
    formats = ["%Y-%m-%dT%H:%M:%S.000Z", "%Y/%m/%d"]
    for format in formats:
        try:
            return datetime.strptime(date, format).strftime("%Y-%m-%d")
        except:
            pass
    return date