from unittest.mock import patch, sentinel
from datetime import datetime, date
from capital_repair.tasks import send_acts
from dictionaries.models import Organization, House
from iggnpk.tests.base import BaseTest
from capital_repair.acts import Act
from freezegun import freeze_time
from mixer.backend.django import mixer
from capital_repair.models import Notify, CreditOrganization, ContributionsInformation, ContributionsInformationMistake


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
        self.assertFalse(Act.is_not_in_reporting_period(date(2020, 6, 21)))
        self.assertTrue(Act.is_not_in_reporting_period(date(2020, 5, 21)))


class ReportingQuarterDateTest(BaseTest):
    @freeze_time("2020-07-22")
    def test_values(self):
        self.assertEqual(Act.reporting_quarter_date(), date(2020,6,20))


class LastReportingDateTest(BaseTest):
    @freeze_time("2020-07-22")
    def test_values(self):
        self.assertEqual(Act.last_reporting_date(), date(2020,7,1))

class GenerateActContextsTest(BaseTest):
    def setUp(self):
        super(GenerateActContextsTest, self).setUp()
        self.mistake1 = mixer.blend(ContributionsInformationMistake, text='Error1', full_text='Full error1 text')
        self.mistake2 = mixer.blend(ContributionsInformationMistake, text='Error2', full_text='Full error2 text')
        self.house1 = mixer.blend(House)
        self.house2 = mixer.blend(House)
        self.org1 = mixer.blend(Organization)
        self.org2 = mixer.blend(Organization)
        self.org3 = mixer.blend(Organization)
        self.org4 = mixer.blend(Organization)
        self.notify1 = mixer.blend(Notify, organization=self.org1, house=self.house1)
        self.notify2 = mixer.blend(Notify, organization=self.org2, house=self.house1)
        self.notify3 = mixer.blend(Notify, organization=self.org3, house=self.house1)
        self.notify4 = mixer.blend(Notify, organization=self.org4, house=self.house1)
        self.notify22 = mixer.blend(Notify, organization=self.org2, house=self.house2)
        self.notify222 = mixer.blend(Notify, organization=self.org2, house=self.house2)
        self.contrib1 = mixer.blend(ContributionsInformation, notify = self.notify1, mistakes=[self.mistake1], status_id=3, date=date.today())
        self.contrib2 = mixer.blend(ContributionsInformation, notify=self.notify2, mistakes=[self.mistake2], status_id=3, date=date.today())
        self.contrib3 = mixer.blend(ContributionsInformation, notify=self.notify3, mistakes=[self.mistake1, self.mistake2], status_id=3, date=date.today())
        self.contrib4 = mixer.blend(ContributionsInformation, notify=self.notify4, mistakes=[], status_id=3,
                               date=date.today())
        self.contrib22 = mixer.blend(ContributionsInformation, notify=self.notify22, mistakes=[], status_id=3,
                               date=date.today())
        self.contrib222 = mixer.blend(ContributionsInformation, notify=self.notify222, mistakes=[self.mistake2],
                                    status_id=3, date=date.today())

    def test_contains_required_keys(self):
        contexts = Act.generate_act_contexts({})
        for key in ['date', 'organization', 'reporting_quarter_date', 'year', 'notifies', 'paragraph', 'mistakes_text']:
            self.assertIn(key ,contexts[0])

    def test_includes_only_contribs_with_mistakes(self):
        contexts = Act.generate_act_contexts({})
        self.assertEqual(len([x for x in contexts if x['organization'] == self.org2]), 1)
        self.assertEqual(len([x for x in contexts if x['organization'] == self.org4]), 0)

    def test_includes_only_notifies_with_mistakes(self):
        contexts = Act.generate_act_contexts({})
        org2 = [x for x in contexts if x['organization'] == self.org2][0]
        self.assertIn(self.notify2, org2['notifies'])
        self.assertIn(self.notify222, org2['notifies'])
        self.assertNotIn(self.notify22, org2['notifies'])

    def test_includes_only_right_mistakes(self):
        contexts = Act.generate_act_contexts({})
        org2 = [x for x in contexts if x['organization'] == self.org2][0]
        self.assertIn(self.mistake2.full_text, org2['mistakes_text'])
        self.assertNotIn(self.mistake1.full_text, org2['mistakes_text'])
        org3 = [x for x in contexts if x['organization'] == self.org3][0]
        self.assertIn(self.mistake2.full_text, org3['mistakes_text'])
        self.assertIn(self.mistake1.full_text, org3['mistakes_text'])


