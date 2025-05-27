
{
    'name': 'Reports Marginal VAT',
    'description': '',
    'summary': '',
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

        #views
        'views/account_taxes.xml',
    ],
}
