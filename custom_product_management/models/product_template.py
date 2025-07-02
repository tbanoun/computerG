from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    def action_export_products_wizard(self):
        """Ouvre le wizard d'export des produits"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Export Products to Excel',
            'res_model': 'product.export.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': dict(self.env.context),
        }
    # Rename existing field (if it exists) - we'll use a different technical name
    shelf_box_old = fields.Char(
        string='Shelf-Box (Old)', 
        help='Renamed from Google Category'
    )
    
    # New Shelf-Box field
    x_google_categorie = fields.Char(
        string='Shelf-Box',
        help='New Shelf-Box field'
    )
    
   