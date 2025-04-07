from odoo import api, models, fields
from bs4 import BeautifulSoup as bs
class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    titleDisplayInvoice = fields.Char(compute='_computeTitleDisplayTerm')

    def _computeTitleDisplayTerm(self):
        for rec in self:
            soup = bs(rec.note, 'html.parser')
            text = ''
            if soup:
                text = soup.get_text()
            try:
                rec.titleDisplayInvoice = f'{rec.name} - {text}'
            except Exception:
                rec.titleDisplayInvoice = rec.name