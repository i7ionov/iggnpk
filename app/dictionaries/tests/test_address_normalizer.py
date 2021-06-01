import dictionaries.address_normalizer
from iggnpk.tests.base import BaseTest


class normalizeStreetTest(BaseTest):
    def test_pass_invalid_values(self):
        self.assertEqual('ул. Ленина', dictionaries.address_normalizer.swap_number_in_street('ул. Ленина'))
        self.assertEqual('ул. Ленина 1-я', dictionaries.address_normalizer.swap_number_in_street('ул. Ленина 1-я'))
        self.assertEqual('пер. Ленина 1-й', dictionaries.address_normalizer.swap_number_in_street('пер. Ленина 1-й'))
        self.assertEqual('пер. Ленина 1', dictionaries.address_normalizer.swap_number_in_street('пер. Ленина 1'))
        self.assertEqual('ул. 12 Декабря', dictionaries.address_normalizer.swap_number_in_street('ул. 12 Декабря'))
        self.assertEqual('пер. 3-й', dictionaries.address_normalizer.swap_number_in_street('пер. 3-й'))

    def test_swap_number(self):
        self.assertEqual('ул. Ленина 1-я', dictionaries.address_normalizer.swap_number_in_street('ул. 1-я Ленина'))
        self.assertEqual('пер. Ленина 1-й', dictionaries.address_normalizer.swap_number_in_street('пер. 1-й Ленина'))

    def test_add_missings_spaces(self):
        self.assertEqual('ул. Ленина', dictionaries.address_normalizer.normalize_street('ул.Ленина'))
        self.assertEqual('пер. Ленина', dictionaries.address_normalizer.normalize_street('пер.Ленина'))


class normalizeNumberTest(BaseTest):
    def test_normalize_number(self):
        self.assertEqual('1', dictionaries.address_normalizer.normalize_number('1'))
        self.assertEqual('1/1', dictionaries.address_normalizer.normalize_number('1/1'))
        self.assertEqual('1/1', dictionaries.address_normalizer.normalize_number('1\\1'))
        self.assertEqual('1/1', dictionaries.address_normalizer.normalize_number('1к.1'))
        self.assertEqual('1/1', dictionaries.address_normalizer.normalize_number('1 к. 1'))
        self.assertEqual('1/1', dictionaries.address_normalizer.normalize_number('1 корп. 1'))
        self.assertEqual('1/1', dictionaries.address_normalizer.normalize_number('1 корп 1'))
        self.assertEqual('1а/а', dictionaries.address_normalizer.normalize_number('1а корпус А'))
