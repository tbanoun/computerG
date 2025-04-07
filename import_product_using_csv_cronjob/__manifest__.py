# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Update and Import Product using csv url and cronJob',
    'version': '16.0.0.1',
    'category': 'Tools',
    'summary': '',
    'description': "",
    'author': 'digitalai_academy',
    'website': 'https://www.digitalai.academy.com',
    'depends': ['base', 'stock', 'account'],
    'data': [
        # security
        'security/ir.model.access.csv',
        # data
        'data/data.xml',
        'data/ir_data_cron_job.xml',

        # views
        'views/product_import_csv.xml',
        'views/product_import_history.xml',
        'views/product_category.xml',
        'views/stock_quant.xml',
        'views/product_product.xml',
    ],
    'qweb': [
    ],
    'demo': [],
    'test': [],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    "images": ["static/description/icon.gif"],
}
