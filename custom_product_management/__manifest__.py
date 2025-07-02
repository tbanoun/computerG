{
    'name': 'Custom Product Management',
    'version': '16.0.1.0.0',
    'category': 'Sales/Inventory',
    'summary': 'Custom product fields and export functionality',
    'description': """
        Custom Product Management Module
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'sale', 'stock', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/product_export_wizard_views.xml',
        'views/product_template_views.xml',
        'views/stock_picking_views.xml',
     
    ],
    'assets': {
        'web.assets_backend': [
            'custom_product_management/static/src/js/product_tree_extend.js',
            'custom_product_management/static/src/js/product_kanban_extend.js',
            'custom_product_management/static/src/xml/product_list_button.xml',
            'custom_product_management/static/src/xml/product_kanban_button.xml',
        ]
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}