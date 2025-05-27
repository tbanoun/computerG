# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Config supplier Csv Cronjob',
    'version': '16.0.0.1',
    'category': 'Tools',
    'summary': '',
    'description': "",
    'author': 'SoftG',
    'website': 'softg.dev',
    'phone': '+357 96 69 96 49',
    'Email': 'Odoo@softg.dev',
    'depends': ['base', 'stock', 'account'],
    'data': [
        # security
        'security/ir.model.access.csv',

        #data
        # 'data/ir_data_cron_job.xml',

        # views
        'views/product_category.xml',
        'views/stock_quant.xml',
        'views/product_product.xml',
        'views/res_config_setting_views.xml',
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
