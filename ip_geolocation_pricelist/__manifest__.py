{
    'name': 'pricelist with IP-Geolocation By Soft G',
    'summary': 'This module geolocates a new customer and set the right pricelist according to its geolocation',
    'description': 'This module geolocates a new customer and set the right pricelist according to its geolocation. IP is cached during a configurable period to avoid asking geolocation for the same IP at each website page.',
    'category': 'Website',
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'author': 'SoftG',
    'website': 'softg.dev',
    'phone': '+357 96 69 96 49',
    'Email': 'Odoo@softg.dev',
    'version': '16.0.1.0.1',
    'depends': [
        'base',
        'mail',
        'portal',
        'website_sale',
        'sale_management',
    ],
    'images': [
        'static/description/icon.png',
    ],
    'data': [
        'data/website_cache_ip_cleaner.xml',
        'views/product_pricelist_view.xml',
        'views/res_config_settings_view.xml',
    ]
}
