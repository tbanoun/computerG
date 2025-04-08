from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = "product.template"


    showDelivryMessage = fields.Boolean(default=True)