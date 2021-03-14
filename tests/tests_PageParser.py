import unittest

from parser import PageParser, PHONE_TEMPLATE
from tests.test_data import TEST_PAGE, FOUNDED_PHONES, PHONES_1, ACTUAL_PHONES_1


class TestPageParser(unittest.TestCase):

    def test_normalize_phones(self):
        out_phones = []
        parser = PageParser(page='', phone_template=PHONE_TEMPLATE,
                            out_phones=out_phones)
        result = parser.normalize_phones(PHONES_1)

        self.assertEqual(result, ACTUAL_PHONES_1)

    def test_find_phones(self):
        out_phones = []
        parser = PageParser(page=TEST_PAGE, phone_template=PHONE_TEMPLATE,
                            out_phones=out_phones)
        result = parser.find_phones()
        self.assertEqual(result, FOUNDED_PHONES)


