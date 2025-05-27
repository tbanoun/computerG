{
    'name': 'Import Product Template',
    'description': '',
    'summary': '',
    'category': 'stock/product',
    'version': '16.0.0.0.1',
    'depends': ['base','stock','sale'],
    'license': 'OPL-1',
    'author': 'SoftG',
    'website': 'softg.dev',
    'phone': '+357 96 69 96 49',
    'Email': 'Odoo@softg.dev',
    'images': [
        'static/description/prime_cover.png',
    ],
    'data': [
        #security
        'security/ir.model.access.csv',
        #views
        'views/product_template_import.xml',
        'views/product_template_list.xml',
    ],
}
