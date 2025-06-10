from odoo import api, models, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    display_message = fields.Boolean(default=False)
    qtyWT = fields.Float()
    qtySu = fields.Float()
    showDelivryMessage = fields.Boolean()
    continue_seling = fields.Boolean()

