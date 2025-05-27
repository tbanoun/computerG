# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol Infotech Private Limited. (<https://www.droggol.com/>)

{
    'name': 'custumize priceList computerG',
    'description': '''
    This Odoo module is designed to automatically update product prices according to a specified pricelist. It also includes a feature to add a customizable margin profit on top of the base price. The module ensures consistent pricing strategies while allowing flexibility in profit management. Ideal for businesses looking to streamline their pricing workflows with automated calculations and margin control.''',
    'summary': '''This module updates product prices based on a selected pricelist and adds a configurable margin profit to each product.''',
    'category': 'Product/Sales',
    'version': '16.0.0.0.1',
    'depends': ['sale_management', 'stock'],
    'license': 'OPL-1',
    'author': 'SoftG',
    'website': 'softg.dev',
    'phone': '+357 96 69 96 49',
    'Email': 'Odoo@softg.dev',
    'images': [
        'static/description/icon.png',
    ],
    'data': [

        # views
        'views/product_pricelist_item.xml',
        'views/product_product.xml',
        # 'views/product_attribute_views.xml',
    ],
}
