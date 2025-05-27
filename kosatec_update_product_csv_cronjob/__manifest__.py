# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Kosatec Update Product With Csv File And Cronjob',
    'version': '16.0.0.2',
    'category': 'Tools',
    'summary': 'This module simplifies the update of product prices and quantities based on data from the supplier Kosatec.',
    'description': """This module is developed to facilitate the automatic update of product prices and quantities using data provided by the supplier Kosatec. It ensures that your product catalog remains accurate and synchronized with the supplier’s inventory, reducing manual effort and minimizing errors. This solution is ideal for businesses working with Kosatec and looking to maintain up-to-date pricing and stock levels in Odoo.""",
    'author': 'SoftG',
    'website': 'softg.dev',
    'phone': '+357 96 69 96 49',
    'Email': 'Odoo@softg.dev',
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
        'views/stock_quant.xml',
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
