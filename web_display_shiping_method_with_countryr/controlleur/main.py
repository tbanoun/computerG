from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import QueryURL
import requests

class CustomWebsiteSale(WebsiteSale):

    def _prepare_product_values(self, product, category, search, **kwargs):

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


        ProductCategory = request.env['product.public.category']

        if category:
            category = ProductCategory.browse(int(category)).exists()

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        keep = QueryURL(
            '/shop',
            **self._product_get_query_url_kwargs(
                category=category and category.id,
                search=search,
                **kwargs,
            ),
        )

        # Needed to trigger the recently viewed product rpc
        view_track = request.website.viewref("website_sale.product").track

        return {
            'search': search,
            'category': category,
            'pricelist': request.website.get_current_pricelist(),
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'keep': keep,
            'categories': ProductCategory.search([('parent_id', '=', False)]),
            'main_object': product,
            'product': product,
            'add_qty': 1,
            'view_track': view_track,
            'country': country_name,
            'country_code': country_code
        }