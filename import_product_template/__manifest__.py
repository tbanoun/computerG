{
    'name': 'Import Product Template',
    'description': '',
    'summary': '',
    'category': 'stock/product',
    'version': '16.0.0.0.1',
    'depends': ['base','stock'],
    'license': 'OPL-1',
    'author': 'Tahar BANOUN',
    'company': 'https://digitalai.academy/',
    'maintainer': 'Tahar BANOUN',
    'website': 'https://digitalai.academy/',
    'images': [
        'static/description/prime_cover.png',
    ],
    'data': [
        #security
        'security/ir.model.access.csv',
        #views
        'views/product_template_import.xml',
    ],
}
