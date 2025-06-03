# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol Infotech Private Limited. (<https://www.droggol.com/>)

{
    'name': 'Web Description Section',
    'description': '''This module customizes the design of the product description section on the product detail page in Odoo. It enhances the layout and visual presentation to improve readability and user experience. The changes may include updated fonts, spacing, titles, borders, and other styling improvements, ensuring the description area is more attractive and consistent with the overall storefront design.''',
    'summary': 'Update the style of the product description section on the product page.',
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
        'views/detail_page_theme_prime.xml'
    ],
    'installable': True,
    'application': True,
}
