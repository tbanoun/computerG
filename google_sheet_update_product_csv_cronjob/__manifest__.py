# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Google Sheet Update Product Csv Cronjob',
    'version': '16.0.0.1',
    'category': 'Tools',
    'summary': 'This module simplifies the update of product prices and quantities based on data from suppliers: Multitech, InfoQuest, and LogiCom.',
    'description': '''This module is developed to facilitate the automatic update of product prices and quantities using data provided by the suppliers Multitech, InfoQuest, and LogiCom. It streamlines the synchronization process between supplier inventories and your Odoo system, ensuring that product information remains accurate and up to date. Ideal for businesses managing multiple supplier feeds and looking to maintain real-time inventory and pricing accuracy.''',
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
