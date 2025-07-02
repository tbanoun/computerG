from odoo import models, fields, api 
from odoo.exceptions import UserError
import xlsxwriter
import base64
from io import BytesIO
import logging

_logger = logging.getLogger(__name__)

class ProductExportWizard(models.TransientModel):
    _name = 'product.export.wizard'
    _description = 'Product Export Wizard'
    
    category_ids = fields.Many2many(
        'product.category',
        string='Categories',
        help='Select categories to export. Leave empty to export all categories.'
    )
    
    export_all_categories = fields.Boolean(
        string='Export All Categories',
        default=False,
        help='Export products from all categories'
    )
    
    pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Pricelist',
        required=True,
        # default=lambda self: self._get_default_pricelist(),
        help='Select pricelist for pricing'
    )
    
    # def _get_default_pricelist(self):
    #     """Get default pricelist"""
    #     pricelist = self.env['product.pricelist'].search([
    #         ('company_id', '=', self.env.company.id)
    #     ], limit=1)
    #     if not pricelist:
    #         pricelist = self.env['product.pricelist'].search([], limit=1)
    #     return pricelist.id if pricelist else False
    
    @api.onchange('export_all_categories')
    def _onchange_export_all_categories(self):
        """Clear category selection when export all is checked"""
        if self.export_all_categories:
            self.category_ids = [(5, 0, 0)]
    
    @api.onchange('category_ids')
    def _onchange_category_ids(self):
        """Uncheck export all when specific categories are selected"""
        if self.category_ids:
            self.export_all_categories = False
    
    def _get_product_status(self, product):
        """
        Get product status based on quantity logic:
        - Si forecasted > 0 : "In Stock" (case rouge)
        - Si forecasted = 0 et supplied > 1 : "Ship in 2-3 days" (case jaune)
        """
        # Récupérer les quantités forecasted et supplied pour le produit
        forecasted_qty = 0
        supplied_qty = 0
        
        for variant in product.product_variant_ids:
            # qty_available = quantité disponible (forecasted)
            forecasted_qty += variant.qty_available
            # virtual_available inclut les quantités à recevoir
            # On peut aussi utiliser incoming_qty pour les quantités en approvisionnement
            supplied_qty += getattr(variant, 'incoming_qty', 0)
        
        if forecasted_qty > 0:
            return 'In Stock', 'red'
        elif forecasted_qty == 0 and supplied_qty > 1:
            return 'Ship in 2-3 days', 'yellow'
        else:
            # Cas par défaut si aucune des conditions n'est remplie
            return 'Out of Stock', 'gray'
    
    def action_export_excel(self):
        """Export products to Excel file"""
        try:
            if not self.pricelist_id:
                raise UserError('Please select a pricelist.')
            
            if not self.export_all_categories and not self.category_ids:
                raise UserError('Please select at least one category or check "Export All Categories".')
            
            # Create Excel file in memory
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D7E4BC',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'
            })
            
            cell_format = workbook.add_format({
                'border': 1,
                'text_wrap': True,
                'valign': 'top'
            })
            
            # Status color formats - Mise à jour selon vos spécifications
            status_in_stock_format = workbook.add_format({
                'border': 1,
                'text_wrap': True,
                'valign': 'top',
                'bg_color': '#FF0000'  # Rouge pour "In Stock"
            })
            
            status_ship_format = workbook.add_format({
                'border': 1,
                'text_wrap': True,
                'valign': 'top',
                'bg_color': '#FFFF00'  # Jaune pour "Ship in 2-3 days"
            })
            
            status_out_of_stock_format = workbook.add_format({
                'border': 1,
                'text_wrap': True,
                'valign': 'top',
                'bg_color': '#CCCCCC'  # Gris pour "Out of Stock"
            })
            
            number_format = workbook.add_format({
                'border': 1,
                'num_format': '#,##0.00'
            })
            
            # Headers for the Excel file
            headers = [
                'SKU', 'Brand', 'Status', 'Product Name', 'CPU', 'RAM', 
                'Storage', 'GPU', 'Screen Size', 'Resolution', 'Touchscreen', 
                'OS', 'Grade', 'Battery', 'Warranty', 'QTY', 'Price Ex VAT', 'Promo Price'
            ]
            
            # Get categories to export
            if self.export_all_categories:
                categories = self.env['product.category'].search([])
            else:
                categories = self.category_ids
            
            # If no categories selected, use all categories
            if not categories:
                categories = self.env['product.category'].search([])
            
            # Create separate sheet for each category
            for category in categories:
                # Get products for this category
                domain = [
                    ('categ_id', '=', category.id),
                    ('active', '=', True)
                ]
                
                products = self.env['product.template'].search(domain)
                
                # Skip if no products in this category
                if not products:
                    continue
                
                # Create worksheet with category name
                sheet_name = category.name[:31]  # Excel sheet names are limited to 31 characters
                worksheet = workbook.add_worksheet(sheet_name)
                
                # Write headers
                for col, header in enumerate(headers):
                    worksheet.write(0, col, header, header_format)
                
                # Write product data
                row = 1
                for product in products:
                    # Get price from sales price (list_price) - selon vos spécifications
                    price_ex_vat = product.list_price or 0.0
                    
                    # Appliquer la pricelist si nécessaire
                    try:
                        pricelist_price = self.pricelist_id._get_product_price(
                            product, 1.0, partner=False
                        )
                        # Utiliser le prix de la pricelist si différent du list_price
                        if pricelist_price != product.list_price:
                            price_ex_vat = pricelist_price
                    except:
                        pass  # Garder le list_price en cas d'erreur
                    
                    # Get available quantity (QTY)
                    qty_available = sum(product.product_variant_ids.mapped('qty_available'))
                    
                    # Get product status and color selon votre logique
                    status, status_color = self._get_product_status(product)
                    
                    # Prepare product data
                    # data = [
                    #     product.default_code or '',  # SKU
                    #     getattr(product, 'x_brand', '') or '',  # Brand (marque du produit)
                    #     status,  # Status (calculé selon votre logique)
                    #     product.name or '',  # Product Name
                    #     getattr(product, 'x_cpu', '') or '',  # CPU
                    #     getattr(product, 'x_ram', '') or '',  # RAM
                    #     getattr(product, 'x_storage', '') or '',  # Storage
                    #     getattr(product, 'x_gpu', '') or '',  # GPU
                    #     getattr(product, 'x_screen_size', '') or '',  # Screen Size
                    #     getattr(product, 'x_resolution', '') or '',  # Resolution
                    #     'Yes' if getattr(product, 'x_touchscreen', False) else '',  # Touchscreen
                    #     getattr(product, 'x_os', '') or '',  # OS
                    #     self._get_selection_label(product, 'x_grade'),  # Grade
                    #     getattr(product, 'x_battery', '') or '',  # Battery
                    #     getattr(product, 'x_warranty', '') or '',  # Warranty
                    #     qty_available,  # QTY (quantité de ce produit)
                    #     price_ex_vat,  # Price Ex VAT (récupéré depuis sales price/list_price)
                    #     getattr(product, 'x_promo_price', 0.0) or 0.0,  # Promo Price
                    # ]

                    data = [
                        product.default_code or '',  # SKU
                        getattr(product, 'x_brand', '') or '',  # Brand (marque du produit)
                        status,  # Status (calculé selon votre logique)
                        product.name or '',  # Product Name
                        product.x_CPU,  # CPU
                        product.x_ram,  # RAM
                        '',  # Storage
                        product.x_GPU,  # GPU
                        product.x_sreen_size,  # Screen Size
                        '',  # Resolution
                        '',  # Touchscreen
                        '',  # OS
                        '',  # Grade
                        '',  # Battery
                        product.x_warranty,  # Warranty
                        qty_available,  # QTY (quantité de ce produit)
                        price_ex_vat,  # Price Ex VAT (récupéré depuis sales price/list_price)
                        getattr(product, 'x_promo_price', 0.0) or 0.0,  # Promo Price
                    ]
                    
                    # Write data to worksheet
                    for col, value in enumerate(data):
                        if col == 2:  # Status column avec couleurs selon votre logique
                            if status_color == 'red':
                                worksheet.write(row, col, value, status_in_stock_format)
                            elif status_color == 'yellow':
                                worksheet.write(row, col, value, status_ship_format)
                            else:
                                worksheet.write(row, col, value, status_out_of_stock_format)
                        elif col in [15, 16, 17]:  # Quantity and price columns
                            worksheet.write(row, col, value, number_format)
                        else:
                            worksheet.write(row, col, value, cell_format)
                    
                    row += 1
                
                # Auto-adjust column widths
                column_widths = [15, 12, 15, 35, 15, 10, 15, 15, 12, 15, 12, 15, 12, 15, 15, 10, 15, 15]
                for col in range(len(headers)):
                    if col < len(column_widths):
                        worksheet.set_column(col, col, column_widths[col])
            
            # If no worksheets were created, create a default one
            if len(workbook.worksheets()) == 0:
                worksheet = workbook.add_worksheet('No Products Found')
                worksheet.write(0, 0, 'No products found for selected categories.', header_format)
            
            workbook.close()
            output.seek(0)
            
            # Create attachment
            file_data = base64.b64encode(output.read())
            timestamp = fields.Datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'products_export_{timestamp}.xlsx'
            
            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'type': 'binary',
                'datas': file_data,
                'res_model': self._name,
                'res_id': self.id,
                'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            })
            
           
        # Téléchargement direct du fichier
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}/{filename}?download=true',
                'target': 'self',
                'close': True,
            }
            
        except Exception as e:
            _logger.error(f"Error in product export: {str(e)}")
            raise UserError(f"Export failed: {str(e)}")
    
    def _get_selection_label(self, record, field_name):
        """Get selection field label"""
        try:
            if hasattr(record, field_name):
                field_value = getattr(record, field_name)
                if field_value and hasattr(record._fields[field_name], 'selection'):
                    selection_dict = dict(record._fields[field_name].selection)
                    return selection_dict.get(field_value, field_value)
            return ''
        except:
            return ''