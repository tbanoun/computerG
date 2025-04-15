from odoo import fields, models, api, _
import logging
from odoo.exceptions import ValidationError
import base64
import pandas as pd
import io
from datetime import datetime

_logger = logging.getLogger(__name__)

def cleanSentence(name):
    result = str(name).replace('.0', '')
    return result

def convertXlsOrCsvToDicts(file):
    fichier_decoded = base64.b64decode(file)
    fichier_io = io.BytesIO(fichier_decoded)

    try:
        df = pd.read_excel(fichier_io)
    except Exception:
        try:
            fichier_io.seek(0)
            df = pd.read_csv(fichier_io, sep=',')
        except Exception as e:
            raise ValueError(f"Impossible de lire le fichier fourni : {str(e)}")

    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.columns = [str(col).strip() for col in df.columns]
    df.fillna(method='ffill', inplace=True)
    df = df.fillna('')

    produits = {}

    for _, row in df.iterrows():
        product_id = row['id']
        if product_id not in produits:
            produit_data = {k: row[k] for k in df.columns if k not in [
                'attribute', 'value', 'price',
                'attribute_line_ids/product_template_value_ids/id',
                'Vendors/Vendor', 'Vendors/Vendor Product Name', 'Vendors/Vendor Product Code',
                'Vendors/Price', 'Vendors/Quantity', 'Vendors/Start Date',
                'Vendors/End Date', 'Vendors/Delivery Lead Time'
            ]}
            produit_data['attributes'] = {}
            produit_data['vendors'] = []
            produits[product_id] = produit_data

        # Gestion des attributs
        attr_name = str(row.get('attribute', '')).strip()
        attr_value = str(row.get('value', '')).strip()
        attr_price = row.get('price', 0.0)

        if attr_name and attr_value:
            if attr_name not in produits[product_id]['attributes']:
                produits[product_id]['attributes'][attr_name] = []

            produits[product_id]['attributes'][attr_name].append({
                'value': attr_value,
                'price': float(attr_price)
            })

        # Gestion des vendors
        vendor_name = str(row.get('Vendors/Vendor', '')).strip()
        if vendor_name:
            vendor_info = {
                'vendor_name': vendor_name,
                'product_name': str(row.get('Vendors/Vendor Product Name', '')).strip(),
                'product_code': str(row.get('Vendors/Vendor Product Code', '')).strip(),
                'price': float(row.get('Vendors/Price', 0.0)),
                'qty': int(row.get('Vendors/Quantity', 0)),
                'start_date': parse_date(row.get('Vendors/Start Date', '')),
                'end_date': parse_date(row.get('Vendors/End Date', '')),
                'time_lead': int(row.get('Vendors/Delivery Lead Time', 0))
            }
            produits[product_id]['vendors'].append(vendor_info)

    # Réorganiser les attributs dans le format demandé
    for produit in produits.values():
        formatted_attributes = []
        for attr_name, values in produit['attributes'].items():
            formatted_attributes.append({
                'attribute': {
                    'name': attr_name,
                    'value': values
                }
            })
        produit['attributes'] = formatted_attributes

    return list(produits.values())

def parse_date(value):
    """Essaye de parser la date au format datetime.date ou retourne une string vide."""
    if isinstance(value, datetime):
        return value.date().isoformat()
    try:
        return pd.to_datetime(value, dayfirst=True).date().isoformat()
    except Exception:
        return ''

def select_detailed_type(self, name):
    if 'Consumable':
        return 'consu'
    elif 'Service':
        return 'service'
    else:
        return 'product'

def select_tracking_type(self, name):
    if 'By Unique Serial Number':
        return 'serial'
    elif 'By Lots':
        return 'lot'
    else:
        return 'none'

def select_categoryId(self, categ_id):
    try:
        categ_id = self.env.ref(categ_id)
    except Exception as e:
        return None
    return categ_id.id

def select_categoryIds(self, categ_ids):
    result = []
    for categ_id in categ_ids:
        try:
            categ_id = self.env.ref(categ_id)
            if not categ_id: continue
            result.append(categ_id.id)
        except Exception as e:
            continue
    return result


def selectElementDataBase(self, item_ids):
    result = []
    for item_id in item_ids:
        try:
            item = self.env.ref(item_id)
            result.append(item_id.id)
        except Exception as e:
            continue
    return result

def selectOneElementDataBase(self, item_id):
    res = None
    try:
        res = self.env.ref(item_id)
    except Exception as e:
        return None
    return res

