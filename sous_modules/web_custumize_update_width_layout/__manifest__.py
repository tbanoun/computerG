# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol Infotech Private Limited. (<https://www.droggol.com/>)

{
    'name': 'web custumize update width layout',
    'description': '''This module enhances the payment section on the checkout page by adjusting its layout to better accommodate and display the delivery message. It ensures that important shipping or delivery-related information is clearly visible to the customer during the payment process, improving transparency and overall user experience.''',
    'summary': 'Improve the payment section layout to clearly display the delivery message.',
    'category': 'Theme/eCommerce',
    'version': '16.0.0.0.1',
    'depends': ['web', 'theme_prime', 'sale', 'website', 'website_sale',
                'website_sale_stock'],
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
        'views/update_layout_website.xml'
    ],
    'installable': True,
    'application': True,
}
