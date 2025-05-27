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
    'author': 'SoftG',
    'website': 'softg.dev',
    'phone': '+357 96 69 96 49',
    'Email': 'Odoo@softg.dev',
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
