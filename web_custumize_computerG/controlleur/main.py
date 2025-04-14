from odoo import http
from odoo.http import request

class ProductInfoController(http.Controller):

    @http.route('/api/get_product_info', type='json', auth='public')
    def get_product_info(self, product_id):
        product = request.env['product.product'].sudo().browse(int(product_id))
        print('product')
        print(product)
        return {
            'id': product.id,
            'virtual_available': product.virtual_available,
            'qty_available_wt': product.qty_available_wt
        }