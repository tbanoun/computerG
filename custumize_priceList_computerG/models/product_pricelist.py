from odoo import api, fields, models


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    discount_attribute = fields.Float('Discount feature')

