import unittest
from datetime import date
from datetime import datetime
from zoneinfo import ZoneInfo

from nominaldelta import NominalDelta


class TestNominalDelta(unittest.TestCase):
    def test_weeks(self):
        self.assertEqual(NominalDelta(weeks=2, days=2).days, 16)
        self.assertEqual(NominalDelta(weeks=2, days=-1).days, 13)

    def test_add(self):
        self.assertEqual(
            NominalDelta(months=1) + NominalDelta(days=2),
            NominalDelta(months=1, days=2),
        )
        self.assertEqual(
            NominalDelta(months=1) + NominalDelta(months=2),
            NominalDelta(months=3),
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

    def test_radd_str_type_error(self):
        with self.assertRaises(TypeError):
            'asd' + NominalDelta(month=1)

        with self.assertRaises(TypeError):
            NominalDelta(month=1) + 'asd'

    def test_radd_date(self):
        self.assertEqual(
            date(1970, 1, 30) + NominalDelta(months=1),
            date(1970, 2, 28),
        )

    def test_radd_datetime(self):
        self.assertEqual(
            datetime(1970, 1, 30, 13) + NominalDelta(months=1),
            datetime(1970, 2, 28, 13),
        )
        self.assertEqual(
            datetime(1970, 1, 30, 13) + NominalDelta(hours=2),
            datetime(1970, 1, 30, 15),
        )
        self.assertEqual(
            datetime(1970, 1, 30, 13) + NominalDelta(hours=24),
            datetime(1970, 1, 31, 13),
        )
        self.assertEqual(
            datetime(1970, 1, 30, 13) + NominalDelta(seconds=80),
            datetime(1970, 1, 30, 13, 1, 20),
        )

    def test_radd_datetime_dst(self):
        tz = ZoneInfo('Europe/Berlin')
        self.assertEqual(
            datetime(2019, 3, 31, 1, 59, tzinfo=tz) + NominalDelta(minutes=2),
            datetime(2019, 3, 31, 3, 1, tzinfo=tz),
        )
        self.assertEqual(
            datetime(2019, 10, 27, 2, 59, tzinfo=tz) + NominalDelta(minutes=2),
            datetime(2019, 10, 27, 2, 1, fold=True, tzinfo=tz),
        )

    def test_rsub_date(self):
        self.assertEqual(
            date(1970, 1, 30) - NominalDelta(days=5),
            date(1970, 1, 25),
        )

    def test_rsub_datetime(self):
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

    def test_rsub_datetime_dst(self):
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
