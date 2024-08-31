from datetime import date
from datetime import datetime
from typing import TypeVar

Self = TypeVar('Self', bound='NominalDelta')


def date_to_timestamp(d):
    return datetime(d.year, d.month, d.day).timestamp()


def date_add(dt, delta):
    total_months = dt.year * 12 + dt.month + delta.months
    year, month = divmod(total_months, 12)
    if month == 0:
        year -= 1
        month = 12

    # clip day to month
    day = dt.day
    while day > 0:
        try:
            tmp = dt.__class__(year, month, day)
            break
        except ValueError:
            day -= 1

    return dt.__class__.fromordinal(tmp.toordinal() + delta.days)


def dt_add(dt, delta):
    d = date_add(dt.date(), delta)
    offset = dt.timestamp() - date_to_timestamp(dt.date())
    return dt.__class__.fromtimestamp(
        date_to_timestamp(d) + offset + delta.seconds, tz=dt.tzinfo
    )


def binary_search(a, b, delta):
    lower = 0
    upper = 1
    while a + delta * upper <= b:
        lower = upper
        upper <<= 1
    while lower + 1 < upper:
        tmp = (lower + upper) // 2
        if a + delta * tmp <= b:
            lower = tmp
        else:
            upper = tmp
    return lower * delta


def date_diff(a, b, *, allow_months=True):
    if a > b:
        return -date_diff(b, a)
    delta = NominalDelta()
    if allow_months:
        delta += binary_search(a, b, NominalDelta(months=1))
    days = b.toordinal() - (a + delta).toordinal()
    return delta + NominalDelta(days=days)


def dt_diff(a, b, *, allow_months=True):
    if a > b:
        return -dt_diff(b, a)
    delta = date_diff(a, b, allow_months=allow_months)
    seconds = b.timestamp() - (a + delta).timestamp()
    if seconds < 0:
        delta -= NominalDelta(days=1)
        seconds = b.timestamp() - (a + delta).timestamp()
    return delta + NominalDelta(seconds=seconds)


class NominalDelta:
    def __init__(
        self: Self,
        *,
        years: int = 0,
        months: int = 0,
        weeks: int = 0,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: float = 0,
    ):
        for key in ['years', 'months', 'weeks', 'days', 'hours', 'minutes']:
            if not isinstance(locals()[key], int):
                raise ValueError(f'{key} must be an int')

        self.months = years * 12 + months
        self.days = weeks * 7 + days
        self.seconds = hours * 3600 + minutes * 60 + seconds

    def __repr__(self):
        return (
            f'NominalDelta(months={self.months}, days={self.days}, '
            f'seconds={self.seconds})'
        )

    def __hash__(self):
        return hash((self.months, self.days, self.seconds))

    def __bool__(self) -> bool:
        return bool(self.months or self.days or self.seconds)

    def __eq__(self, other) -> bool:
        if isinstance(other, NominalDelta):
            return (
                self.months == other.months
                and self.days == other.days
                and self.seconds == other.seconds
            )
        return NotImplemented

    def __add__(self: Self, other) -> Self:
        if isinstance(other, NominalDelta):
            return self.__class__(
                months=self.months + other.months,
                days=self.days + other.days,
                seconds=self.seconds + other.seconds,
            )
        return NotImplemented

    def __sub__(self: Self, other) -> Self:
        if isinstance(other, NominalDelta):
            return self.__class__(
                months=self.months - other.months,
                days=self.days - other.days,
                seconds=self.seconds - other.seconds,
            )
        return NotImplemented

    def __neg__(self: Self) -> Self:
        return self.__class__() - self

    def __mul__(self: Self, factor: int) -> Self:
        if isinstance(factor, int):
            return self.__class__(
                months=self.months * factor,
                days=self.days * factor,
                seconds=self.seconds * factor,
            )
        return NotImplemented

    def __rmul__(self: Self, factor: int) -> Self:
        return self * factor

    def __radd__(self: Self, other: date) -> date:
        if isinstance(other, datetime):
            return dt_add(other, self)
        elif isinstance(other, date):
            return date_add(other, self)
        return NotImplemented

    def __rsub__(self: Self, other: date) -> date:
        return (-self).__radd__(other)

    @classmethod
    def diff(cls: type[Self], a: date, b: date, *, allow_months: bool = True) -> Self:
        if isinstance(a, datetime) and isinstance(b, datetime):
            return dt_diff(a, b, allow_months=allow_months)
        elif isinstance(a, date) and isinstance(b, date):
            return date_diff(a, b, allow_months=allow_months)
        raise TypeError('Unsupported types')
