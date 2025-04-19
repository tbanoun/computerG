from odoo import fields, models, api
from bs4 import BeautifulSoup as bs

class ProductTemplate(models.Model):
    _inherit = "product.template"


    showDelivryMessage = fields.Boolean(default=True)
    messageDelivryTimeRemoteStock = fields.Char('Delivery Time – Remote Stock Message', default='Ship 4-8 Days')
    messageDelivryTimeStock = fields.Char('Delivery Time – Stock Message', default='Ship 1-2 Days')

    def _compute_dr_show_out_of_stock(self):
        for product in self:
            product.dr_show_out_of_stock = 'OUT_OF_STOCK'


    # out_of_stock_message_text = fields.Char(compute='_compute_dr_show_out_of_stock', compute_sudo=True)
    out_of_stock_message_text = fields.Text(compute='_compute_out_of_stock_message_text', string="Out-of-Stock Text Message", default="Ask for Availability",
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
            soup = bs(text, 'html.parser')
            rec.out_of_stock_message_text = soup.get_text()



class ProductProduct(models.Model):
    _inherit = "product.product"


    showDelivryMessage = fields.Boolean(related='product_tmpl_id.showDelivryMessage')
    messageDelivryTimeRemoteStock = fields.Char(related='product_tmpl_id.messageDelivryTimeRemoteStock')
    messageDelivryTimeStock = fields.Char(related='product_tmpl_id.messageDelivryTimeStock')