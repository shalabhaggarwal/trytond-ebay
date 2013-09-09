# -*- coding: utf-8 -*-
"""
    test_party

    Tests party

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: GPLv3, see LICENSE for more details.
"""
import os
import sys
import unittest
DIR = os.path.abspath(os.path.normpath(
    os.path.join(
        __file__,
        '..', '..', '..', '..', '..', 'trytond'
    )
))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, USER, DB_NAME, CONTEXT
from test_base import TestBase, load_json
from trytond.transaction import Transaction
from trytond.exceptions import UserError


class TestParty(TestBase):
    """
    Tests party
    """

    def test0010_create_party(self):
        """
        Tests if users imported from ebay is created as party in tryton
        """
        with Transaction().start(DB_NAME, USER, CONTEXT):

            self.setup_defaults()

            ebay_data = load_json('users', 'testuser_shalabhaggarwal')

            parties = self.Party.search([])
            self.assertEqual(len(parties), 1)

            # Create party
            party = self.Party.create_using_ebay_data(ebay_data)
            self.assert_(party)

            self.assertTrue(
                self.Party.search([
                    ('name', '=', 'testuser_shalabhaggarwal')
                ])
            )
            parties = self.Party.search([])
            self.assertEqual(len(parties), 2)
            self.assertTrue(len(party.contact_mechanisms), 1)
            self.assertTrue(party.contact_mechanisms[0].email)

    def test0020_create_party_duplicate(self):
        """
        Tests if users imported from ebay is duplicated as party in tryton
        """
        with Transaction().start(DB_NAME, USER, CONTEXT):

            self.setup_defaults()

            ebay_data = load_json('users', 'testuser_shalabhaggarwal')

            # Create party
            party = self.Party.create_using_ebay_data(ebay_data)
            self.assert_(party)

            # Create again and it should fail
            self.assertRaises(
                UserError, self.Party.create_using_ebay_data,
                ebay_data,
            )

    def test0030_import_addresses_from_ebay(self):
        """
        Test address import as party addresses and make sure no duplication
        is there.
        """
        Address = POOL.get('party.address')

        with Transaction().start(DB_NAME, USER, CONTEXT):

            self.setup_defaults()

            self.Subdivision.create([{
                'name': 'New Delhi',
                'code': 'IN-DL',
                'type': 'state',
                'country': self.country_in.id,
            }])

            # Load json of address data
            ebay_data = load_json('users', 'testuser_shalabhaggarwal')
            address_data = ebay_data['User']['RegistrationAddress']

            self.party = self.Party.create_using_ebay_data(ebay_data)

            # Check party address before address import
            self.assertEqual(len(self.party.addresses), 1)

            # Check contact mechanism before address import
            self.assertEqual(len(self.party.contact_mechanisms), 1)

            # Import address for party1 from ebay
            address = Address.find_or_create_for_party_using_ebay_data(
                self.party, address_data
            )

            # Check address after import
            self.assertEqual(len(self.party.addresses), 2)
            self.assertEqual(address.party, self.party)
            self.assertEqual(
                address.name, address_data['Name']['value']
            )
            self.assertEqual(address.street, address_data['Street']['value'])
            self.assertEqual(address.zip, address_data['PostalCode']['value'])
            self.assertEqual(address.city, address_data['CityName']['value'])
            self.assertEqual(
                address.country.code, address_data['Country']['value']
            )
            self.assertEqual(
                address.subdivision.name.lower(),
                address_data['StateOrProvince']['value'].lower()
            )

            # Check contact mechnanism after import
            self.assertEqual(len(self.party.contact_mechanisms), 2)

            # Try to import address data again.
            address = Address.find_or_create_for_party_using_ebay_data(
                self.party, address_data
            )
            self.assertEqual(len(self.party.addresses), 2)
            self.assertEqual(len(self.party.contact_mechanisms), 2)

    def test0040_match_address(self):
        """
        Tests if address matching works as expected
        """
        Address = POOL.get('party.address')

        with Transaction().start(DB_NAME, USER, CONTEXT):

            self.setup_defaults()

            self.Subdivision.create([{
                'name': 'New Delhi',
                'code': 'IN-DL',
                'type': 'state',
                'country': self.country_in.id,
            }])
            self.Subdivision.create([{
                'name': 'Goa',
                'code': 'IN-GA',
                'type': 'state',
                'country': self.country_in.id,
            }])
            self.Subdivision.create([{
                'name': 'New York',
                'code': 'US-NY',
                'type': 'state',
                'country': self.country_us.id,
            }])

            # Load json of address data
            ebay_data = load_json('users', 'testuser_shalabhaggarwal')

            self.party = self.Party.create_using_ebay_data(ebay_data)

            # Import address for self.party from ebay
            address = Address.find_or_create_for_party_using_ebay_data(
                self.party, load_json('addresses', '1a')
            )

            # Same address imported again
            self.assertTrue(
                address.match_with_ebay_data(load_json('addresses', '1b'))
            )

            # Similar with different country and state
            self.assertFalse(
                address.match_with_ebay_data(load_json('addresses', '1c'))
            )

            # Similar with different state
            self.assertFalse(
                address.match_with_ebay_data(load_json('addresses', '1d'))
            )

            # Similar with different city
            self.assertFalse(
                address.match_with_ebay_data(load_json('addresses', '1e'))
            )

            # Similar with different street
            self.assertFalse(
                address.match_with_ebay_data(load_json('addresses', '1f'))
            )


def suite():
    """
    Test Suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestParty)
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
