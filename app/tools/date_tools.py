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
