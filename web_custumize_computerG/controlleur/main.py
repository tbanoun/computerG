from odoo import http
from odoo.http import request
import requests
import logging

_logger = logging.getLogger(__name__)


class ProductInfoController(http.Controller):

    @http.route('/api/get_product_info', type='json', auth='public')
    def get_product_info(self, product_id):
        product = request.env['product.product'].sudo().browse(int(product_id))

        # get the shiping method
        duration = None
        company_shiping = None
        amount_shiping = None
        # if country_code:
        #     shiping_method_id = request.env['delivery.carrier'].sudo().search(
        #         [
        #             ('country_ids.code', '=', country_code)
        #         ]
        #     ,limit=1
        #     )
        #     if shiping_method_id:
        #         duration = shiping_method_id.shiping_duration
        #         company_shiping = shiping_method_id.company_shiping.name
        #         amount_shiping = shiping_method_id.amount_shiping





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
        }

        return result
