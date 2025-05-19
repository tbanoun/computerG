# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.tools import float_compare

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qtyWT = fields.Float()
    qtySu = fields.Float()
    showDelivryMessage = fields.Boolean()
    continue_seling = fields.Boolean()

    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        return res

    def create(self, vals_list):
        res = True
        for vals in vals_list:
            try:
                product_id = vals.get('product_template_id')
                product = self.env['product.template'].sudo().browse(int(product_id))
                vals['qtyWT'] = product.virtual_available
                vals['qtySu'] =product.qty_available_wt
                vals['showDelivryMessage'] = product.showDelivryMessage
                vals['continue_seling'] =  product.continue_seling
            except Exception as e:
                print(e)

            res = super(SaleOrderLine, self).create(vals)
        return  res