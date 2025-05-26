from odoo import api, models, fields, _
import requests
from io import StringIO, BytesIO
import csv
import pandas as pd



GOOGLE_ID = 1
KOSATEC_ID = 1
SEWERT_KU_ID = 1

def extract_value(val):
    if isinstance(val, pd.Series):
        return val.iloc[0] if not val.empty else 0
    return val

def downloadCsvFile(url, ean='EAN'):
    res = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    res.raise_for_status()
    csv_data = StringIO(res.text)
    sep = detect_separator(csv_data)
    df = None
    try:
        df = pd.read_csv(csv_data, sep=sep, quotechar='"', on_bad_lines='warn', low_memory=False, dtype={ean: str})
    except Exception as e:
        print(f"Échec avec le séparateur '{sep}': {e}")
        df = pd.read_csv(csv_data, sep=sep, quotechar='"', on_bad_lines='warn', low_memory=False, dtype={ean: str})
    return df


def detect_separator(csv_file):
    csv_file.seek(0)
    sample = csv_file.read(1024)
    csv_file.seek(0)  # Revenir au début pour les lectures ultérieures
    dialect = csv.Sniffer().sniff(sample)
    return dialect.delimiter


def checkAvalableProductOnData(dataframes, product):
    for name, df in dataframes:
        # Vérifie si la colonne 'ean' ou 'EAN' ou similaire existe dans le DataFrame
        matching_cols = [col for col in df.columns if col.lower() == 'ean']

        if matching_cols:
            ean_col = matching_cols[0]
            matched_rows = df[df[ean_col].astype(str) == product.barcode]
            if not matched_rows.empty:
                print(f"\n✅ EAN trouvé dans {name} :\n{matched_rows}\n")
            else:
                print(f"\n❌ EAN non trouvé dans {name}.\n")
                return False, 0, 0
        else:
            print(f"\n⚠️ Colonne 'ean' non trouvée dans {name}.\n")
            return False, 0, 0


def kosatecCheckAvalableProductOnData(dataframes, product):
    result = {
        'is_published': False,
        'qty': 0,
        'price': 0
    }
    for name, df in dataframes:
        # Vérifie si la colonne 'ean' ou 'EAN' ou similaire existe dans le DataFrame
        matching_cols = [col for col in df.columns if col.lower() == 'ean']

        if matching_cols:
            ean_col = matching_cols[0]
            matched_rows = df[df[ean_col].astype(str) == product.barcode]
            if not matched_rows.empty:
                print(f"\n✅ EAN trouvé dans {name} :\n{matched_rows}\n")
                result['is_published'] = True
                result['qty'] = matched_rows.get('menge', 0)
                result['price'] = matched_rows.get('vkbrutto', 0)
                print(f"\n✅ EAN trouvé dans {name} :\n{matched_rows}\n")
                return result
            else:
                print(f"\n❌ EAN non trouvé dans {name}.\n")
                return result
        else:
            print(f"\n⚠️ Colonne 'ean' non trouvée dans {name}.\n")
            return result


def sewertKuCheckAvalableProductOnData(dataframes, product):
    result = {
        'is_published': False,
        'qty': 0,
        'price': 0
    }
    for name, df in dataframes:
        # Vérifie si la colonne 'ean' ou 'EAN' ou similaire existe dans le DataFrame
        matching_cols = [col for col in df.columns if col.lower() == 'ean']

        if matching_cols:
            ean_col = matching_cols[0]
            matched_rows = df[df[ean_col].astype(str) == product.barcode]
            if not matched_rows.empty:
                result['is_published'] = True
                result['qty'] = matched_rows.get('AvailableQuantity', 0)
                result['price'] = matched_rows.get('NetPrice', 0)
                print(f"\n✅ EAN trouvé dans {name} :\n{matched_rows}\n")
                return result
            else:
                print(f"\n❌ EAN non trouvé dans {name}.\n")
                return result
        else:
            print(f"\n⚠️ Colonne 'ean' non trouvée dans {name}.\n")
            return result


def googleCheckAvalableProductOnData(dataframes, product):
    result = {
        'is_published': False,
        'qty': 0,
        'price': 0
    }
    for name, df in dataframes:
        # Vérifie si la colonne 'ean' ou 'EAN' ou similaire existe dans le DataFrame
        matching_cols = [col for col in df.columns if col.lower() == 'ean']

        if matching_cols:
            ean_col = matching_cols[0]
            matched_rows = df[df[ean_col].astype(str) == product.barcode]
            if not matched_rows.empty:
                print(f"\n✅ EAN trouvé dans {name} :\n{matched_rows}\n")
                result['is_published'] = True
                result['qty'] = matched_rows['AvailableQuantity']
                result['price'] = matched_rows['NetPrice']
                print(f"\n✅ EAN trouvé dans {name} :\n{matched_rows}\n")
                return result
            else:
                print(f"\n❌ EAN non trouvé dans {name}.\n")
                return result
        else:
            print(f"\n⚠️ Colonne 'ean' non trouvée dans {name}.\n")
            return result

class ProductCategory(models.Model):
    _inherit = "product.category"

    categoryCode = fields.Char("Category code")



