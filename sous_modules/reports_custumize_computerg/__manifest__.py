# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol Infotech Private Limited. (<https://www.droggol.com/>)

{
    'name': 'Reports custumize computerg',
    'summary': '''The web_customize_computerg module consolidates all modified web features implemented on your Odoo website. This includes enhancements like customizable delivery messages and tailored invoice reports, improving communication and documentation processes. It provides a centralized solution to manage various web customizations for a better user and customer experience.''',
    'description': 'This module allows you to customize the design and structure of the Sale Order and Invoice PDF reports in Odoo.',
    'category': 'Theme/eCommerce',
    'version': '16.0.0.0.1',
    'depends': ['web_custumize_computerG'],
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
        # reports
        'reports/update_invoice.xml',
        'reports/update_delivery_note.xml',
    ],
    'installable': True,
    'application': True,
}
