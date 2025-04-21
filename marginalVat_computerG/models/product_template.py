from odoo import models, fields, api, Command


class productTemplate(models.Model):
    _inherit = 'product.template'

    productSaleType = fields.Selection([
        ('new', 'New'),
        ('used', 'Used'),
    ], string='Product Condition', default='new')