class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_available_wt = fields.Float(compute="claculateQtyWT")

    stockQuant = fields.Many2one('stock.location', compute='calculateSuplierWherhouse')

    def calculateSuplierWherhouse(self):
        stock_location_id = self.env['ir.config_parameter'].sudo().get_param(
            'config_supplier_csv_cronjob.stock_supplier_id')
        if stock_location_id:
            self.stockQuant = int(stock_location_id)
        else:
            self.stockQuant = stock_location_id
        return stock_location_id


    def unpublishedProduct(self):
        self.is_published = not self.is_published

    def action_view_inventory_supplier(self):
        """ Similar to _get_quants_action except specific for inventory adjustments (i.e. inventory counts). """
        if not self.stockQuant: return None
        action = {
            'name': _('Inventory Adjustments'),
            'view_mode': 'list',
            'view_id': self.env.ref(
                'config_supplier_csv_cronjob.view_stock_quant_tree_inventory_supplier_inherit_stock_account').id,
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



    def openKosatecFile(self):
        # open file kosatec
        kosatec_data = None
        try:
            kosatec_id = self.env['kosatec.product.import.csv'].sudo().browse(KOSATEC_ID)
            if kosatec_id.active:
                kosatec_data = downloadCsvFile(kosatec_id.csv_url, 'ean')
                selectCategoryName = kosatec_id.selectCategoryName()
                kosatec_data['kat2'] = kosatec_data['kat2'].str.lower()
                selectCategoryName = [cat.lower() for cat in selectCategoryName]
                kosatec_data = kosatec_data[
                    kosatec_data['kat2'].isin(selectCategoryName) & kosatec_data['ean'].notna() & (
                            kosatec_data['ean'] != "")]
        except Exception as e:
            print(e)
        return kosatec_data

    def openGoogleFile(self):
        # open file google
        google_data = None
        try:
            google_id = self.env['google.product.import.csv'].sudo().browse(GOOGLE_ID)
            if google_id.active:
                google_data = downloadCsvFile(google_id.csv_url, 'EAN')
                selectCategoryName = google_id.selectCategoryName()
                google_data['Category1'] = google_data['Category1'].str.lower()
                selectCategoryName = [cat.lower() for cat in selectCategoryName]
                google_data = google_data[
                    google_data['Category1'].isin(selectCategoryName) & google_data['EAN'].notna() & (
                            google_data['EAN'] != "")]
        except Exception as e:
            print(e)
        return google_data

    def opensiewertKuFile(self):
        # open file sewertKu
        sewertKu_data = None
        try:
            sewertKu_id = self.env['product.import.csv'].sudo().browse(SEWERT_KU_ID)
            if sewertKu_id.active:
                sewertKu_data = downloadCsvFile(sewertKu_id.csv_url, 'EAN')
                selectCategoryName = sewertKu_id.selectCategoryName()
                sewertKu_data['Category1'] = sewertKu_data['Category1'].str.lower()
                selectCategoryName = [cat.lower() for cat in selectCategoryName]
                google_data = sewertKu_data[
                    sewertKu_data['Category1'].isin(selectCategoryName) & sewertKu_data['EAN'].notna() & (
                            sewertKu_data['EAN'] != "")]
        except Exception as e:
            print(e)
        return google_data

    def updateQtyStockProduct(self, product_id, availableQuantity):
        """ function to update qty product on supplier wherehouse """

        stock_location_id = self.env['ir.config_parameter'].sudo().get_param(
            'config_supplier_csv_cronjob.stock_supplier_id')
        if not stock_location_id: return None
        stock_id = self.env['stock.quant'].sudo().search([
            ("location_id", "=", int(stock_location_id)),
            ("product_id", "=", product_id.product_variant_id.id),
        ], limit=1)
        if stock_id:
            stock_id.sudo().write({
                "inventory_quantity": availableQuantity,
                "quantity": availableQuantity
            })
            stock_id.sudo().action_apply_inventory()
        else:
            stock_id = self.env['stock.quant'].sudo().create({
                "location_id": int(stock_location_id),
                "product_id": product_id.product_variant_id.id,
                "inventory_quantity": availableQuantity,
                "quantity": availableQuantity
            })
            stock_id.sudo().action_apply_inventory()
        return True

    def resetProductInformation(self):
        products = self.env['product.template'].sudo().search([
            ('supplier_id', '!=', 'other')
        ])
        kosatec_data = self.openKosatecFile()
        google_data = self.openGoogleFile()
        siewert_ku_data = self.opensiewertKuFile()
        dataframes_google_data = [
            ('google_data', google_data),
        ]
        dataframes_kosatec_data = [
            ('kosatec_data', kosatec_data),
        ]
        dataframes_siewert_ku_data = [
            ('siewert_ku_data', siewert_ku_data)
        ]
        for product in products:
            google_vals = googleCheckAvalableProductOnData(dataframes_google_data, product)
            kosatec_vals = kosatecCheckAvalableProductOnData(dataframes_kosatec_data, product)
            siewert_vals = sewertKuCheckAvalableProductOnData(dataframes_siewert_ku_data, product)
            # qty = google_vals.get('qty', 0) + kosatec_vals.get('qty', 0) + siewert_vals.get('qty', 0)
            qty = extract_value(google_vals.get('qty')) + extract_value(kosatec_vals.get('qty')) + extract_value(
                siewert_vals.get('qty'))
            if qty <= 0:
                product.sudo().is_published = False
            else:
                product.sudo().is_published = True
            product.sudo().standard_price = 0
            self.updateQtyStockProduct(product, 0)
