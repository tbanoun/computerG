from odoo import api, models, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    qtyWT = fields.Float()
    qtySu = fields.Float()
    showDelivryMessage = fields.Boolean()
    continue_seling = fields.Boolean()


class ProductTemplate(models.Model):
    _inherit = "product.template"

    out_of_stock_message = fields.Char(string="Out-of-Stock Message")
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
