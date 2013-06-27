"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import os, sys

sys.path.append('/home/dmitrii/code/others/haknews/latest/haknews/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'haknews.settings'

from django.test import TestCase



class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
