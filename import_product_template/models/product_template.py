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
            if "end" != product_id.lower():
                created = False
                print(f'\n\n product_id ==> {product_id} \n\n')
                print(f'\n\n rec ==> {rec} \n\n')
                try:
                    product_template = self.env.ref(product_id)
                except Exception as e:
                    # create the product
                    created = True
                    product_template = self.create_product_template(rec)
                    if product_template:
                        print('TEST ME', product_template.name)
                        error += 1
                if not product_template: continue
                if not created: update_index += 1
                attributes = rec.pop('Attributes', None)
                vendors = rec.pop('Vendor', None)
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
        """
        Optimized: Update product attributes using only existing attributes in database.
        Handles case insensitivity, minimizes SQL calls, and improves speed.
        """
        try:
            ProductAttribute = self.env['product.attribute']
            ProductAttributeValue = self.env['product.attribute.value']
            # 1. Supprimer les lignes existantes en un seul appel
            product_template.attribute_line_ids.unlink()

            # 2. Préparation des données normalisées
            attr_name_map = {}
            attr_value_map = {}

            for rec in attributes:
                attr = rec.get("attribute")
                if not attr:
                    continue

                attr_name = attr.get("name", "").strip()
                if not attr_name:
                    continue

                norm_attr = attr_name.lower()
                if norm_attr not in attr_name_map:
                    attr_name_map[norm_attr] = attr_name

                for val in attr.get("value", []):
                    val_name = val.get("value", "").strip()
                    if not val_name:
                        continue
                    norm_val = val_name.lower()
                    attr_value_map.setdefault(norm_attr, {})[norm_val] = {
                        "name": val_name,
                        "price": float(val.get("price", 0))
                    }

            # 3. Recherche en batch des attributs existants seulement
            attr_objs = ProductAttribute.sudo().search([('name', 'in', list(attr_name_map.values()))])
            attr_dict = {a.name.lower(): a for a in attr_objs}

            print('________________________________________________')
            print('attr_name_map', attr_name_map.values())
            print('\n')
            print('attr_dict', attr_dict)
            print('\n')
            print('attr_objs', attr_objs)
            print('________________________________________________')


            # Ne pas créer de nouveaux attributs - utiliser seulement ceux qui existent
            # Supprimer les attributs non trouvés de nos maps
            attr_name_map = {k: v for k, v in attr_name_map.items() if k in attr_dict}
            attr_value_map = {k: v for k, v in attr_value_map.items() if k in attr_dict}

            # 4. Recherche en batch des valeurs existantes
            all_attr_ids = [attr.id for attr in attr_dict.values()]
            val_objs = ProductAttributeValue.sudo().search([
                ('attribute_id', 'in', all_attr_ids)
            ])
            val_dict = {}  # { (attr_id, norm_val_name): val }
            for v in val_objs:
                val_dict[(v.attribute_id.id, v.name.lower())] = v

            # 5. Création et regroupement des valeurs (seulement pour les attributs existants)
            line_data = []
            ptav_price_map = {}

            for norm_attr, values in attr_value_map.items():
                attr = attr_dict[norm_attr]
                value_ids = []

                for norm_val, val_info in values.items():
                    key = (attr.id, norm_val)
                    val_obj = val_dict.get(key)

                    if val_obj:  # Utiliser seulement les valeurs existantes
                        value_ids.append(val_obj.id)
                        ptav_price_map[val_obj.id] = val_info['price']

                if value_ids:  # Ne créer des lignes que si on a des valeurs
                    line_data.append((0, 0, {
                        'attribute_id': attr.id,
                        'value_ids': [(6, 0, value_ids)],
                    }))

            # 6. Création des lignes d'attributs groupées
            if line_data:
                product_template.write({
                    'attribute_line_ids': line_data
                })

            # 7. Mise à jour des prix des variantes
            for line in product_template.attribute_line_ids:
                for ptav in line.product_template_value_ids:
                    val_id = ptav.product_attribute_value_id.id
                    price = ptav_price_map.get(val_id)
                    if price is not None:
                        ptav.price_extra = price

            return True

        except Exception as e:
            _logger.exception("Error updating attributes")
            raise


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
            date_start = rec.get('start_date', None)
            date_end = rec.get('end_date', None)
            time_lead = convertStrTofloat(rec.get('time_lead', 0))
            vals = {
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
            }
            if currency_id:
                vals['currency_id'] = currency_id
            self.env['product.supplierinfo'].create(
                vals
            )

    def update_product_template(self, product_id, vals):
        product_vals = generateProductVals(self, vals)
        # manufacturer_id
        manufacturer_id = product_vals.pop('manufacturer_id_int', None)
        if manufacturer_id: manufacturer_id = selectOneElementDataBase(self, manufacturer_id)
        manufacturer_id = manufacturer_id if manufacturer_id else 0
        # dr_label_id
        dr_label_id = product_vals.pop('dr_label_id', None)
        if dr_label_id: dr_label_id = selectOneElementDataBase(self, dr_label_id)
        dr_label_id = dr_label_id.id if dr_label_id else None
        if manufacturer_id:
            product_vals['manufacturer_id_int'] = manufacturer_id
        if dr_label_id:
            product_vals['dr_label_id'] = dr_label_id

        product_id.sudo().write(
            product_vals
        )

    def create_product_template(self, vals):
        product_vals = generateProductVals(self, vals)
        product_vals['detailed_type'] = 'product'
        default_code = product_vals.get('default_code', None)
        barcode = product_vals.get('barcode', None)
        product_find = None
        if default_code and barcode:
            product_find = self.env['product.template'].sudo().search([
                '|',
                ('barcode', '=', barcode), ('default_code', '=', default_code)
            ])
        if product_find: return None
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
        print(f'The stock {stock_id} has ok')
        stock_id.sudo().action_apply_inventory()
        return True


class TestProductQty(models.Model):
    _inherit = "product.template"

    manufacturer_id_int = fields.Integer(string='Manufacturer')
    out_of_stock_message = fields.Char(string="Out-of-Stock Message")

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
