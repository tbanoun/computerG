from odoo import models, fields, api, Command


class AccountTax(models.Model):
    _inherit = 'account.tax'

    showOnInvoice = fields.Boolean('Is Marginal VAT')





class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    price_tax = fields.Monetary(
        string='Total',
        compute='_compute_totals_tax', store=True,
        currency_field='currency_id',
    )

    @api.depends('price_subtotal', 'price_subtotal')
    def _compute_totals_tax(self):
        for line in self:
            price_total = line.price_total or 0
            price_subtotal = line.price_subtotal or 0
            line.price_tax = price_total - price_subtotal