# -*- coding: utf-8 -*-
"""
    ebay

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: GPLv3, see LICENSE for more details.
"""
from trytond.model import ModelSQL, ModelView, fields


__all__ = ['SellerAccount']


class SellerAccount(ModelSQL, ModelView):
    "eBay Seller Account"
    __name__ = 'ebay.seller.account'

    name = fields.Char(
        'Name', required=True, help="A name which defines this account",
    )

    company = fields.Many2One(
        'company.company', 'Company', required=True,
        help="Company to which this account is linked",
    )

    app_id = fields.Char(
        'AppID', required=True,
        help="APP ID of the account - provided by eBay",
    )

    dev_id = fields.Char(
        'DevID', required=True, help="Dev ID of account - provided by eBay",
    )

    cert_id = fields.Char(
        'CertID', required=True, help="Cert ID of account - provided by eBay",
    )

    token = fields.Text(
        'Token', required=True,
        help="Token for this user account - to be generated from eBay "
        "developer home. If it expirees, then a new one should be generated",
    )
