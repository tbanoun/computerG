from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
class StockMove(models.Model):
    _inherit = 'stock.move'
    
    shelf_box = fields.Char(
        related='product_id.x_google_categorie',
        string='Shelf-Box',
        readonly=True
    )