# nominaldelta - nominal difference of date/datetime

Python's [`datetime` module][1] is great: It has `ordinal` and `timestamp` as
absolute values, and `date` and `datetime` as nominal ones for the Gregorian
calendar. The only issue is `timedelta`: It is really an absolute delta, so
basically the same as `date1.toordinal() - date2.toordinal()` or
`dt1.timestamp() - dt2.timestamp()`.

The third party library [python-dateutil][2] adds `relativedelta`, which is a
nominal delta. However, it acts as if every day had 24 hours, which is not
quite true.

So this is an attempt to add a proper nominal delta.

## Example

```python
>>> from datetime import date
>>> from datetime import datetime
>>> from zoneinfo import ZoneInfo
>>> from nominaldelta import NominalDelta

# adding months does what you would expect
>>> datetime(1970, 1, 15, 13) + NominalDelta(months=1)
datetime(1970, 2, 15, 13)

# for shorter months, result are clipped to the last day of the month
>>> datetime(1970, 1, 30, 13) + NominalDelta(months=1)
datetime(1970, 2, 28, 13)

# daylight saving time is handled correctly
>>> tz = ZoneInfo('Europe/Berlin')
>>> datetime(2019, 3, 31, 3, 1, tzinfo=tz) - NominalDelta(minutes=2)
datetime(2019, 3, 31, 1, 59, tzinfo=tz)

# you can compute top-heavy differences
>>> delta = NominalDelta.diff(date(1970, 1, 1), date.today())
>>> f'{delta.months // 12} years'
'54 years'
```

## Status

This is just an experiment, so I did not publish it to pypi. Feel free to open
an issue if you think this should be published.

## Usage

### `class NominalDelta(years, months, weeks, days, hours, minutes, seconds)`

All values are optional and default to 0.

`NominalDelta` only stores months, days, and seconds. All other values are
converted to one of them:

-   `years` are converted to 12 months
-   `weeks` are converted to 7 days
-   `hours` are converted to 3600 seconds
-   `minutes` are converted to 60 seconds
-   `seconds` can be a float to represent milli- and micoseconds

Notably, `NominalDelta` avoids to perpetuate some common misconceptions:

-   `years` are not converted to 365 days because leap years have 366 days
-   `days` are not converted to 24 hours because of daylight saving time. Also,
    days with leap seconds have an extra second.

The three values are independent from each other. Seconds are never converted
to days, and days are never converted to months.

### `a + NominalDelta()`

When a `NominalDelta` is added to a `date` or `datetime`, the months are added
first. If the original day does not exist in that month (e.g. there is no
1970-02-30), the last day of that month is used instead. Days are added after
that and seconds are added last.

When adding to a `date`, seconds are ignored.

### `NominalDelta.diff(a, b)`

Calculate the delta between two `date` or `datetime` objects. This will first
check how many months can be added without overshooting. Then it will check how
many days can be added on top of the month. Last, the remaining difference in
seconds is calculated. This approach is called "top heavy" because it
prioritizes larger units over smaller ones.

If you prefer to get a difference in days or seconds, you can derive them from
the absolute differences:

```python
delta = NominalDelta(days=dt1.toordinal() - dt2.toordinal())
delta = NominalDelta(seconds=dt1.timestamp() - dt2.timestamp())
```

[1]: https://docs.python.org/3/library/datetime.html
[2]: https://github.com/dateutil/dateutil
