# -*- coding: utf-8 -*-
"""
    test_views

    Tests views and depends

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: GPLv3, see LICENSE for more details.
"""
from trytond.pool import Pool
from .country import Subdivision
from .party import Party, Address
from .product import Product, Template
from .sale import Sale
from .ebay import (
    SellerAccount, CheckTokenStatusView, CheckTokenStatus,
    ImportOrders, ImportOrdersView, ExportCatalogInventoryStart,
    ExportCatalogInventoryDone, ExportCatalogInventory,
    ExportCatalogStart, ExportCatalogDone, ExportCatalog
)


def register():
    "Register classes with pool"
    Pool.register(
        Subdivision,
        Party,
        Address,
        SellerAccount,
        Product,
        Template,
        Sale,
        CheckTokenStatusView,
        ImportOrdersView,
        ExportCatalogInventoryStart,
        ExportCatalogInventoryDone,
        ExportCatalogStart,
        ExportCatalogDone,
        module='ebay', type_='model'
    )
    Pool.register(
        CheckTokenStatus,
        ImportOrders,
        ExportCatalogInventory,
        ExportCatalog,
        module='ebay', type_='wizard'
    )
