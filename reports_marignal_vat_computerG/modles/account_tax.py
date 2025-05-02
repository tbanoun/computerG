from odoo import models, fields, api, Command


class AccountTax(models.Model):
    _inherit = 'account.tax'

    showOnInvoice = fields.Boolean('Is Marginal VAT')