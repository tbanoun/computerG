from odoo import api, models, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    qtyWT = fields.Float()
    qtySu = fields.Float()
    showDelivryMessage = fields.Boolean()
    continue_seling = fields.Boolean()



    def write(self, vals):
        self._ensure_one()
        qtyWT = self.product_id.virtual_available or 0
        qtySu = self.product_id.product_tmpl_id.qty_available_wt or 0
        showDelivryMessage = self.product_id.product_tmpl_id.showDelivryMessage or False
        continue_seling = self.product_id.product_tmpl_id.continue_seling or False
        vals['qtyWT'] = qtyWT
        vals['qtySu'] = qtySu
        vals['showDelivryMessage'] = showDelivryMessage
        vals['continue_seling'] = continue_seling
        res = super(AccountMoveLine, self).write(vals)
        return res


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