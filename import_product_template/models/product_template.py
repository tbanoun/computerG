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
            product_id = rec.get('id', None)
            if not product_id: continue
            created = False
            try:
                product_template = self.env.ref(product_id)
            except Exception as e:
                print(f'error! {e}')
                error += 1
                # create the product
                created = True
                product_template = self.create_product_template(rec)
            if not created: update_index += 1
            attributes = rec.pop('attributes', None)
            vendors = rec.pop('vendors', None)
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
            # currency_id = selectOneElementDataBase(self, rec.get('currency_id', ''))
            # currency_id = currency_id.id if currency_id else None
            product_name = rec.get('product_name', '')
            product_code = rec.get('product_code', '')
            vendor_price = convertStrTofloat(rec.get('price', 0.0))
            vendor_qty = convertStrTofloat(rec.get('qty', 0.0))
            date_start = rec.get('start_date', None)
            date_end = rec.get('end_date', None)
            time_lead = convertStrTofloat(rec.get('time_lead', 0))
            # taxes_ids = selectElementDataBase(self, rec.get('taxes_ids', 0))
            self.env['product.supplierinfo'].create({
                'product_id': product_id,
                'partner_id': partner_id,
                'price': vendor_price,
                'delay': time_lead,
                'product_name': product_name,
                'product_code': product_code,
                'date_start': date_start if isinstance(date_start, datetime) else False,
                'date_end': date_end if isinstance(date_end, datetime) else False,
                'min_qty': vendor_qty,
                'product_tmpl_id': product_template.id,
                # 'currency_id': currency_id,
                # 'supplier_taxes_id': [(6, 0, taxes_ids)],
            })

    def update_product_template(self, product_id, vals):
        product_vals = generateProductVals(self, vals)
        qty = product_vals.pop('quantity', 0)

        product_id.sudo().write(
            product_vals
        )
        # delete qty
        stock_ids = self.env['stock.quant'].sudo().search(
            [
                (
                    'product_id', '=', product_id.id
                )
            ]
        )
        if stock_ids: stock_ids.sudo().unlink()
        location_id = self.env['stock.location'].sudo().search(
            [
                (
                    'usage', '=', 'internal'
                )
            ], limit=1
        )
        if location_id:
            stock_id = self.env['stock.quant'].sudo().create({
                "location_id": location_id.id,
                "product_id": product_id.product_variant_id.id,
                "product_tmpl_id": product_id.id,
                "inventory_quantity": qty
            })
        stock_id.sudo().action_apply_inventory()

    def create_product_template(self, vals):
        product_vals = generateProductVals(self, vals)
        product_vals['detailed_type'] = 'product'
        qty = product_vals.pop('quantity', 0)
        product_id = self.env['product.template'].sudo().create(
            product_vals
        )
        # self.updateQtyStockProduct(product_id, qty)

        return product_id

    def updateQtyStockProduct(self, product_id, availableQuantity):
        """ function to update qty product on supplier wherehouse """
        default_product_id = self.env.context.get('default_product_id', len(product_id.product_variant_ids) == 1 and product_id.product_variant_id.id)
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
        print(f'The stock {stock_id} has ok')
        stock_id.sudo().action_apply_inventory()
        return True
