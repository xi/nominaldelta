import unittest
from datetime import date
from datetime import datetime

from zoneinfo import ZoneInfo

from nominaldelta import NominalDelta


class NotAValueClass:
    def _op(self, other):
        return self

    __add__ = __radd__ = _op
    __sub__ = __rsub__ = _op
    __mul__ = __rmul__ = _op

    __lt__ = __rlt__ = _op
    __gt__ = __rgt__ = _op
    __eq__ = __req__ = _op
    __le__ = __rle__ = _op
    __ge__ = __rge__ = _op


NotAValue = NotAValueClass()


class GeneralTests(unittest.TestCase):
    def test_construct(self):
        self.assertEqual(NominalDelta(years=22, months=9).months, 273)
        self.assertEqual(NominalDelta(weeks=2, days=2).days, 16)
        self.assertEqual(NominalDelta(weeks=2, days=-1).days, 13)
        self.assertEqual(NominalDelta(hours=1, minutes=2, seconds=3).seconds, 3723)
        self.assertNotEqual(NominalDelta(days=365), NominalDelta(years=1))
        self.assertNotEqual(NominalDelta(hours=24), NominalDelta(days=1))

    def test_fractional_year(self):
        with self.assertRaises(ValueError):
            NominalDelta(years=1.5)

    def test_fractional_month(self):
        with self.assertRaises(ValueError):
            NominalDelta(months=1.5)

    def test_hashable(self):
        try:
            {NominalDelta(minutes=1): 'test'}
        except Exception:  # pragma: no cover
            self.fail('NominalDelta() failed to hash!')

    def test_boolean(self):
        self.assertFalse(NominalDelta(days=0))
        self.assertTrue(NominalDelta(days=1))

    def test_repr(self):
        self.assertEqual(
            repr(NominalDelta(years=1, months=-1, days=15)),
            'NominalDelta(months=11, days=15, seconds=0)',
        )
        self.assertEqual(
            repr(NominalDelta(months=14, seconds=-25)),
            'NominalDelta(months=14, days=0, seconds=-25)',
        )

    def test_unsupported_eq(self):
        self.assertIs(NominalDelta(hours=3) == NotAValue, NotAValue)
        self.assertFalse(NominalDelta(years=1) == 19)

    def test_unsupported_add(self):
        self.assertIs(NominalDelta(days=1) + NotAValue, NotAValue)
        with self.assertRaises(TypeError):
            NominalDelta(days=3) + 9
        with self.assertRaises(TypeError):
            'asd' + NominalDelta(month=1)
        with self.assertRaises(TypeError):
            NominalDelta(month=1) + 'asd'
        with self.assertRaises(TypeError):
            NominalDelta(days=1) + datetime(2000, 1, 1)

    def test_unsupported_sub(self):
        self.assertIs(NominalDelta(days=1) + NotAValue, NotAValue)
        with self.assertRaises(TypeError):
            NominalDelta(hours=12) - 14
        with self.assertRaises(TypeError):
            NominalDelta(days=1) - datetime(2000, 1, 1)

    def test_multiplication_unsupported_type(self):
        self.assertIs(NominalDelta(days=1) * NotAValue, NotAValue)
        with self.assertRaises(TypeError):
            NominalDelta(hours=12) * 1.9


