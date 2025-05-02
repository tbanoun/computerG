
{
    'name': 'Reports Marginal VAT',
    'description': '',
    'summary': '',
    'category': 'Extra Tools',
    'version': '16.0.0.0.1',
    'depends': ['sale', 'account'],
    'license': 'OPL-1',
    'author': 'Tahar BANOUN',
    'company': 'https://digitalai.academy/',
    'maintainer': 'Tahar BANOUN',
    'website': 'https://digitalai.academy/',
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
