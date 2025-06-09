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
    try:
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
    except Exception as e:
        return result


def sewertKuCheckAvalableProductOnData(dataframes, product):
    result = {
        'is_published': False,
        'qty': 0,
        'price': 0
    }
    try:
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
    except Exception as e:
        return result

def googleCheckAvalableProductOnData(dataframes, product):
    result = {
        'is_published': False,
        'qty': 0,
        'price': 0
    }
    try:
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
    except Exception as e:
        return  result


class ResConfigCronJobCsv(models.Model):
    _name = 'cronjob.csv.settings'
    _description = 'Configuration pour le cron de mise à jour CSV'

    # stock_id = fields.Many2one("stock.location")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    stock_supplier_id = fields.Many2one("stock.location",
                                        config_parameter='config_supplier_csv_cronjob.stock_supplier_id')

    reset_quantity_supplier = fields.Boolean(config_parameter='config_supplier_csv_cronjob.reset_quantity_supplier', default=False)

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
                sewertKu_data = sewertKu_data[
                    sewertKu_data['Category1'].isin(selectCategoryName) & sewertKu_data['EAN'].notna() & (
                            sewertKu_data['EAN'] != "")]
        except Exception as e:
            print(e)
        return sewertKu_data

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
        self.env['ir.config_parameter'].sudo().set_param(
            'config_supplier_csv_cronjob.reset_quantity_supplier', '1'
        )
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
            # google_vals = googleCheckAvalableProductOnData(dataframes_google_data, product)
            # kosatec_vals = kosatecCheckAvalableProductOnData(dataframes_kosatec_data, product)
            # siewert_vals = sewertKuCheckAvalableProductOnData(dataframes_siewert_ku_data, product)
            # qty = google_vals.get('qty', 0) + kosatec_vals.get('qty', 0) + siewert_vals.get('qty', 0)
            # qty = extract_value(google_vals.get('qty')) + extract_value(kosatec_vals.get('qty')) + extract_value(
            #     siewert_vals.get('qty'))
            # if qty <= 0:
            product.sudo().is_published = False
            # else:
            #     product.sudo().is_published = False
            product.sudo().standard_price = 0
            self.updateQtyStockProduct(product, 0)
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Succès'),
                'type': 'info',
                'message': f"The operation was successful!",
                'sticky': False,
            }
        }
        return notification


    def updateMessageDelivery(self):
        products = self.env['product.template'].sudo().search([

        ])
        for product in products:
            try:
                product.write(
                    {
                        'out_of_stock_message': '3 Weeks Delivery',
                        # 'show_availability': True,
                        # 'showDelivryMessage': True,
                        'messageDelivryTimeRemoteStock': 'Ship in 2-3 Days',
                        'messageDelivryTimeStock': 'Ship in 1-2 Days',

                    }
                )
            except Exception as e:
                continue
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Succès'),
                'type': 'info',
                'message': f"The operation was successful!",
                'sticky': False,
            }
        }
        return notification