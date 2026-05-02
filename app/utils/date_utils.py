from datetime import date, datetime, timedelta


UZ_DATE_FORMAT = "%d.%m.%Y"


def today() -> date:
    return datetime.now().date()


def yesterday() -> date:
    return today() - timedelta(days=1)


def parse_uz_date(value: str) -> date | None:
    try:
        return datetime.strptime(value.strip(), UZ_DATE_FORMAT).date()
    except ValueError:
        return None


def format_dt(value: datetime | None) -> str:
    if value is None:
        return "-"
    return value.strftime("%d.%m.%Y %H:%M")
