# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol Infotech Private Limited. (<https://www.droggol.com/>)

{
    'name': 'custumize computerG for odoo16',
    'description': '',
    'summary': '',
    'category': 'stock',
    'version': '16.0.0.0.1',
    'depends': ['sale', 'stock', 'website_sale',
                'website_sale_stock'],
    'license': 'OPL-1',
    'author': 'Tahar BANOUN',
    'company': 'https://digitalai.academy/',
    'maintainer': 'Tahar BANOUN',
    'website': 'https://digitalai.academy/',
    'images': [
        'static/description/prime_cover.png',
    ],
    'data': [
        # views
        'views/product_template.xml',

    ],
    'installable': True,
    'application': True,
}
