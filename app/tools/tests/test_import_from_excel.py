from iggnpk.tests.base import BaseTest
from tools import import_from_excel

class swapNumberInStreetTest(BaseTest):
    def test_pass_invalid_values(self):
        self.assertEqual('ул. Ленина', import_from_excel.swap_number_in_street('ул. Ленина'))
        self.assertEqual('ул. Ленина 1-я', import_from_excel.swap_number_in_street('ул. Ленина 1-я'))
        self.assertEqual('пер. Ленина 1-й', import_from_excel.swap_number_in_street('пер. Ленина 1-й'))
        self.assertEqual('пер. Ленина 1', import_from_excel.swap_number_in_street('пер. Ленина 1'))
        self.assertEqual('ул. 12 Декабря', import_from_excel.swap_number_in_street('ул. 12 Декабря'))
        self.assertEqual('пер. 3-й', import_from_excel.swap_number_in_street('пер. 3-й'))

    def test_swap_number(self):
        self.assertEqual('ул. Ленина 1-я', import_from_excel.swap_number_in_street('ул. 1-я Ленина'))
        self.assertEqual('пер. Ленина 1-й', import_from_excel.swap_number_in_street('пер. 1-й Ленина'))
