# -*- coding: UTF-8 -*-
'''
    product

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: GPLv3, see LICENSE for more details.
'''
from decimal import Decimal

from trytond.model import fields
from trytond.transaction import Transaction
from trytond.pool import PoolMeta, Pool
from trytond.pyson import Eval


__all__ = [
    'Product', 'Template'
]
__metaclass__ = PoolMeta


class Template:
    "Product Template"
    __name__ = 'product.template'

    ebay_exportable = fields.Boolean('eBay Exportable')

    ebay_max_dispatch_time = fields.Integer(
        'Maximum Dispatch Time', states={
            'invisible': ~Eval('ebay_exportable', False),
            'required': Eval('ebay_exportable', False),
        }
    )
    ebay_listing_duration = fields.Selection([
        ('Days_1', 'Days_1'),
        ('Days_3', 'Days_3'),
        ('Days_5', 'Days_5'),
        ('Days_7', 'Days_7'),
        ('Days_10', 'Days_10'),
        ('Days_14', 'Days_14'),
        ('Days_21', 'Days_21'),
        ('Days_30', 'Days_30'),
        ('Days_60', 'Days_60'),
        ('Days_90', 'Days_90'),
        ('Days_120', 'Days_120'),
        ('GTC', 'Good Till Cancelled'),
    ], 'Listing Duration', states={
        'invisible': ~Eval('ebay_exportable', False),
        'required': Eval('ebay_exportable', False),
    })
    ebay_return_policy_option = fields.Selection([
        ('ReturnsAccepted', 'ReturnsAccepted'),
        ('ReturnsNotAccepted', 'ReturnsNotAccepted')
    ], 'Return Policy Accepted Option', states={
        'invisible': ~Eval('ebay_exportable', False),
        'required': Eval('ebay_exportable', False),
    })

    ebay_refund_option = fields.Selection([
        ('Exchange', 'Exchange'),
        ('MerchandiseCredit', 'MerchandiseCredit'),
        ('MoneyBack', 'MoneyBack'),
        ('MoneyBackOrExchange', 'MoneyBackOrExchange'),
        ('MoneyBackOrReplacement', 'MoneyBackOrReplacement'),
    ], 'Refund Option', states={
        'invisible': ~Eval('ebay_exportable', False),
        'required': Eval('ebay_exportable', False),
    })

    ebay_returns_within_option = fields.Selection([
        ('Days_3', 'Days_3'),
        ('Days_7', 'Days_7'),
        ('Days_10', 'Days_10'),
        ('Days_14', 'Days_14'),
        ('Days_30', 'Days_30'),
        ('Days_60', 'Days_60'),
        ('Months_1', 'Months_1'),
    ], 'Returns within Option', states={
        'invisible': ~Eval('ebay_exportable', False),
        'required': Eval('ebay_exportable', False),
    })

    ebay_refund_description = fields.Text('Refund Description', states={
        'invisible': ~Eval('ebay_exportable', False),
        'required': Eval('ebay_exportable', False),
    })

    ebay_refund_shipping_cost_paid_by_option = fields.Selection([
        ('Buyer', 'Buyer'),
        ('Seller', 'Seller')
    ], 'Refund Shipping Cost Paid By Option', states={
        'invisible': ~Eval('ebay_exportable', False),
        'required': Eval('ebay_exportable', False),
    })

    ebay_shipping_type = fields.Selection([
        ('Flat', 'Flat'),
        ('', ''),
    ], 'Shipping Type', states={
        'invisible': ~Eval('ebay_exportable', False),
        'required': Eval('ebay_exportable', False),
    })
    ebay_shipping_service = fields.Char(
        'eBay Shipping Service', states={
            'invisible': ~Eval('ebay_exportable', False),
            'required': Eval('ebay_shipping_type') == 'Flat',
        }
    )
    ebay_shipping_cost = fields.Numeric('Shipping Service Cost', states={
        'invisible': ~Eval('ebay_exportable', False),
        'required': Eval('ebay_shipping_type') == 'Flat',
    })
    ebay_category_id = fields.Char('eBay Category ID', states={
        'invisible': ~Eval('ebay_exportable', False),
        'required': Eval('ebay_exportable', False),
    })


