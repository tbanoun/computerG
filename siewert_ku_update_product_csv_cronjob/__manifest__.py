# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Siewert-kau Update Product With Csv File And Cronjob',
    'version': '16.0.0.2',
    'category': 'Tools',
    'summary': '',
    'description': "",
    'author': 'digitalai_academy',
    'website': 'https://www.digitalai.academy',
    'depends': ['base', 'stock', 'account', 'config_supplier_csv_cronjob'],
    'data': [
        # security
        'security/ir.model.access.csv',
        # data
        'data/data.xml',
        'data/ir_data_cron_job.xml',

        # views
        'views/product_import_csv.xml',
        'views/product_import_history.xml',
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
