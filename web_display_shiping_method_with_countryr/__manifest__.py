# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol Infotech Private Limited. (<https://www.droggol.com/>)

{
    'name': 'Display shiping method with countryr',
    'description': '''The web_customize_computerg module consolidates all modified web features implemented on your Odoo website. This includes enhancements like customizable delivery messages and tailored invoice reports, improving communication and documentation processes. It provides a centralized solution to manage various web customizations for a better user and customer experience.''',
    'summary': 'The module web_customize_computerg includes all customized web functionalities such as delivery messages and invoice reports.',
    'category': 'Theme/eCommerce',
    'version': '16.0.0.0.1',
    'depends': ['web', 'theme_prime', 'sale', 'config_supplier_csv_cronjob', 'website', 'website_sale',
                'website_sale_stock'],
    'license': 'OPL-1',
    'author': 'SoftG',
    'website': 'softg.dev',
    'phone': '+357 96 69 96 49',
    'Email': 'Odoo@softg.dev',
    'website': 'https://digitalai.academy/',
    'images': [
        'static/description/prime_cover.png',
    ],
    'data': [
        # website
        'views/product_detail_page.xml',
    ],
    'installable': True,
    'application': True,
}
