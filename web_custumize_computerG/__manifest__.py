# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol Infotech Private Limited. (<https://www.droggol.com/>)

{
    'name': 'web custumize computer G',
    'description': '''
    This module is designed to manage supplier configurations in a centralized way. It includes all the common variables and settings required for supplier integration, as well as access menus and other essential configurations. It serves as the core setup point for handling supplier-related operations in the system.''',
    'summary': 'Supplier configuration module with shared settings, variables, and access menus.',
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
        # 'views/webSite/button_add_to_wishlist.xml',
        'views/webSite/product_detail_page.xml',
        'views/webSite/layout.xml',
        'views/webSite/shop_layout.xml',
        'views/webSite/button_payment.xml',
        'views/webSite/carte_sidbar.xml',
        'views/webSite/template_adress_customer.xml',
        'views/webSite/update_layout_website.xml',

        # backend
        'views/product_template.xml',
        'views/product_pricelist.xml',

        # reports
        'reports/update_invoice.xml',
        'reports/update_delivery_note.xml',
    ],
    'installable': True,
    'application': True,
}
