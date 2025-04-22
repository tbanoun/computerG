from odoo import models, fields, api, Command


class productTemplate(models.Model):
    _inherit = 'product.template'

    productSaleType = fields.Selection([
        ('new', 'New'),
        ('used', 'Used'),
    ], string='Product Condition', default='new')

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        # inherit of the function from account.move to validate a new tax and the priceunit of a downpayment
        res = super(AccountMove, self).action_post()
        # down_payment_lines = self.line_ids.filtered('is_downpayment')
        # for line in down_payment_lines:
        #
        #     if not line.sale_line_ids.display_type:
        #         line.sale_line_ids._compute_name()
        #
        # downpayment_lines = self.line_ids.sale_line_ids.filtered(lambda l: l.is_downpayment and not l.display_type)
        # other_so_lines = downpayment_lines.order_id.order_line - downpayment_lines
        # real_invoices = set(other_so_lines.invoice_lines.move_id)
        # for dpl in downpayment_lines:
        #     try:
        #         dpl.price_unit = dpl._get_downpayment_line_price_unit(real_invoices)
        #         dpl.tax_id = dpl.invoice_lines.tax_ids
        #     except UserError:
        #         # a UserError here means the SO was locked, which prevents changing the taxes
        #         # just ignore the error - this is a nice to have feature and should not be blocking
        #         pass
        return True