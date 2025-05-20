from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_available_wt = fields.Float(compute="claculateQtyWT")

    stockQuant = fields.Many2one('stock.location', compute='calculateSuplierWherhouse')

    def calculateSuplierWherhouse(self):
        cron_id = self.env['product.import.csv'].sudo().search([('id', '=', 1)], limit=1)
        for rec in self:
            if cron_id:
                if cron_id.stock_id:
                    rec.stockQuant = cron_id.stock_id
                    print(rec.stockQuant)
                    continue
            rec.stockQuant = None


    def unpublishedProduct(self):
        self.is_published = not self.is_published

    def action_view_inventory_supplier(self):
        """ Similar to _get_quants_action except specific for inventory adjustments (i.e. inventory counts). """
        if not self.stockQuant: return None
        action = {
            'name': _('Inventory Adjustments'),
            'view_mode': 'list',
            'view_id': self.env.ref(
                'import_product_using_csv_cronjob.view_stock_quant_tree_inventory_supplier_inherit_stock_account').id,
            'res_model': 'stock.quant',
            'type': 'ir.actions.act_window',
            'domain': [
                ('product_id', '=', self.product_variant_id.id),
                ('location_id', '=', self.stockQuant.id),
            ],
            'help': """
                <p class="o_view_nocontent_smiling_face">
                    {}
                </p><p>
                    {} <span class="fa fa-long-arrow-right"/> {}</p>
                """.format(_('Your stock is currently empty'),
                           _('Press the CREATE button to define quantity for each product in your stock or import them from a spreadsheet throughout Favorites'),
                           _('Import')),
        }
        return action

    def claculateQtyWT(self):
        for rec in self:
            qty = 0.0
            if rec.stockQuant:
                stockQuant_ids = self.env['stock.quant'].sudo().search([
                    ('location_id', '=', rec.stockQuant.id),
                    ('product_id', '=', rec.product_variant_id.id)
                ])
                for stockQuant_id in stockQuant_ids:
                    qty += stockQuant_id.quantity
            rec.sudo().qty_available_wt = qty
