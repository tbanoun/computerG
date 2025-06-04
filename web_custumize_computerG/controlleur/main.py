from odoo import http
from odoo.http import request
import requests
import logging

_logger = logging.getLogger(__name__)


class ProductInfoController(http.Controller):

    @http.route('/api/get_product_info', type='json', auth='public')
    def get_product_info(self, product_id):
        product = request.env['product.product'].sudo().browse(int(product_id))

        # Détection du pays
        country_name = ''
        country_code = ''
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


        result =  {
            'id': product.id,
            'virtual_available': product.virtual_available if product.virtual_available else 0 ,
            'virtual_available_product_tmpl_id': product.product_tmpl_id.virtual_available if product.product_tmpl_id.virtual_available else 0 ,
            'qty_available_wt': product.qty_available_wt if product.qty_available_wt else 0,
            'showDelivryMessage': product.product_tmpl_id.showDelivryMessage if product.product_tmpl_id.showDelivryMessage else False,
            'messageDelivryTimeRemoteStock': product.product_tmpl_id.messageDelivryTimeRemoteStock if product.product_tmpl_id.messageDelivryTimeRemoteStock else '',
            'messageDelivryTimeStock': product.product_tmpl_id.messageDelivryTimeStock if product.product_tmpl_id.messageDelivryTimeStock else '',
            'out_of_stock_message': product.product_tmpl_id.out_of_stock_message if product.product_tmpl_id.out_of_stock_message else '',
            'allow_out_of_stock_order': product.product_tmpl_id.allow_out_of_stock_order if product.product_tmpl_id.allow_out_of_stock_order else '',
            'continue_seling': product.product_tmpl_id.continue_seling if product.product_tmpl_id.continue_seling else False,
            'show_qty': product.product_tmpl_id.show_availability if product.product_tmpl_id.show_availability else False,
            'country': country_name,
            'country_code': country_code,
        }

        print(f'\n\n country ==> {country_name} \n\n')
        print(f'\n\n country_code ==> {country_code} \n\n')

        return result
