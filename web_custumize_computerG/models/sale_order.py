# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.fields import Command
import logging

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qtyWT = fields.Float()
    qtySu = fields.Float()
    showDelivryMessage = fields.Boolean()
    continue_seling = fields.Boolean()

    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        return res

    def create(self, vals_list):
        # S'assurer que c'est une liste
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        new_vals_list = []
        for vals in vals_list:
            try:
                product_id = vals.get('product_template_id')
                product = self.env['product.template'].sudo().browse(int(product_id))
                vals['qtyWT'] = product.virtual_available
                vals['qtySu'] = product.qty_available_wt
                vals['showDelivryMessage'] = product.showDelivryMessage
                vals['continue_seling'] = product.continue_seling
            except Exception as e:
                _logger.warning(f"Erreur lors de la récupération des champs produit : {e}")

            new_vals_list.append(vals)

        return super(SaleOrderLine, self).create(new_vals_list)

    def _prepare_invoice_line(self, **optional_values):
        """Prepare the values to create the new invoice line for a sales order line.

        :param optional_values: any parameter that should be added to the returned invoice line
        :rtype: dict
        """
        self.ensure_one()
        res = {
            'display_type': self.display_type or 'product',
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [Command.set(self.tax_id.ids)],
            'sale_line_ids': [Command.link(self.id)],
            'is_downpayment': self.is_downpayment,
            'qtyWT': self.qtyWT,
            'qtySu': self.qtySu,
            'showDelivryMessage': self.showDelivryMessage,
            'continue_seling': self.continue_seling,
        }
        analytic_account_id = self.order_id.analytic_account_id.id
        if self.analytic_distribution and not self.display_type:
            res['analytic_distribution'] = self.analytic_distribution
        if analytic_account_id and not self.display_type:
            analytic_account_id = str(analytic_account_id)
            if 'analytic_distribution' in res:
                res['analytic_distribution'][analytic_account_id] = res['analytic_distribution'].get(analytic_account_id, 0) + 100
            else:
                res['analytic_distribution'] = {analytic_account_id: 100}
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res