class DeltaArithmeticTests(unittest.TestCase):
    def test_add(self):
        self.assertEqual(
            NominalDelta(months=1) + NominalDelta(days=2),
            NominalDelta(months=1, days=2),
        )
        self.assertEqual(
            NominalDelta(months=1) + NominalDelta(months=2),
            NominalDelta(months=3),
        )
        self.assertEqual(
            NominalDelta(days=10)
            + NominalDelta(years=1, months=2, days=3, hours=4, minutes=5),
            NominalDelta(years=1, months=2, days=13, hours=4, minutes=5),
        )

    def test_sub(self):
        self.assertEqual(
            NominalDelta(months=1) - NominalDelta(days=2),
            NominalDelta(months=1, days=-2),
        )
        self.assertEqual(
            NominalDelta(months=1) - NominalDelta(months=2),
            NominalDelta(months=-1),
        )
        self.assertEqual(
            NominalDelta(days=10)
            - NominalDelta(years=1, months=2, days=3, hours=4, minutes=5),
            NominalDelta(years=-1, months=-2, days=7, hours=-4, minutes=-5),
        )

    def test_neg(self):
        self.assertEqual(
            -NominalDelta(months=1, days=-2),
            NominalDelta(months=-1, days=2),
        )

    def test_mul(self):
        self.assertEqual(
            NominalDelta(months=1, days=-2) * 2,
            NominalDelta(months=2, days=-4),
        )

    def test_rmul(self):
        self.assertEqual(
            2 * NominalDelta(months=1, days=-2),
            NominalDelta(months=2, days=-4),
        )

    def test_inheritance(self):
        class ChildClass(NominalDelta):
            pass

        delta = NominalDelta(months=1)
        child = ChildClass(months=1)

        self.assertEqual(type(child + delta), type(child))
        self.assertEqual(type(child - delta), type(child))
        self.assertEqual(type(-child), type(child))
        self.assertEqual(type(child * 5), type(child))


