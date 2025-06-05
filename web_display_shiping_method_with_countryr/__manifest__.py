# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol Infotech Private Limited. (<https://www.droggol.com/>)

{
    'name': 'Display shiping method with countryr',
    'description': '''This module extends Odoo's delivery/shipping functionality by dynamically showing the appropriate shipping methods according to the country selected by the customer.''',
    'summary': "This module allows you to display available shipping methods based on the customer's selected delivery country, enhancing transparency and improving user experience during the checkout process.",
    'category': 'Theme/eCommerce',
    'version': '16.0.0.0.1',
    'depends': ['website_sale'],
    'license': 'OPL-1',
    'author': 'SoftG',
    'website': 'softg.dev',
    'phone': '+357 96 69 96 49',
    'Email': 'Odoo@softg.dev',
    'website': 'https://digitalai.academy/',
    'images': [
        'static/description/icon.png',
    ],
    'data': [
        # website
        'views/product_detail_page.xml',
    ],
    'installable': True,
    'application': True,
}
