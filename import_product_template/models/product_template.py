import datetime

from reportlab.lib.pagesizes import elevenSeventeen

from odoo import fields, models, api, _
import logging
from odoo.exceptions import ValidationError
from .common import *

_logger = logging.getLogger(__name__)


class ImportProduct(models.TransientModel):
    _name = 'base.import.product.wizard'
    _description = "Import product using template xlsx"

    file_xls = fields.Binary()
    file_name = fields.Char(string="File name")

    @api.constrains('file_name')
    def _check_file_extension(self):
        for record in self:
            if record.file_name:
                if not (record.file_name.lower().endswith('.xlsx') or record.file_name.lower().endswith('.csv')):
                    raise ValidationError("Le fichier doit être au format .csv ou .xlsx")

    def importProductLigne(self):
        # get dict data (convert file csv or xlsx to dict)
        result = convertXlsOrCsvToDicts(self.file_xls)
        if not result: return False
        update_index = 0
        error = 0
        for rec in result:
            product_id = rec.get('ID', None)
            if not product_id: continue
            created = False
            print(f'\n\n rec ==> {rec} \n\n')
            try:
                product_template = self.env.ref(product_id)
            except Exception as e:
                error += 1
                # create the product
                created = True
                product_template = self.create_product_template(rec)
            if not created: update_index += 1
            attributes = rec.pop('Attributes', None)
            vendors = rec.pop('Vendor', None)
            print(f'\n\n\n attributes: {attributes}')
            if attributes: self.update_attributes(product_template, attributes)
            if vendors: self.update_list_vendors(product_template, vendors)
            self.update_product_template(product_template, rec)

        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Succès'),
                'type': 'info',
                'message': f"{update_index} products have been updated, and {error} products have been created!",
                'sticky': True,
            }
        }
        return notification

    def update_attributes(self, product_template, attributes):
        # delete attributes product
        product_template.sudo().attribute_line_ids.unlink()
        for rec in attributes:
            attribute = rec.get('attribute', None)
            if not attribute: continue
            attribute_name = attribute.get('name', None)
            # search attribute if existe:
            attribute_databse_id = self.env['product.attribute'].sudo().search([('name', 'ilike', attribute_name)],
                                                                               limit=1)
            if not attribute_databse_id:
                attribute_databse_id = self.env['product.attribute'].create(
                    {
                        "name": attribute_name
                    }
                )
            # lop values:
            values = attribute.get('value', None)
            value_ids = []
            for val in values:
                value = self.env['product.attribute.value'].sudo().search(
                    [('name', '=', val.get('value', '')), ('attribute_id', '=', attribute_databse_id.id)], limit=1)
                if not value:
                    value = self.env['product.attribute.value'].create({
                        'name': val.get('value', ''),
                        'attribute_id': attribute_databse_id.id
                    })
                value_ids.append(value.id)
                # # #
            vals = {
                "attribute_id": attribute_databse_id.id,
                "product_tmpl_id": product_template.id,
                "value_ids": value_ids
            }
            attribute_line_ids = self.env['product.template.attribute.line'].sudo().create(
                vals
            )
            config_lines = self.env['product.template.attribute.value'].sudo().search([
                ('id', 'in', attribute_line_ids.product_template_value_ids.ids)
            ])
            # update price
            for line in config_lines:
                price = 0
                for val in values:
                    if val.get('value') == line.name:
                        price = val.get('price')
                        break
                line.sudo().write(
                    {
                        'price_extra': price
                    }
                )

    def update_list_vendors(self, product_template, vendors):
        # delete seller_ids line on product
        product_template.sudo().seller_ids.unlink()
        for rec in vendors:
            # select partner_id
            partner_id = selectOneElementDataBase(self, rec.get('vendor_id', None))
            if not partner_id: continue
            partner_id = partner_id.id
            # select product_id
            product_id = selectOneElementDataBase(self, rec.get('product_id', None))
            if product_id:
                product_id = product_id.id
            else:
                product_id = None
            currency_id = selectOneElementDataBase(self, rec.get('currency_id', ''))
            currency_id = currency_id.id if currency_id else None
            product_name = rec.get('product_name', '')
            product_code = rec.get('product_code', '')
            vendor_price = convertStrTofloat(rec.get('price', 0.0))
            vendor_qty = convertStrTofloat(rec.get('qty', 0.0))
            date_start = rec.get('date_start', None)
            date_end = rec.get('date_end', None)
            time_lead = convertStrTofloat(rec.get('time_lead', 0))
            vals = {
                'product_id': product_id,
                'partner_id': partner_id,
                'price': vendor_price,
                'delay': time_lead,
                'product_name': product_name,
                'product_code': product_code,
                'date_start': date_start,
                'date_end': date_end,
                'min_qty': vendor_qty,
                'product_tmpl_id': product_template.id,
            }
            if currency_id:
                vals['currency_id'] = currency_id
            self.env['product.supplierinfo'].create(
                vals
            )

    def update_product_template(self, product_id, vals):
        product_vals = generateProductVals(self, vals)
        # manufacturer_id
        manufacturer_id = product_vals.pop('manufacturer_id', 0)
        # dr_label_id
        dr_label_id = product_vals.pop('dr_label_id', None)
        try:
            dr_label_id = selectOneElementDataBase(self, dr_label_id)
            if dr_label_id:
                product_vals['dr_label_id'] = dr_label_id
        except Exception:
            pass


        product_vals['manufacturer_id_int'] = manufacturer_id

        product_id.sudo().write(
            product_vals
        )

    def create_product_template(self, vals):
        product_vals = generateProductVals(self, vals)

        product_vals['detailed_type'] = 'product'
        # dr_label_id
        # dr_label_id
        dr_label_id = product_vals.pop('dr_label_id', None)
        if dr_label_id: dr_label_id = selectOneElementDataBase(self, dr_label_id)
        if dr_label_id:
            product_vals['dr_label_id'] = dr_label_id

        product_id = self.env['product.template'].sudo().create(
            product_vals
        )
        return product_id

    def updateQtyStockProduct(self, product_id, availableQuantity):
        """ function to update qty product on supplier wherehouse """
        default_product_id = self.env.context.get('default_product_id',
                                                  len(product_id.product_variant_ids) == 1 and product_id.product_variant_id.id)
        location_id = self.env['stock.location'].sudo().search(
            [
                (
                    'usage', 'in', ['internal', 'transit']
                )
            ], limit=1
        )
        stock_id = self.env['stock.quant'].sudo().create({
            "location_id": product_id.stockQuant.id,
            "product_id": default_product_id,
            "inventory_quantity": availableQuantity,
            "quantity": availableQuantity
        })
        stock_id.sudo().action_apply_inventory()
        return True


class TestProductQty(models.Model):
    _inherit = "product.template"

    manufacturer_id_int = fields.Integer(string='Manufacturer')

    def updateQtyStockProduct(self):
        """ function to update qty product on supplier wherehouse """
        default_product_id = self.env.context.get('default_product_id',
                                                  len(self.product_variant_ids) == 1 and self.product_variant_id.id)
        location_id = self.env['stock.location'].sudo().search(
            [
                (
                    'usage', 'in', ['internal', 'transit']
                )
            ], limit=1
        )
        stock_id = self.env['stock.quant'].sudo().create({
            "location_id": location_id.id,
            "product_id": self.product_variant_id.id,
            "inventory_quantity": 44,
            "quantity": 44,
        })
        stock_id.sudo().action_apply_inventory()
        return True