class AdditionTests(unittest.TestCase):
    def test_add_date(self):
        self.assertEqual(
            date(2003, 9, 17) + NominalDelta(months=1, weeks=1),
            date(2003, 10, 24),
        )
        self.assertEqual(date(2003, 12, 1) + NominalDelta(months=13), date(2005, 1, 1))
        self.assertEqual(date(2021, 1, 28) + NominalDelta(months=1), date(2021, 2, 28))
        self.assertEqual(date(2021, 2, 27) + NominalDelta(months=1), date(2021, 3, 27))
        self.assertEqual(date(2021, 4, 29) + NominalDelta(months=1), date(2021, 5, 29))
        self.assertEqual(date(2021, 5, 30) + NominalDelta(months=1), date(2021, 6, 30))
        self.assertEqual(date(2021, 11, 1) + NominalDelta(months=1), date(2021, 12, 1))

    def test_add_date_negative_months(self):
        self.assertEqual(date(2003, 1, 1) + NominalDelta(months=-2), date(2002, 11, 1))

    def test_add_date_month_clip(self):
        self.assertEqual(date(2003, 1, 27) + NominalDelta(months=1), date(2003, 2, 27))
        self.assertEqual(date(2003, 1, 31) + NominalDelta(months=1), date(2003, 2, 28))
        self.assertEqual(date(2003, 1, 31) + NominalDelta(months=2), date(2003, 3, 31))
        self.assertEqual(date(2021, 1, 31) + NominalDelta(months=1), date(2021, 2, 28))
        self.assertEqual(date(2021, 1, 30) + NominalDelta(months=1), date(2021, 2, 28))
        self.assertEqual(date(2021, 1, 29) + NominalDelta(months=1), date(2021, 2, 28))
        self.assertEqual(date(2021, 1, 28) + NominalDelta(months=1), date(2021, 2, 28))
        self.assertEqual(date(2021, 2, 28) + NominalDelta(months=1), date(2021, 3, 28))
        self.assertEqual(date(2021, 4, 30) + NominalDelta(months=1), date(2021, 5, 30))
        self.assertEqual(date(2021, 5, 31) + NominalDelta(months=1), date(2021, 6, 30))

    def test_date_add_leap_year_clip(self):
        self.assertEqual(date(1999, 2, 28) + NominalDelta(years=1), date(2000, 2, 28))
        self.assertEqual(date(1999, 3, 1) + NominalDelta(years=1), date(2000, 3, 1))

        self.assertEqual(date(2000, 2, 28) + NominalDelta(years=1), date(2001, 2, 28))
        self.assertEqual(date(2000, 2, 29) + NominalDelta(years=1), date(2001, 2, 28))

    def test_sub_date(self):
        self.assertEqual(date(1970, 1, 30) - NominalDelta(days=5), date(1970, 1, 25))
        self.assertEqual(date(2021, 2, 27) - NominalDelta(months=1), date(2021, 1, 27))
        self.assertEqual(date(2021, 2, 28) - NominalDelta(months=1), date(2021, 1, 28))
        self.assertEqual(date(2021, 3, 28) - NominalDelta(months=1), date(2021, 2, 28))
        self.assertEqual(date(2021, 5, 30) - NominalDelta(months=1), date(2021, 4, 30))
        self.assertEqual(date(2021, 6, 29) - NominalDelta(months=1), date(2021, 5, 29))

    def test_sub_date_clip(self):
        self.assertEqual(date(2021, 3, 29) - NominalDelta(months=1), date(2021, 2, 28))
        self.assertEqual(date(2021, 3, 30) - NominalDelta(months=1), date(2021, 2, 28))
        self.assertEqual(date(2021, 3, 31) - NominalDelta(months=1), date(2021, 2, 28))
        self.assertEqual(date(2021, 5, 31) - NominalDelta(months=1), date(2021, 4, 30))
        self.assertEqual(date(2021, 6, 30) - NominalDelta(months=1), date(2021, 5, 30))

    def test_add_datetime(self):
        self.assertEqual(
            datetime(2000, 1, 1) + NominalDelta(days=1), datetime(2000, 1, 2)
        )
        self.assertEqual(
            datetime(2003, 9, 17, 20, 54, 47) + NominalDelta(months=1),
            datetime(2003, 10, 17, 20, 54, 47),
        )
        self.assertEqual(
            datetime(2003, 9, 17, 20, 54, 47) + NominalDelta(months=1, weeks=1),
            datetime(2003, 10, 24, 20, 54, 47),
        )
        self.assertEqual(
            datetime(2003, 9, 17, 20, 54, 47) + NominalDelta(years=1, months=-1),
            datetime(2004, 8, 17, 20, 54, 47),
        )
        self.assertEqual(
            datetime(1970, 1, 30, 13) + NominalDelta(hours=2),
            datetime(1970, 1, 30, 15),
        )
        self.assertEqual(
            datetime(1970, 1, 30, 13) + NominalDelta(seconds=80),
            datetime(1970, 1, 30, 13, 1, 20),
        )

    def test_add_datetime_24h(self):
        self.assertEqual(
            datetime(1970, 1, 30, 13) + NominalDelta(hours=24),
            datetime(1970, 1, 31, 13),
        )

    def test_add_datetime_clip(self):
        self.assertEqual(
            datetime(1970, 1, 30, 13) + NominalDelta(months=1),
            datetime(1970, 2, 28, 13),
        )

    def test_add_datetime_fractional_seconds(self):
        self.assertEqual(
            datetime(2009, 9, 3, 0, 0) + NominalDelta(minutes=30, seconds=30.5),
            datetime(2009, 9, 3, 0, 30, 30, 500000),
        )

    def test_add_datetime_dst(self):
        tz = ZoneInfo('Europe/Berlin')
        self.assertEqual(
            datetime(2019, 3, 31, 1, 59, tzinfo=tz) + NominalDelta(minutes=2),
            datetime(2019, 3, 31, 3, 1, tzinfo=tz),
        )
        self.assertEqual(
            datetime(2019, 10, 27, 2, 59, tzinfo=tz) + NominalDelta(minutes=2),
            datetime(2019, 10, 27, 2, 1, fold=True, tzinfo=tz),
        )
        self.assertEqual(
            datetime(2019, 3, 30, 2, 30, tzinfo=tz) + NominalDelta(days=1),
            datetime(2019, 3, 31, 3, 30, tzinfo=tz),
        )

    def test_sub_datetime(self):
        self.assertEqual(
            datetime(1970, 1, 30, 13) - NominalDelta(days=1),
            datetime(1970, 1, 29, 13),
        )
        self.assertEqual(
            datetime(1970, 1, 30, 13) - NominalDelta(hours=2),
            datetime(1970, 1, 30, 11),
        )
        self.assertEqual(
            datetime(1970, 1, 30, 13) - NominalDelta(hours=24),
            datetime(1970, 1, 29, 13),
        )
        self.assertEqual(
            datetime(1970, 1, 30, 13) - NominalDelta(seconds=80),
            datetime(1970, 1, 30, 12, 58, 40),
        )
        self.assertEqual(
            datetime(2000, 1, 2) - NominalDelta(days=1), datetime(2000, 1, 1)
        )

    def test_sub_datetime_dst(self):
        tz = ZoneInfo('Europe/Berlin')
        self.assertEqual(
            datetime(2019, 3, 31, 3, 1, tzinfo=tz) - NominalDelta(minutes=2),
            datetime(2019, 3, 31, 1, 59, tzinfo=tz),
        )
        self.assertEqual(
            datetime(2019, 10, 27, 2, 1, fold=True, tzinfo=tz)
            - NominalDelta(minutes=2),
            datetime(2019, 10, 27, 2, 59, tzinfo=tz),
        )


