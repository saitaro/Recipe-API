from django.test import TestCase

from .calc import add, subtract


class CalcTests(TestCase):
    def test_add(self):
        """ Testing that two numbers are added """
        self.assertEqual(add(8, 3), 11)

    def test_subtract(self):
        """ Testing that one number is subtracted from the other """
        self.assertEqual(subtract(11, 5), 6)
