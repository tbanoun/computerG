from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'


    def write(self, vals):
        if 'standard_price' not in vals:
            vals['standard_price'] = self.product_tmpl_id.standard_price
        elif vals['standard_price'] <= 0:
            vals['standard_price'] = self.product_tmpl_id.standard_price
        res = super(ProductProduct, self).write(vals)
        return  res


    def create(self, vals_list):
        res = super(ProductProduct, self).create(vals_list)
        res.sudo().write(
            {
                'standard_price': res.product_tmpl_id.standard_price
            }
        )
        return res