class DiffTests(unittest.TestCase):
    def test_diff_invalid(self):
        with self.assertRaises(TypeError):
            NominalDelta.diff('2018-01-02', '2018-01-01')

        with self.assertRaises(TypeError):
            NominalDelta.diff('2018-01-02', datetime(2018, 1, 1))

        with self.assertRaises(TypeError):
            NominalDelta.diff(datetime(2018, 1, 2), '2018-01-01')

    def test_diff_date(self):
        self.assertEqual(
            NominalDelta.diff(date(1970, 1, 15), date(1970, 2, 15)),
            NominalDelta(months=1),
        )
        self.assertEqual(
            NominalDelta.diff(date(1970, 2, 15), date(1970, 1, 15)),
            NominalDelta(months=-1),
        )
        self.assertEqual(
            NominalDelta.diff(date(1000, 1, 1), date(2000, 1, 1)),
            NominalDelta(months=12_000),
        )
        self.assertEqual(
            NominalDelta.diff(date(1970, 1, 15), date(1970, 1, 16)),
            NominalDelta(days=1),
        )

    def test_diff_datetime(self):
        self.assertEqual(
            NominalDelta.diff(datetime(1970, 1, 30, 13), datetime(1970, 2, 28, 13)),
            NominalDelta(months=1),
        )
        self.assertEqual(
            NominalDelta.diff(datetime(1970, 1, 30, 13), datetime(1970, 1, 31, 13)),
            NominalDelta(days=1),
        )
        self.assertEqual(
            NominalDelta.diff(datetime(1970, 1, 30, 13), datetime(1970, 1, 30, 15)),
            NominalDelta(hours=2),
        )
        self.assertEqual(
            NominalDelta.diff(
                datetime(1970, 1, 30, 13),
                datetime(1970, 1, 30, 13, 1, 20),
            ),
            NominalDelta(seconds=80),
        )
        self.assertEqual(
            NominalDelta.diff(datetime(2001, 1, 1), datetime(2003, 9, 17, 20, 54, 47)),
            NominalDelta(
                years=2,
                months=8,
                days=16,
                hours=20,
                minutes=54,
                seconds=47,
            ),
        )

    def test_diff_datetime_full_month(self):
        self.assertEqual(
            NominalDelta.diff(
                datetime(2003, 1, 31, 23, 59, 59),
                datetime(2003, 3, 1, 0, 0, 0),
            ),
            NominalDelta(months=1, seconds=1),
        )
        self.assertEqual(
            NominalDelta.diff(
                datetime(2003, 3, 1, 0, 0, 0),
                datetime(2003, 1, 31, 23, 59, 59),
            ),
            NominalDelta(months=-1, seconds=-1),
        )

    def test_diff_datetime_full_month_leap_year(self):
        self.assertEqual(
            NominalDelta.diff(
                datetime(2004, 1, 31, 23, 59, 59),
                datetime(2004, 3, 1, 0, 0, 0),
            ),
            NominalDelta(months=1, seconds=1),
        )
        self.assertEqual(
            NominalDelta.diff(
                datetime(2004, 3, 1, 0, 0, 0),
                datetime(2004, 1, 31, 23, 59, 59),
            ),
            NominalDelta(months=-1, seconds=-1),
        )
