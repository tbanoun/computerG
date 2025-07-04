import os
from odoo import models, fields, api 
from odoo.exceptions import UserError
from odoo.modules.module import get_module_path
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
        help='Select pricelist for pricing'
    )
    
    
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
    
    def _create_info_sheet(self, workbook, header_format, cell_format):
        """Create information sheet with company details"""
        info_sheet = workbook.add_worksheet('Summary-ComputerG')
        
       
        logo_format = workbook.add_format({
            'bold': True,
            'font_size': 18,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FFFFFF',
            'font_color': '#4472C4',
            'border': 1
        })
        
        description_format = workbook.add_format({
            'font_size': 11,
            'text_wrap': True,
            'valign': 'top',
            'border': 1,
            'bg_color': '#F8F9FA'
        })
        
    
        category_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'underline': True
        })
        
        notes_header_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'left',
            'valign': 'vcenter',
            'bg_color': '#E8F4FD',
            'border': 1
        })
        
        grade_label_format = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'text_wrap': True,
            'valign': 'top',
            'border': 1,
            'bg_color': '#F0F0F0'
        })
        
        grade_desc_format = workbook.add_format({
            'font_size': 10,
            'text_wrap': True,
            'valign': 'top',
            'border': 1
        })
        
        contact_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FFE699',
            'border': 1
        })
     
        try:
        
            module_path = get_module_path('custom_product_management')  
            if module_path:
                logo_path = os.path.join(module_path, 'static', 'description', 'computerg_logo.png')
                
                if os.path.exists(logo_path):
                 
                    info_sheet.insert_image('A1', logo_path, {
                        'x_scale': 1.0,  
                        'y_scale': 1.0, 
                        'x_offset': 10,  
                        'y_offset': 10, 
                    })
                    
                    info_sheet.set_row(0, 80)  
                    info_sheet.set_row(1, 20)  
                    
                    info_sheet.set_column('A:A', 25)  
                    info_sheet.set_column('B:B', 25)  
                   
                    _logger.info(f"Logo inserted successfully from: {logo_path}")
                else:
                    raise FileNotFoundError(f"Logo file not found at: {logo_path}")
            else:
                raise Exception("Module path not found")
            
        
            info_sheet.set_row(0, 60)  
          
        except Exception as e:
       
            _logger.warning(f"Logo not found, using text instead: {str(e)}")
            info_sheet.merge_range('A1:F1', 'ComputerG.', logo_format)
     
        description = ("At ComputerG, we are Cyprus's premier destination for laptop solutions. "
                      "Specializing in laptop parts, refurbished computers, and pioneering laptop "
                      "motherboard repair services, we bring unparalleled expertise and innovation "
                      "to the technology landscape.")
        info_sheet.merge_range('A3:F4', description, description_format)
        
      
        row = 6
        

        info_sheet.merge_range(row, 0, row, 5, 'Refurbished Notebook', category_format)
        row += 1
        
    
        info_sheet.merge_range(row, 0, row, 2, 'Pre Owned Macbooks', category_format)
        info_sheet.merge_range(row, 3, row, 5, 'PC Desktops', category_format)
        row += 1
        
 
        info_sheet.merge_range(row, 0, row, 2, 'Pre Owned PC Monitors', category_format)
        info_sheet.merge_range(row, 3, row, 5, 'Brand New PC Monitors', category_format)
        row += 1
        
    
        info_sheet.merge_range(row, 0, row, 2, 'All-in-ones', category_format)
        info_sheet.merge_range(row, 3, row, 5, 'Docking Stations', category_format)
        row += 1
        
    
        info_sheet.merge_range(row, 0, row, 5, 'PC & Monitor Bundles', category_format)
        row += 2
        
    
        info_sheet.merge_range(row, 0, row, 5, 'Notes', notes_header_format)
        row += 1
        
     
        info_sheet.merge_range(row, 0, row, 5, 'All Customizable - Ask for RAM & SSD Upgrade', contact_format)
        row += 2
        
  
        info_sheet.merge_range(row, 0, row, 5, 'Grading System:', grade_label_format)
        row += 1
  
        grading_info = [
            ('New Sealed:', 'Device has never been used and comes in original sealed factory salespack and covered with manufacturer warranty'),
            ('New Open Box:', 'Device is new and could have been used as a demo unit, comes with original open-box'),
            ('Grade A+:', 'Device is in like-new condition boxed in 3rd Party Box'),
            ('Grade A:', 'Device is in a very good condition with minimal wear and tear boxed in 3rd Party Box'),
            ('Grade A-:', 'Device is in mint condition with minor visible wear and tear'),
            ('Grade B:', 'Device is in a good working condition with medium visible wear and tear'),
            ('Grade C:', 'Device is in a good working condition but can have a visible dent, crack or missing part')
        ]
        
        for grade, description in grading_info:
            info_sheet.write(row, 0, grade, grade_label_format)
            info_sheet.merge_range(row, 1, row, 5, description, grade_desc_format)
            row += 1
        
   
        row += 1
        info_sheet.merge_range(row, 0, row, 5, 
            'Batteries & AC Adapters are all tested and covered with DOA (Dead on Arrival) Warranty Only!', 
            grade_desc_format)
        row += 1
        

        info_sheet.merge_range(row, 0, row, 5, 'Prices Don\'t Include VAT', grade_label_format)
        row += 2
        

        info_sheet.merge_range(row, 0, row, 5, 'Call 22 250 676 | Email: Sales@computerg.eu', contact_format)
        

        info_sheet.set_column('A:A', 20)
        info_sheet.set_column('B:B', 15)
        info_sheet.set_column('C:C', 15)
        info_sheet.set_column('D:D', 15)
        info_sheet.set_column('E:E', 15)
        info_sheet.set_column('F:F', 15)
        
    
        info_sheet.set_row(0, 25)  
        info_sheet.set_row(2, 40)  
        info_sheet.set_row(3, 40)  
        
    # def _get_product_status(self, product):
    #     """
    #     Get product status based on quantity logic:
    #     - Si forecasted > 0 : "In Stock" (case rouge)
    #     - Si forecasted = 0 et supplied > 1 : "Ship in 2-3 days" (case jaune)
    #     """
    #     # Récupérer les quantités forecasted et supplied pour le produit
    #     forecasted_qty = 0
    #     supplied_qty = 0
        
    #     for variant in product.product_variant_ids:
    #         # qty_available = quantité disponible (forecasted)
    #         forecasted_qty += variant.qty_available
    #         # virtual_available inclut les quantités à recevoir
    #         # On peut aussi utiliser incoming_qty pour les quantités en approvisionnement
    #         supplied_qty += getattr(variant, 'incoming_qty', 0)
        
    #     if forecasted_qty > 0:
    #         return 'In Stock', 'red'
    #     elif forecasted_qty == 0 and supplied_qty > 1:
    #         return 'Ship in 2-3 days', 'yellow'
    #     else:
    #         # Cas par défaut si aucune des conditions n'est remplie
    #         return 'Out of Stock', 'gray'
    def _get_product_status(self, product):
        """
        Get product status based on quantity logic:
        - Si forecasted > 0 : "In Stock" (case rouge)
        - Si forecasted = 0 et on supplier >= 1 : "Ship in 2-3 days" (case jaune)
        - Si forecasted = 0 : "Out of Stock" (case grise)
        """
     
        forecasted_qty = 0
        on_supplier_qty = 0
    
        for variant in product.product_variant_ids:
          
            forecasted_qty += variant.virtual_available
    
            on_supplier_qty += getattr(variant, 'incoming_qty', 0)
    
        if forecasted_qty > 0:
            return 'In Stock', 'red'
        elif forecasted_qty == 0 and on_supplier_qty >= 1:
            return 'Ship in 2-3 days', 'yellow'
        else:
       
            return 'Out of Stock', 'gray'
    
    def _get_product_attribute_value(self, product, attribute_name):
        """
        Récupère la valeur d'un attribut spécifique pour un produit
        Args:
            product: product.template record
            attribute_name: nom de l'attribut (ex: 'Resolution', 'Touchscreen', etc.)
        Returns:
            string: valeur de l'attribut ou chaîne vide si pas trouvé
        """
        try:
    
            attribute = self.env['product.attribute'].search([
                ('name', '=', attribute_name)
            ], limit=1)
            
            if not attribute:
        
                attribute = self.env['product.attribute'].search([
                    ('name', 'ilike', attribute_name)
                ], limit=1)
            
            if attribute:
       
                for variant in product.product_variant_ids:
                    for attribute_value in variant.product_template_attribute_value_ids:
                        if attribute_value.attribute_id.id == attribute.id:
                            return attribute_value.product_attribute_value_id.name
                
          
                for attribute_line in product.attribute_line_ids:
                    if attribute_line.attribute_id.id == attribute.id:
                   
                        if attribute_line.value_ids:
                            return attribute_line.value_ids[0].name
            
            return ''
            
        except Exception as e:
            _logger.warning(f"Error getting attribute {attribute_name} for product {product.name}: {str(e)}")
            return ''
    
    def _get_all_product_attributes(self, product):
        """
        Récupère tous les attributs d'un produit sous forme de dictionnaire
        Args:
            product: product.template record
        Returns:
            dict: dictionnaire avec nom_attribut: valeur
        """
        attributes_dict = {}
        
        try:
   
            for variant in product.product_variant_ids:
                for attribute_value in variant.product_template_attribute_value_ids:
                    attr_name = attribute_value.attribute_id.name
                    attr_value = attribute_value.product_attribute_value_id.name
                    attributes_dict[attr_name] = attr_value
            
        
            for attribute_line in product.attribute_line_ids:
                attr_name = attribute_line.attribute_id.name
                if attr_name not in attributes_dict and attribute_line.value_ids:
             
                    if len(attribute_line.value_ids) == 1:
                        attributes_dict[attr_name] = attribute_line.value_ids[0].name
                    else:
               
                        attributes_dict[attr_name] = ', '.join(attribute_line.value_ids.mapped('name'))
                        
        except Exception as e:
            _logger.warning(f"Error getting all attributes for product {product.name}: {str(e)}")
        
        return attributes_dict
    
    def _get_touchscreen_value(self, product):
        """
        Récupère la valeur Touchscreen et retourne Yes/No
        """
        touchscreen_value = self._get_product_attribute_value(product, 'Touchscreen')
        if touchscreen_value:
  
            if touchscreen_value.lower() in ['yes', 'oui', 'true', '1', 'touchscreen']:
                return 'Yes'
            elif touchscreen_value.lower() in ['no', 'non', 'false', '0', 'no touchscreen']:
                return 'No'
            else:
                return touchscreen_value
        return ''

    def action_export_excel(self):
        """Export products to Excel file"""
        try:
            if not self.pricelist_id:
                raise UserError('Please select a pricelist.')
            
            if not self.export_all_categories and not self.category_ids:
                raise UserError('Please select at least one category or check "Export All Categories".')
            

            output = BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            
    
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
            
     
            status_in_stock_format = workbook.add_format({
                'border': 1,
                'text_wrap': True,
                'valign': 'top',
                'bg_color': '#FF0000'  
            })
            
            status_ship_format = workbook.add_format({
                'border': 1,
                'text_wrap': True,
                'valign': 'top',
                'bg_color': '#FFFF00'  
            })
            
            status_out_of_stock_format = workbook.add_format({
                'border': 1,
                'text_wrap': True,
                'valign': 'top',
                'bg_color': '#CCCCCC'  
            })
            
            number_format = workbook.add_format({
                'border': 1,
                'num_format': '#,##0.00'
            })


            self._create_info_sheet(workbook, header_format, cell_format)


            headers = [
                'SKU', 'Brand', 'Status', 'Product Name', 'CPU', 'RAM', 
                'Storage', 'GPU', 'Screen Size', 'Resolution', 'Touchscreen', 
                'OS', 'Grade', 'Battery', 'Warranty', 'QTY', 'Price Ex VAT'
            ]
            

            if self.export_all_categories:
                categories = self.env['product.category'].search([])
            else:
                categories = self.category_ids
            

            if not categories:
                categories = self.env['product.category'].search([])
            

            for category in categories:
    
                domain = [
                    ('categ_id', '=', category.id),
                    ('active', '=', True)
                ]
                
                products = self.env['product.template'].search(domain)
                
             
                if not products:
                    continue
                
     
                sheet_name = category.name[:31]  # Excel sheet names are limited to 31 characters
                worksheet = workbook.add_worksheet(sheet_name)
                
          
                for col, header in enumerate(headers):
                    worksheet.write(0, col, header, header_format)
                
        
                row = 1
                for product in products:
                    # if not product.is_published: continue
                    # Get price from sales price (list_price) - selon vos spécifications
                    price_ex_vat = product.list_price or 0.0
                    
          
                    # try:
                    #     pricelist_price = self.pricelist_id._get_product_price(
                    #         product, 1.0, partner=False
                    #     )
                     
                    #     if pricelist_price != product.list_price:
                    #         price_ex_vat = pricelist_price
                    # except:
                    #     pass  
                    
                    

                     # Get forecasted quantity (QTY) - CORRECTION ICI
                    qty_forecasted = sum(product.product_variant_ids.mapped('virtual_available'))
                     
                 
                    status, status_color = self._get_product_status(product)
                    
            
                    product_attributes = self._get_all_product_attributes(product)
                
             
                    resolution = product_attributes.get('Resolution', '') or product_attributes.get('Screen Resolution', '')
                    touchscreen = self._get_touchscreen_value(product)
                    os_value = product_attributes.get('OS', '') or product_attributes.get('Operating System', '')
                    grade = product_attributes.get('Grade', '') or product_attributes.get('Condition', '')
                    battery = product_attributes.get('Battery', '') or product_attributes.get('Battery Life', '')
                
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
                        getattr(product, 'x_brand', '') or '',  # Brand 
                        status,  # Status 
                        product.name or '',  # Product Name
                        # product.x_CPU,  # CPU
                        '',
                        # product.x_ram,  # RAM
                         '',
                        '',  # Storage
                        # product.x_GPU,  # GPU
                         '',
                        # product.x_sreen_size,  # Screen Size
                         '',
                        # '',  # Resolution
                        # '',  # Touchscreen
                        # '',  # OS
                        # '',  # Grade
                        # '',  # Battery
                        resolution,  # Resolution depuis attributs
                        touchscreen,  # Touchscreen depuis attributs (Yes/No)
                        os_value,  # OS depuis attributs
                        grade,  # Grade depuis attributs
                        battery,  # Battery depuis attributs
                        # product.x_warranty,  # 
                        '',
                        qty_forecasted,  # QTY 
                        price_ex_vat,  # Price Ex VAT (récupéré depuis sales price/list_price)
                       
                    ]
                    
                  
                    for col, value in enumerate(data):
                        if col == 2:  
                            if status_color == 'red':
                                worksheet.write(row, col, value, status_in_stock_format)
                            elif status_color == 'yellow':
                                worksheet.write(row, col, value, status_ship_format)
                            else:
                                worksheet.write(row, col, value, status_out_of_stock_format)
                        elif col in [15, 16, 17]:  
                            worksheet.write(row, col, value, number_format)
                        else:
                            worksheet.write(row, col, value, cell_format)
                    
                    row += 1
                
             
                column_widths = [15, 12, 15, 35, 15, 10, 15, 15, 12, 15, 12, 15, 12, 15, 15, 10, 15, 15]
                for col in range(len(headers)):
                    if col < len(column_widths):
                        worksheet.set_column(col, col, column_widths[col])
            
       
            if len(workbook.worksheets()) == 0:
                worksheet = workbook.add_worksheet('No Products Found')
                worksheet.write(0, 0, 'No products found for selected categories.', header_format)
            
            workbook.close()
            output.seek(0)
            
      
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