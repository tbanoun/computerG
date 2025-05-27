{
    'name': 'Reports Marginal VAT',
    'description': '''This module allows you to generate detailed reports for Marginal VAT, specifically for invoices and sales orders. It is designed to help businesses comply with VAT regulations by providing clear and structured printouts of applicable transactions under the Marginal VAT scheme.''',
    'summary': 'Module for generating Marginal VAT reports for invoices and sales orders.',
    'category': 'Extra Tools',
    'version': '16.0.0.0.1',
    'depends': ['sale', 'account'],
    'license': 'OPL-1',
    'author': 'SoftG',
    'website': 'softg.dev',
    'phone': '+357 96 69 96 49',
    'Email': 'Odoo@softg.dev',
    'images': [
        'static/description/icon.png',
    ],
    'data': [
        'reports/sale_order_inherit.xml',
        'reports/invoice_inherit.xml',

        # views
        'views/account_taxes.xml',
    ],
}
