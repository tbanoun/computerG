from odoo import fields, models, api
from bs4 import BeautifulSoup as bs


class ProductTemplate(models.Model):
    _inherit = "product.template"

    continue_seling = fields.Boolean(default=True)

    allow_out_of_stock_order = fields.Boolean(string='Continue selling when out-of-stock',
                                              compute="_computeContinueSelling")

    def _computeContinueSelling(self):
        for rec in self:
            if rec.qty_available_wt + rec.virtual_available <= 0:
                rec.allow_out_of_stock_order = False
            elif rec.qty_available_wt <= 0 and rec.showDelivryMessage == False:
                rec.allow_out_of_stock_order = False
            else:
                rec.allow_out_of_stock_order = True

    out_of_stock_message = fields.Char(string="Out-of-Stock Message")
    showDelivryMessage = fields.Boolean(default=True)
    messageDelivryTimeRemoteStock = fields.Char('Delivery Time – Remote Stock Message', default='Ship 4-8 Days')
    messageDelivryTimeStock = fields.Char('Delivery Time – Stock Message', default='Ship 1-2 Days')

    def _compute_dr_show_out_of_stock(self):
        for product in self:
            product.dr_show_out_of_stock = 'OUT_OF_STOCK'

    # out_of_stock_message_text = fields.Char(compute='_compute_dr_show_out_of_stock', compute_sudo=True)
    out_of_stock_message_text = fields.Text(compute='_compute_out_of_stock_message_text',
                                            string="Out-of-Stock Text Message", default="Ask for Availability",
                                            translate=True)

    def _compute_out_of_stock_message_text(self):
        text = ''
        for rec in self:
            rec.out_of_stock_message_text = ''
            if rec.virtual_available > 0:
                text = rec.messageDelivryTimeStock
                # rec.out_of_stock_message_text = rec.messageDelivryTimeStock
            elif rec.qty_available_wt > 0:
                text = rec.messageDelivryTimeRemoteStock
                # rec.out_of_stock_message_text = rec.messageDelivryTimeRemoteStock
            else:
                text = rec.out_of_stock_message
                # rec.out_of_stock_message_text = rec.out_of_stock_message
            text = str(text)
            soup = bs(text, 'html.parser')
            if soup:
                text_soup = soup.get_text()
            else:
                text_soup = text
            rec.out_of_stock_message_text = text_soup


class ProductProduct(models.Model):
    _inherit = "product.product"

    showDelivryMessage = fields.Boolean(related='product_tmpl_id.showDelivryMessage')
    messageDelivryTimeRemoteStock = fields.Char(related='product_tmpl_id.messageDelivryTimeRemoteStock')
    messageDelivryTimeStock = fields.Char(related='product_tmpl_id.messageDelivryTimeStock')
