from odoo import http
from odoo.http import request


class ProductInfoController(http.Controller):

    @http.route('/api/get_product_info', type='json', auth='public')
    def get_product_info(self, product_id):
        product = request.env['product.product'].sudo().browse(int(product_id))
        return {
            'id': product.id,
            'virtual_available': product.virtual_available if product.virtual_available else 0 ,
            'qty_available_wt': product.qty_available_wt if product.qty_available_wt else 0,
            'showDelivryMessage': product.product_tmpl_id.showDelivryMessage if product.product_tmpl_id.showDelivryMessage else False,
            'messageDelivryTimeRemoteStock': product.product_tmpl_id.messageDelivryTimeRemoteStock if product.product_tmpl_id.messageDelivryTimeRemoteStock else '',
            'messageDelivryTimeStock': product.product_tmpl_id.messageDelivryTimeStock if product.product_tmpl_id.messageDelivryTimeStock else '',
            'out_of_stock_message': product.product_tmpl_id.out_of_stock_message if product.product_tmpl_id.out_of_stock_message else '',
            'allow_out_of_stock_order': product.product_tmpl_id.allow_out_of_stock_order if product.product_tmpl_id.allow_out_of_stock_order else '',
            'continue_seling': product.product_tmpl_id.continue_seling if product.product_tmpl_id.continue_seling else False,
        }