def generateProductVals(self, vals):
    # seller_ids / currency_id / id

    product_vals = {}
    product_vals = {
        'name': vals.get('name', ''),
        'standard_price': vals.get('standard_price', 0),
        'list_price': vals.get('Sales Price', 0),
        'default_code': cleanSentence(vals.get('default_code', '')),
        'barcode': cleanSentence(vals.get('barcode', '')),
        'x_product_website_url': vals.get('x_product_website_url', ''),
        'x_condition': vals.get('x_condition', ''),
        'x_': vals.get('x_', ''),
        'x_kind': vals.get('x_kind', ''),
        'image_url': vals.get('image_url', ''),
        'description_sale': vals.get('description_sale', ''),
        'available_in_pos': vals.get('available_in_pos', False),
        'out_of_stock_message': vals.get('out_of_stock_message', ''),
        'allow_out_of_stock_order': vals.get('allow_out_of_stock_order', False),
        'showDelivryMessage': vals.get('showDelivryMessage', False),
        'messageDelivryTimeRemoteStock': vals.get('showDelivryMessage', ''),
        'seo_name': vals.get('seo_name', ''),
        'website_meta_title': vals.get('website_meta_title', ''),
        'website_meta_keywords': vals.get('website_meta_keywords', ''),
        'website_description': vals.get('website_description', ''),
        'weight': vals.get('weight', ''),
        'tracking': select_tracking_type(self, vals.get('tracking', '')),
        'categ_id': select_categoryId(self, vals.get('categ_id/id', None)),
        'pos_categ_id': select_categoryId(self, vals.get('pos_categ_id/id', None)),
        'public_categ_ids': [(6, 0, select_categoryIds(self, vals.get('public_categ_ids/id', None)))],
        'dr_product_offer_ids': [(6, 0, selectElementDataBase(self, vals.get('dr_product_offer_ids/id', None)))],
        'dr_product_offer_ids': [(6, 0, selectElementDataBase(self, vals.get('dr_product_offer_ids/id', None)))],
        'dr_product_tab_ids': [(6, 0, selectElementDataBase(self, vals.get('dr_product_tab_ids/id', None)))],
        'supplier_taxes_id': [(6, 0, selectOneElementDataBase(self, vals.get('supplier_taxes_id', None)))],
    }
    return product_vals

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
        return None
        # delete attributes product
        # product_template.sudo().seller_ids.unlink()
        # for rec in vendors:
        #     partner_id = selectPartnerId(rec.get('attribute', None))
        #     if not attribute: continue
        #     attribute_name = attribute.get('name', None)
        #     # search attribute if existe:
        #     attribute_databse_id = self.env['product.attribute'].sudo().search([('name', 'ilike', attribute_name)],
        #                                                                        limit=1)
        #     if not attribute_databse_id:
        #         attribute_databse_id = self.env['product.attribute'].create(
        #             {
        #                 "name": attribute_name
        #             }
        #         )
        #     # lop values:
        #     values = attribute.get('value', None)
        #     value_ids = []
        #     for val in values:
        #         value = self.env['product.attribute.value'].sudo().search(
        #             [('name', '=', val.get('value', '')), ('attribute_id', '=', attribute_databse_id.id)], limit=1)
        #         if not value:
        #             value = self.env['product.attribute.value'].create({
        #                 'name': val.get('value', ''),
        #                 'attribute_id': attribute_databse_id.id
        #             })
        #         value_ids.append(value.id)
        #         # # #
        #     vals = {
        #         "attribute_id": attribute_databse_id.id,
        #         "product_tmpl_id": product_template.id,
        #         "value_ids": value_ids
        #     }
        #     attribute_line_ids = self.env['product.template.attribute.line'].sudo().create(
        #         vals
        #     )
        #     config_lines = self.env['product.template.attribute.value'].sudo().search([
        #         ('id', 'in', attribute_line_ids.product_template_value_ids.ids)
        #     ])
        #     # update price
        #     for line in config_lines:
        #         price = 0
        #         for val in values:
        #             if val.get('value') == line.name:
        #                 price = val.get('price')
        #                 break
        #         line.sudo().write(
        #             {
        #                 'price_extra': price
        #             }
        #         )

    def update_product_template(self, product_id, vals):
        product_vals = generateProductVals(self, vals)
        product_id.sudo().write(
            product_vals
        )

    def create_product_template(self, vals):
        product_vals = generateProductVals(self, vals)
        product_vals['detailed_type'] = 'product'
        product_id = self.env['product.template'].sudo().create(
            product_vals
        )
        return product_id
