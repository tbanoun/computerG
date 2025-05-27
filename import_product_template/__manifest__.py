{
    'name': 'Import Product Template',
    'description': '''This module is designed to simplify the import and export of product templates in Odoo. It allows users to import products with all necessary details, including attributes and their corresponding values, supporting both creation and update of existing records. Additionally, it enables the export of product data for easy sharing or backup. This tool is ideal for businesses that handle large product catalogs and need efficient data management workflows.''',
    'summary': 'This module facilitates the import and export of product templates with complete information, including attributes and their values.',
    'category': 'stock/product',
    'version': '16.0.0.0.1',
    'depends': ['base', 'stock', 'sale'],
    'license': 'OPL-1',
    'author': 'SoftG',
    'website': 'softg.dev',
    'phone': '+357 96 69 96 49',
    'Email': 'Odoo@softg.dev',
    'images': [
        'static/description/prime_cover.png',
    ],
    'data': [
        # security
        'security/ir.model.access.csv',
        # views
        'views/product_template_import.xml',
        'views/product_template_list.xml',
    ],
}
