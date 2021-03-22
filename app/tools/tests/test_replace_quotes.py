import tools.replace_quotes
from iggnpk.tests.base import BaseTest


class normalizeStreetTest(BaseTest):
    def test_pass_invalid_values(self):
        pass

    def test_replaces_quotes(self):
        self.assertEqual('ООО «Ромашка»', tools.replace_quotes.replace_quotes('ООО "Ромашка"'))
        self.assertEqual('ООО«Ромашка»', tools.replace_quotes.replace_quotes('ООО"Ромашка"'))
        self.assertEqual('ООО «УК «Ромашка»»', tools.replace_quotes.replace_quotes('ООО "УК "Ромашка""'))
        self.assertEqual('ООО«УК«Ромашка»»', tools.replace_quotes.replace_quotes('ООО"УК"Ромашка""'))
        self.assertEqual('ООО «Ромашка»', tools.replace_quotes.replace_quotes('ООО «Ромашка»'))
        self.assertEqual('ООО«УК«Ромашка»»', tools.replace_quotes.replace_quotes('ООО«УК«Ромашка»»'))
