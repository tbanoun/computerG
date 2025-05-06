from odoo import api, models, fields
from odoo.tools.translate import html_translate
from bs4 import BeautifulSoup as bs


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    qtyWT = fields.Float()
    qtySu = fields.Float()
    showDelivryMessage = fields.Boolean()
    continue_seling = fields.Boolean()


class ProductTemplate(models.Model):
    _inherit = "product.template"

    out_of_stock_message = fields.Html(string="Out-of-Stock Message", translate=html_translate)
    showDelivryMessage = fields.Boolean(default=True)
    messageDelivryTimeRemoteStock = fields.Char('Delivery Time – Remote Stock Message')
    messageDelivryTimeStock = fields.Char('Delivery Time – Stock Message')


class ProductProduct(models.Model):
    _inherit = "product.product"

    showDelivryMessage = fields.Boolean(related='product_tmpl_id.showDelivryMessage')
    messageDelivryTimeRemoteStock = fields.Char(related='product_tmpl_id.messageDelivryTimeRemoteStock')
    messageDelivryTimeStock = fields.Char(related='product_tmpl_id.messageDelivryTimeStock')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qtyWT = fields.Float()
    qtySu = fields.Float()
    showDelivryMessage = fields.Boolean()
    continue_seling = fields.Boolean()


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
