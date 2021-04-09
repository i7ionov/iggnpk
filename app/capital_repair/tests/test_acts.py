from unittest.mock import patch, sentinel
from datetime import datetime
from capital_repair.tasks import send_acts
from iggnpk.tests.base import BaseTest
from capital_repair.acts import Act
from freezegun import freeze_time


class ReportMonthTest(BaseTest):
    @freeze_time("2012-09-14")
    def test_report_month_returns_7(self):
        self.assertEqual(Act.report_month(), 7)

    @freeze_time("2012-05-14")
    def test_report_month_returns_4(self):
        self.assertEqual(Act.report_month(), 4)

    @freeze_time("2012-02-14")
    def test_report_month_returns_1(self):
        self.assertEqual(Act.report_month(), 1)

    @freeze_time("2012-11-14")
    def test_report_month_returns_1(self):
        self.assertEqual(Act.report_month(), 10)


class IsNotInReportingPeriodTest(BaseTest):
    @freeze_time("2020-07-14")
    def test_values(self):
        self.assertFalse(Act.is_not_in_reporting_period(datetime(2020, 6, 21)))
        self.assertTrue(Act.is_not_in_reporting_period(datetime(2020, 5, 21)))


class ReportingQuarterDateTest(BaseTest):
    @freeze_time("2020-07-22")
    def test_values(self):
        self.assertEqual(Act.reporting_quarter_date(), datetime(2020,6,20))


class LastReportingDateTest(BaseTest):
    @freeze_time("2020-07-22")
    def test_values(self):
        self.assertEqual(Act.last_reporting_date(), datetime(2020,7,1))