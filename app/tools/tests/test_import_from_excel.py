import tools.get_value
from iggnpk.tests.base import BaseTest
from tools import import_from_excel


class CutValueTest(BaseTest):
    def test_cut_value(self):
        self.assertEqual(tools.get_value.cut_value('foo (bar)', 'myfield'), ('foo', 'myfield: (bar). '))
