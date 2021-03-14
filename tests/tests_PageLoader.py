import unittest
from unittest.mock import Mock

import requests

from parser import PageLoader


class TestPageLoader(unittest.TestCase):

    def test_get_pages_1(self):
        loaded_pages = []
        self.parser = PageLoader('https://mlw2.ru/', loaded_pages)
        with self.assertRaises(requests.exceptions.ConnectionError):
            self.parser.get_page()

    def test_get_pages_2(self):
        loaded_pages = []
        self.parser = PageLoader('asdsdasdasd', loaded_pages)
        with self.assertRaises(requests.exceptions.MissingSchema):
            self.parser.get_page()

    def test_get_pages_3(self):
        loaded_pages = []
        self.parser = PageLoader('htt://mlw2.ru/', loaded_pages)
        with self.assertRaises(requests.exceptions.InvalidSchema):
            self.parser.get_page()

    def test_get_pages_ok(self):
        loaded_pages = []
        self.parser = PageLoader('https://masterdel.ru/', loaded_pages)
        self.parser.get_page()
