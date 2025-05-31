{
    'name': 'Dynamic pricelist with visitors IP-Geolocation',
    'summary': 'This module geolocates a new customer and set the right pricelist according to its geolocation',
    'description': 'This module geolocates a new customer and set the right pricelist according to its geolocation. IP is cached during a configurable period to avoid asking geolocation for the same IP at each website page.',
    'category': 'Website',
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'author': 'Liseo SRL',
    'website': 'https://www.liseo.be',
    'version': '16.0.1.0.1',
    'depends': [
        'base',
        'mail',
        'portal',
        'website_sale',
        'sale_management',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'data': [
        'data/website_cache_ip_cleaner.xml',
        'views/product_pricelist_view.xml',
        'views/res_config_settings_view.xml',
    ],
    'price': 30.00,
    'currency': 'EUR',
}
