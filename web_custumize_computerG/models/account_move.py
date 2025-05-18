from odoo import api, models, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    qtyWT = fields.Float()
    qtySu = fields.Float()
    showDelivryMessage = fields.Boolean()
    continue_seling = fields.Boolean()

    def write(self, vals):
        res = super().write(vals)

        update_vals = []
        for line in self:
            if line.product_id:
                update_vals.append((
                    line.id,
                    {
                        'qtyWT': line.product_id.virtual_available or 0,
                        'qtySu': line.product_id.product_tmpl_id.qty_available_wt or 0,
                        'showDelivryMessage': line.product_id.product_tmpl_id.showDelivryMessage or False,
                        'continue_seling': line.product_id.product_tmpl_id.continue_seling or False,
                    }
                ))

        for line_id, vals_to_update in update_vals:
            self.browse(line_id).sudo().write(vals_to_update)

        return res

    def create(self, vals_list):
        res = super(AccountMoveLine, self).create(vals_list)

        for line in res:
            product = line.product_id
            template = product.product_tmpl_id

            qtyWT = product.virtual_available or 0
            qtySu = template.qty_available_wt or 0
            showDelivryMessage = template.showDelivryMessage or False
            continue_seling = template.continue_seling or False

            line.sudo().write({
                'qtyWT': qtyWT,
                'qtySu': qtySu,
                'showDelivryMessage': showDelivryMessage,
                'continue_seling': continue_seling,
            })

            print('qtySu', qtySu)
            print('qtyWT', qtyWT)

        return res
