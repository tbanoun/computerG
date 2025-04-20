# -*- coding: utf-8 -*-

{
    'name': 'Login/signup reCAPTCHA',
    'version': '16.0.1.0.1',
    'summary': """Protect robot login and signup with reCAPTCHA""",
    'description': """CAPTCHA helps you detect abusive traffic on your website without any user friction. 
    The user must register their  domain with CAPTCHA site to get site key add same with our code and use the app.
    login page, signup page,login,signup,protection,site protection,fake login,fake signup,website login, 
    website,captcha,captcha,version 16 protectionwebsite protection,robot attack,security,secure login
    ,secure signup, contact us...""",
    'author': 'Tahar BANOUN',
    'company': 'digitalai-academy',
    'website': 'https://www.digitalai.academy',
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