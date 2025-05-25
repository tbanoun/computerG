from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    supplier_id = fields.Selection(
        [
            ('other', 'Other'),
            ('multitech', 'Multitech'),
            ('infoQuest', 'InfoQuest'),
            ('logiCom', 'LogiCom'),
        ], string='Product Condition', default='other')
