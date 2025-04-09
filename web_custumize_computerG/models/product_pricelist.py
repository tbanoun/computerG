from odoo import models, fields


class PricelistInherit(models.Model):
    _inherit = 'product.pricelist'

    showQtyOnStock = fields.Boolean(default=True)