class Product:
    "Product"

    __name__ = "product.product"

    ebay_item_id = fields.Char(
        'eBay Item ID',
        help="This is global and unique ID given to an item across whole ebay."
        " Warning: Editing this might result in duplicate products on next"
        " import"
    )

    @classmethod
    def __setup__(cls):
        """
        Setup the class before adding to pool
        """
        super(Product, cls).__setup__()
        cls._error_messages.update({
            "invalid_product": 'Product with eBay Item ID "%s" already exists',
            "missing_product_code": 'Product "%s" has a missing code.',
            "ebay_error": 'Messages: "%s"',
        })

    @classmethod
    def validate(cls, products):
        super(Product, cls).validate(products)
        for product in products:
            product.check_ebay_item_id()

    def check_ebay_item_id(self):
        "Check the eBay Item ID for duplicates"
        if self.ebay_item_id and len(
            self.search([('ebay_item_id', '=', self.ebay_item_id)])
        ) > 1:
            self.raise_user_error('invalid_product', (self.ebay_item_id,))

    @classmethod
    def find_or_create_using_ebay_id(cls, ebay_id):
        """
        Find or create a product using ebay ID. This method looks
        for an existing product using the ebay ID provided. If found, it
        returns the product found, else creates a new one and returns that

        :param ebay_id: Product ID from eBay
        :returns: Active record of Product Created
        """
        SellerAccount = Pool().get('ebay.seller.account')

        products = cls.search([('ebay_item_id', '=', ebay_id)])

        if products:
            return products[0]

        # if product is not found get the info from ebay and
        # delegate to create_using_ebay_data
        seller_account = SellerAccount(
            Transaction().context.get('ebay_seller_account')
        )
        api = seller_account.get_trading_api()

        product_data = api.execute(
            'GetItem', {'ItemID': ebay_id, 'DetailLevel': 'ReturnAll'}
        ).response_dict()

        return cls.create_using_ebay_data(product_data)

    @classmethod
    def extract_product_values_from_ebay_data(cls, product_data):
        """
        Extract product values from the ebay data, used for
        creation of product. This method can be overwritten by
        custom modules to store extra info to a product

        :param: product_data
        :returns: Dictionary of values
        """
        SellerAccount = Pool().get('ebay.seller.account')

        account = SellerAccount(
            Transaction().context.get('ebay_seller_account')
        )
        return_policy = product_data['Item']['ReturnPolicy']
        template_data = {
            'name': product_data['Item']['Title']['value'],
            'list_price': Decimal(
                product_data['Item']['BuyItNowPrice']['value'] or
                product_data['Item']['StartPrice']['value']
            ),
            'cost_price': Decimal(product_data['Item']['StartPrice']['value']),
            'default_uom': account.default_uom.id,
            'salable': True,
            'sale_uom': account.default_uom.id,
            'account_expense': account.default_account_expense.id,
            'account_revenue': account.default_account_revenue.id,
            'ebay_exportable': True,
            'ebay_max_dispatch_time': product_data['Item'][
                'DispatchTimeMax'
            ]['value'],
            'ebay_listing_duration': product_data['Item'][
                'ListingDuration'
            ]['value'],
            'ebay_return_policy_option': return_policy[
                'ReturnsAcceptedOption'
            ]['value'],
            'ebay_refund_option': return_policy['RefundOption']['value'],
            'ebay_returns_within_option': return_policy[
                'ReturnsWithinOption'
            ]['value'],
            'ebay_refund_description': return_policy.get('Description') and
                return_policy['Description']['value'] or 'No Description',
            'ebay_refund_shipping_cost_paid_by_option': return_policy[
                'ShippingCostPaidByOption'
            ]['value'],
            'ebay_category_id': product_data['Item'][
                'PrimaryCategory'
            ]['CategoryID']['value']
        }
        # Only flat shipment is supported now so handle only flat
        if product_data['Item'][
            'ShippingDetails'
        ]['ShippingType']['value'] == 'Flat':
            template_data.update({
                'ebay_shipping_type': product_data['Item'][
                    'ShippingDetails'
                ]['ShippingType']['value'],
                'ebay_shipping_service': product_data['Item'][
                    'ShippingDetails'
                ]['ShippingServiceOptions']['ShippingService']['value'],
                'ebay_shipping_cost': Decimal(product_data['Item'][
                    'ShippingDetails'
                ]['ShippingServiceOptions']['ShippingServiceCost']['value']),
            })
        return template_data

    @classmethod
    def create_using_ebay_data(cls, product_data):
        """
        Create a new product with the `product_data` from ebay.

        :param product_data: Product Data from eBay
        :returns: Browse record of product created
        """
        Template = Pool().get('product.template')

        product_values = cls.extract_product_values_from_ebay_data(
            product_data
        )

        product_values.update({
            'products': [('create', [{
                'ebay_item_id': product_data['Item']['ItemID']['value'],
                'description': product_data['Item']['Description']['value'],
                'code': product_data['Item'].get('SKU', None) and
                    product_data['Item']['SKU']['value'],
            }])],
        })

        product_template, = Template.create([product_values])

        return product_template.products[0]

    @classmethod
    def export_inventory_to_ebay(cls, products):
        """Export inventory of the products to the eBay account in context
        """
        SellerAccount = Pool().get('ebay.seller.account')
        Location = Pool().get('stock.location')

        seller_account = SellerAccount(
            Transaction().context['ebay_seller_account']
        )
        locations = Location.search([('type', '=', 'storage')])
        api = seller_account.get_trading_api()

        # eBay can process only 4 inventory updates in one call,
        # hence we iterate over products in batches of 4
        def batch(products, n=4):
            for each in range(0, len(products), n):
                yield products[each:min(each + n, len(products))]

        with Transaction().set_context({'locations': map(int, locations)}):
            for product_batch in batch(products):
                update_list = []
                for product in product_batch:
                    update_list.append({
                        'ItemID': product.ebay_item_id,
                        'Quantity': str(int(product.template.quantity)),
                    })
                api.execute(
                    'ReviseInventoryStatus', {
                        'InventoryStatus': update_list
                    }
                ).response_dict()

    @classmethod
    def export_catalog_to_ebay(cls, products):
        """Export the selected products to the eBay account in context
        """
        SellerAccount = Pool().get('ebay.seller.account')
        Location = Pool().get('stock.location')

        seller_account = SellerAccount(
            Transaction().context['ebay_seller_account']
        )
        locations = Location.search([('type', '=', 'storage')])
        api = seller_account.get_trading_api()

        with Transaction().set_context({'locations': map(int, locations)}):
            for product in products:
                product_data = {
                    'Item': {
                        'Title': product.template.name,
                        'Description': product.description or
                            product.template.name,
                        'PrimaryCategory': {
                            'CategoryID': product.template.ebay_category_id
                        },
                        'StartPrice': str(product.template.list_price),
                        'CategoryMappingAllowed': 'true',
                        'Country': seller_account.listing_country.code,
                        'ConditionID': '1000',
                        'Currency': seller_account.company.currency.code,
                        'DispatchTimeMax': str(
                            product.template.ebay_max_dispatch_time
                        ),
                        'ListingDuration':
                            product.template.ebay_listing_duration,
                        'ListingType': 'FixedPriceItem',
                        'PaymentMethods': 'PayPal',
                        'PayPalEmailAddress':
                            seller_account.paypal_email_address,
                        'PictureDetails': {
                            'PictureURL': 'http://i1.sandbox.ebayimg.com/03/i/'
                                '00/30/07/20_1.JPG?set_id=880000500',
                        },
                        'PostalCode': seller_account.company.
                            party.addresses[0].zip,
                        'Quantity': str(int(product.template.quantity)),
                        'ListingDetails': {
                            'BuyItNowAvailable': True
                        },
                        'ReturnPolicy': {
                            'ReturnsAcceptedOption': product.template.
                                ebay_return_policy_option,
                            'RefundOption': product.template.
                                ebay_refund_option,
                            'ReturnsWithinOption': product.template.
                                ebay_returns_within_option,
                            'Description': product.template.
                                ebay_refund_description,
                            'ShippingCostPaidByOption': product.template.
                                ebay_refund_shipping_cost_paid_by_option,
                        },
                        'ShippingDetails': {
                            'ShippingType': product.template.
                                ebay_shipping_type,
                            'ShippingServiceOptions': {
                                'ShippingServicePriority': '1',
                                'ShippingService': product.template.
                                    ebay_shipping_service,
                                'ShippingServiceCost': str(
                                    product.template.ebay_shipping_cost
                                )
                            }
                        }
                    }
                }
                response = api.execute('AddItem', product_data).response_dict()

                if response.get('ItemID'):
                    cls.write([product], {
                        'ebay_item_id': response['ItemID']['value']
                    })
                    return

                if response.get('Errors'):
                    if isinstance(response['Errors'], dict):
                        errors = [response['Errors']]
                    else:
                        errors = response['Errors']
                    cls.raise_user_error(
                        'ebay_error', ', '.join([
                            error['LongMessage']['value']
                                for error in errors
                        ])
                    )
