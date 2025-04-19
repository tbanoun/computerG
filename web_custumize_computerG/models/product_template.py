from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = "product.template"


    showDelivryMessage = fields.Boolean(default=True)
    messageDelivryTimeRemoteStock = fields.Char('Delivery Time – Remote Stock Message', default='Ship 4-8 Days')
    messageDelivryTimeStock = fields.Char('Delivery Time – Stock Message', default='Ship 1-2 Days')

    def _compute_dr_show_out_of_stock(self):
        for product in self:
            product.dr_show_out_of_stock = 'OUT_OF_STOCK'


    # out_of_stock_message_text = fields.Char(compute='_compute_dr_show_out_of_stock', compute_sudo=True)
    out_of_stock_message_text = fields.Text(compute='_compute_dr_show_out_of_stock', string="Out-of-Stock Text Message", default="Ask for Availability",
                                            translate=True)

    def _compute_out_of_stock_message_text(self):
        for rec in self:
            rec.out_of_stock_message_text = ''
            if rec.virtual_available > 0:
                rec.out_of_stock_message_text = rec.messageDelivryTimeStock
            elif rec.qty_available_wt > 0:
                rec.out_of_stock_message_text = rec.messageDelivryTimeRemoteStock
            else:
                rec.out_of_stock_message_text = rec.out_of_stock_message


class ProductProduct(models.Model):
    _inherit = "product.product"


    showDelivryMessage = fields.Boolean(related='product_tmpl_id.showDelivryMessage')
    messageDelivryTimeRemoteStock = fields.Char(related='product_tmpl_id.messageDelivryTimeRemoteStock')
    messageDelivryTimeStock = fields.Char(related='product_tmpl_id.messageDelivryTimeStock')