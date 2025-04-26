# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol Infotech Private Limited. (<https://www.droggol.com/>)

{
    'name': 'web custumize computer G',
    'description': '',
    'summary': '',
    'category': 'Theme/eCommerce',
    'version': '16.0.0.0.1',
    'depends': ['theme_prime', 'sale', 'import_product_using_csv_cronjob', 'website', 'website_sale',
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
        # website
        # 'views/webSite/button_add_to_wishlist.xml',
        'views/webSite/product_detail_page.xml',
        'views/webSite/layout.xml',
        'views/webSite/shop_layout.xml',
        'views/webSite/button_payment.xml',
        'views/webSite/carte_sidbar.xml',
        'views/webSite/template_adress_customer.xml',

        # backend
        'views/product_template.xml',
        'views/product_pricelist.xml',

        # reports
        'reports/update_invoice.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'web_custumize_computerG/static/src/js/variant_mixin.js',
        ],
        'web.assets_backend': [
            'web_custumize_computerG/static/src/js/variant_mixin.js',
        ],
    },
    'installable': True,
    'application': True,
}
