from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import QueryURL
import requests

class CustomWebsiteSale(WebsiteSale):

    def _prepare_product_values(self, product, category, search, **kwargs):

        res = super(CustomWebsiteSale, self)._prepare_product_values(product, category, search)
        # Détection du pays
        country_name = request.env.user.partner_id.country_id.name
        country_code = request.env.user.partner_id.country_id.code
        if not country_name:
            ip = request.httprequest.remote_addr
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
            if response.status_code == 200:
                result = response.json()
                country_code = result.get('countryCode')
                country_name = result.get('country')
            else:
                response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)
                if response.status_code == 200:
                    result = response.json()
                    country_code = result.get('country_code')
                    country_name = result.get('country_name')

        res['country'] = country_name
        res['country_code'] = country_code
        return res