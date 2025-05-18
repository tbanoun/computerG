from odoo import api, models, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    qtyWT = fields.Float()
    qtySu = fields.Float()
    showDelivryMessage = fields.Boolean()
    continue_seling = fields.Boolean()

    def write(self, vals):
        res = super().write(vals)
        update_lines = self.filtered(lambda l: l.product_id)

        for line in update_lines:
            product = line.product_id
            template = product.product_tmpl_id

            line.sudo().write({
                'qtyWT': product.virtual_available or 0,
                'qtySu': template.qty_available_wt or 0,
                'showDelivryMessage': template.showDelivryMessage or False,
                'continue_seling': template.continue_seling or False,
            })

        return res

    def create(self, vals_list):
        res = super().create(vals_list)

        for line in res.filtered(lambda l: l.product_id):
            product = line.product_id
            template = product.product_tmpl_id

            line.sudo().write({
                'qtyWT': product.virtual_available or 0,
                'qtySu': template.qty_available_wt or 0,
                'showDelivryMessage': template.showDelivryMessage or False,
                'continue_seling': template.continue_seling or False,
            })

        return res

