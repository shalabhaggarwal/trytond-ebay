# -*- coding: utf-8 -*-
"""
    test_base

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: GPLv3, see LICENSE for more details.
"""
import unittest

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, USER
from trytond.transaction import Transaction


class TestBase(unittest.TestCase):
    """
    Setup basic defaults
    """

    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test function execution.
        """
        trytond.tests.test_tryton.install_module('ebay')

    def setup_defaults(self):
        """
        Setup default data
        """
        self.Currency = POOL.get('currency.currency')
        self.Company = POOL.get('company.company')
        self.Party = POOL.get('party.party')
        self.Country = POOL.get('country.country')
        self.Subdivision = POOL.get('country.subdivision')
        self.User = POOL.get('res.user')

        with Transaction().set_context(company=None):
            self.party, = self.Party.create([{
                'name': 'ABC',
            }])
            self.usd, = self.Currency.create([{
                'name': 'US Dollar',
                'code': 'USD',
                'symbol': '$',
            }])
            self.company, = self.Company.create([{
                'party': self.party.id,
                'currency': self.usd.id,
            }])

        self.User.write([self.User(USER)], {
            'main_company': self.company.id,
            'company': self.company.id,
        })

        self.country_us, = self.Country.create([{
            'name': 'United States',
            'code': 'US',
        }])

        self.country_in, = self.Country.create([{
            'name': 'India',
            'code': 'IN',
        }])

        self.subdivision_fl, = self.Subdivision.create([{
            'name': 'Florida',
            'code': 'US-FL',
            'country': self.country_us.id,
            'type': 'state',
        }])

        self.subdivision_up, = self.Subdivision.create([{
            'name': 'Uttar Pradesh',
            'code': 'IN-UP',
            'country': self.country_in.id,
            'type': 'state',
        }])
