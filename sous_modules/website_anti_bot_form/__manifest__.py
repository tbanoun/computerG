# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol Infotech Private Limited. (<https://www.droggol.com/>)

{
    'name': 'Website anti bot form',
    'description': '''This module enhances the Odoo eCommerce experience by allowing users to search for products by barcode directly from the Shop page on the website.''',
    'summary': 'Adds barcode search functionality to the Odoo website shop page. Allows users to scan or enter a barcode to quickly find a product.',
    'category': 'Theme/eCommerce',
    'version': '16.0.0.0.1',
    'depends': ['web', 'auth_signup'],
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
        'views/login_form.xml',
        'views/register_form.xml'
    ],
    'installable': True,
    'application': True,
}
