# -*- coding: utf-8 -*-
"""
    test_views

    Tests views and depends

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: GPLv3, see LICENSE for more details.
"""
from trytond.pool import Pool
from .country import Subdivision
from .ebay import SellerAccount, CheckTokenStatusView, CheckTokenStatus


def register():
    "Register classes with pool"
    Pool.register(
        Subdivision,
        SellerAccount,
        CheckTokenStatusView,
        module='ebay', type_='model'
    )
    Pool.register(
        CheckTokenStatus,
        module='ebay', type_='wizard'
    )
