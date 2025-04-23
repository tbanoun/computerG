import datetime
import logging
import csv
import io
import base64
from datetime import datetime
from odoo import models, fields, api
from .common import *
_logger = logging.getLogger(__name__)


class ProductTemplateExport(models.Model):
    _inherit = "product.template"


    def exportData(self):
        # Create a file-like object in memory
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)

        # Write header row based on your example
        headers = [
            "Is Published", "ID", "Name", "Product Type", "Cost", "Sales Price",
            "Inventory Categ", "SKU", "Barcode", "Website URL Bz", "CPU Bz",
            "Sreen Size Bz", "Hard Drive Type Bz", "RAM Bz", "GPU Bz", "Manufacturer Bz", "Kind Bz",
            "Condition Bz", "Rubric Bz", "Image URL", "Website Categ", "Available in POS T/F",
            "POS Categ", "Out of Stock T/F", "Show Avil Qty T/F", "Out of Stock Message", "Dis/Hide Dliv Mes T/F",
            "Stock Message", "Remote Stock Message", "Sale Description", "SEO Name",
            "Meta Keywords", "Meta Description", "Meta Title", "Label", "Tabs",
            "Offers", "Quantity On Hand", "Website Description html", "Weight", "Tracking", "Vendor Taxes",
            "Vendor", "Vendor Product Name", "Vendor Product Code", "Vendors/Price", "Vendors Currency", "Vendors/Quantity",
            "Vendors/Start Date", "Vendors/End Date", "Product Variant", "Delivery Lead Time",
           "Attributes", "Value", "Price",
        ]
        writer.writerow(headers)

        # Write data for each product
        all_result = []
        for product in self:
            product_xmld_id = generateExportId(product)
            print(f'\n\n\ {product_xmld_id} \n\n')
            category_xmld_id = generateExportId(product.categ_id)
            pos_categ_id = generateExportId(product.pos_categ_id)
            supplier_taxes_id = generateExportId(product.supplier_taxes_id)
            public_categ_ids = ''
            for rec in product.public_categ_ids:
                rec_xmld_id = generateExportId(rec)
                if not rec_xmld_id: continue
                public_categ_ids += f'{rec_xmld_id},'
            dr_label_id = generateExportId(product.dr_label_id)
            dr_product_tab_ids = ''
            for rec in product.dr_product_tab_ids:
                rec_xmld_id = generateExportId(rec)
                if not rec_xmld_id: continue
                dr_product_tab_ids += f'{rec_xmld_id},'
            dr_product_offer_ids = ''
            for rec in product.dr_product_offer_ids:
                rec_xmld_id = generateExportId(rec)
                if not rec_xmld_id: continue
                dr_product_offer_ids += f'{rec_xmld_id},'
            tracking = select_tracking_type_with_key(product.tracking)
            manufacturer_id = product.manufacturer_id_int if product.manufacturer_id_int else 0
            # manufacturer_id = 0
            # Get first seller ids

            # Prepare the row data
            result = []
            row = [
                product.is_published,  # Is Published
                product_xmld_id,  # extenal_id
                product.name,  # product name
                product.detailed_type,  # detailed_type
                product.standard_price,  # standard_price
                product.list_price,  # Sales Price
                category_xmld_id or '',  # categ_id/id
                product.default_code or "",  # default_code
                product.barcode or "",  # barcode
                product.x_product_website_url or "",  # x_product_website_url (empty in example)
                product.x_CPU or "",  # x_CPU (empty in example)
                product.x_sreen_size or "",  # x_sreen_size (empty in example)
                product.x_hddtype or "",  # x_hddtype (empty in example)
                product.x_ram or "",  # x_ram (empty in example)
                product.x_GPU or "",  # x_GPU (empty in example)
                manufacturer_id or "", # f"__export__.res_partner_{product.manufacturer.id}_{product.manufacturer.id}" if product.manufacturer else "",
                product.x_kind or "",  # x_kind (empty in example)
                product.x_condition or "",  # x_condition (empty in example)
                product.x_ or "",  # x_ (empty in example)
                product.image_url or "",  # image_url (you can add product.image_1920 URL here)
                public_categ_ids or '', # public_categ_ids/id
                product.available_in_pos or '', # available_in_pos
                pos_categ_id or '', # pos_categ_id/id
                product.allow_out_of_stock_order or False,  # allow_out_of_stock_order
                product.show_availability or False,  # show_availability
                product.out_of_stock_message or '',  # out_of_stock_message
                product.showDelivryMessage or False,  # showDelivryMessage
                product.messageDelivryTimeStock or '',  # messageDelivryTimeStock
                product.messageDelivryTimeRemoteStock or '',  # messageDelivryTimeRemoteStock
                product.description_sale or "",  # description_sale
                product.name.lower().replace(" ", "-") or '',  # seo_name (simple conversion)
                product.website_meta_keywords or '',  # website_meta_keywords
                product.description_sale or "",  # website_meta_description
                product.website_meta_title or '',  # website_meta_title
                dr_label_id or '',  # dr_label_id/id (empty in example)
                dr_product_tab_ids or '',  # dr_product_tab_ids
                dr_product_offer_ids or '',  # dr_product_offer_ids
                product.qty_available or 0,  # Quantity On Hand
                product.description or "",  # website_description
                product.weight or 0,  # weight
                tracking,  # tracking (as in example)
                supplier_taxes_id or '',

            ]
            print(f'\n Holla {row} \n')
            start = True
            # export saller ids
            if not product.seller_ids: result.append(row)
            for rec in product.seller_ids:
                vendor_xmld_id = generateExportId(rec.partner_id)
                if not vendor_xmld_id: continue
                currency_xmld_id = generateExportId(rec.currency_id)
                if not currency_xmld_id: currency_xmld_id = ''
                product_id_xmld_id = generateExportId(rec.product_id)
                if not product_id_xmld_id: product_id_xmld_id = ''
                if not start: row = generateNewRow()
                row.append(vendor_xmld_id)
                row.append(rec.product_name or '')
                row.append(rec.product_code or '')
                row.append(rec.price)
                row.append(currency_xmld_id)
                row.append(rec.min_qty)
                row.append(rec.date_start or '')
                row.append(rec.date_end or '')
                row.append(product_id_xmld_id)
                row.append(rec.delay)
                start = False
                result.append(row)


            # export attributes
            value_ids = []
            for rec in product.dr_ptav_ids:
                res = []
                res.append(rec.attribute_line_id.attribute_id.name) #attribute name
                res.append(rec.name) # value name
                res.append(rec.price_extra) #value price
                value_ids.append(res)

            #Concatiner les tableau
            for i in range(0, len(value_ids)):
                if (i < len(result)):
                    result[i] = result[i] + value_ids[i]
                else:
                    res = generateNewRowAttribute()
                    res = res + value_ids[i]
                    result.append(res)

            # result = result + value_ids
            all_result = all_result + result
        writer.writerows(all_result)

        # Prepare the file for download
        output.seek(0)
        file_data = output.getvalue().encode()
        output.close()

        # Create an attachment
        attachment = self.env['ir.attachment'].create({
            'name': f'product_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            'datas': base64.b64encode(file_data),
            'type': 'binary',
            'res_model': 'product.template',
            'mimetype': 'text/csv'
        })

        # Return download action
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }