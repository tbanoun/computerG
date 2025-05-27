# -*- coding: utf-8 -*-

{
    'name': 'Login/signup reCAPTCHA',
    'version': '16.0.1.0.1',
    'summary': """This module integrates reCAPTCHA to protect your website from bot attacks.""",
    'description': """CAPTCHA helps you detect abusive traffic on your website without any user friction. 
    The user must register their  domain with CAPTCHA site to get site key add same with our code and use the app.
    login page, signup page,login,signup,protection,site protection,fake login,fake signup,website login, 
    website,captcha,captcha,version 16 protectionwebsite protection,robot attack,security,secure login
    ,secure signup, contact us...""",
    'author': 'SoftG',
    'website': 'softg.dev',
    'phone': '+357 96 69 96 49',
    'Email': 'Odoo@softg.dev',
    'category': 'Extra Tools',
    'depends': ['base'],
    'images': ['static/description/banner.gif'],
    'license': 'LGPL-3',
    'depends': ['base','web', 'website_mass_mailing'],
    'data': [
        'views/captcha_views.xml'
        ],
    'installable': True,
    'auto_install': False,

}