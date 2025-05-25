# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Google Sheet Update Product Csv Cronjob',
    'version': '16.0.0.1',
    'category': 'Tools',
    'summary': '',
    'description': "",
    'author': 'digitalai_academy',
    'website': 'https://www.digitalai.academy',
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
        'views/product_template.xml'
    ],
    'qweb': [
    ],
    'demo': [],
    'test': [],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    "images": ["static/description/icon.png"],
}
