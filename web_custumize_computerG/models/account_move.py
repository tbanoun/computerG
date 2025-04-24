from odoo import api, models, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    qtyWT = fields.Float()
    qtySu = fields.Float()
    showDelivryMessage = fields.Boolean()
    continue_seling = fields.Boolean()

    def write(self, vals):
        for line in self:
            if line.product_id:
                line_vals = vals.copy()
                line_vals['qtyWT'] = line.product_id.virtual_available or 0
                line_vals['qtySu'] = line.product_id.product_tmpl_id.qty_available_wt or 0
                line_vals['showDelivryMessage'] = line.product_id.product_tmpl_id.showDelivryMessage or False
                line_vals['continue_seling'] = line.product_id.product_tmpl_id.continue_seling or False
                super(AccountMoveLine, line).write(line_vals)
            else:
                super(AccountMoveLine, line).write(vals)
        return True


    def create(self, vals_list):
        res = super(AccountMoveLine, self).create(vals_list)
        qtyWT = res.product_id.virtual_available or 0
        qtySu = res.product_id.product_tmpl_id.qty_available_wt or 0
        showDelivryMessage = res.product_id.product_tmpl_id.showDelivryMessage or False
        continue_seling = res.product_id.product_tmpl_id.continue_seling or False
        res.sudo().write(
            {
                'qtyWT': qtyWT,
                'qtySu': qtySu,
                'showDelivryMessage': showDelivryMessage,
                'continue_seling': continue_seling,
            }
        )
        print('qtySu', qtySu)
        print('qtyWT', qtyWT)
        return res