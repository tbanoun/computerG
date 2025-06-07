import time
from email.policy import default

from odoo import api, models, fields
from datetime import datetime
from datetime import date
import requests
import pandas as pd
from io import StringIO, BytesIO
import base64
import io
import logging
import math
from odoo.exceptions import UserError
import csv

_logger = logging.getLogger(__name__)


def convert_comma_decimal_to_float(value):
    """
    Convertit une chaîne avec virgule décimale en float
    Exemples:
        '138,04' → 138.04
        '1.234,56' → 1234.56 (gère aussi les séparateurs de milliers)
    """
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return 0.0

    # Nettoyage de la chaîne
    cleaned = value.strip().replace(' ', '')

    # Si vide, retourne 0
    if not cleaned:
        return 0.0

    # Remplace les séparateurs de milliers et la virgule décimale
    if '.' in cleaned and ',' in cleaned:
        # Format comme 1.234,56 → 1234.56
        cleaned = cleaned.replace('.', '').replace(',', '.')
    elif ',' in cleaned:
        # Format comme 138,04 → 138.04
        cleaned = cleaned.replace(',', '.')

    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def detect_separator(csv_file):
    csv_file.seek(0)
    sample = csv_file.read(1024)
    csv_file.seek(0)  # Revenir au début pour les lectures ultérieures
    dialect = csv.Sniffer().sniff(sample)
    return dialect.delimiter


class ImportProductConfig(models.Model):
    _name = "google.product.import.csv"
    _rec_name = "stock_id"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    csv_url = fields.Char()
    file_csv = fields.Binary()
    category_ids = fields.Many2many("product.category")
    stock_id = fields.Many2one("stock.location", compute='_camputeStockLocation')
    index = fields.Integer()
    max_products = fields.Integer()
    active = fields.Boolean(default=True)
    start_update = fields.Boolean(default=False)

    def _camputeStockLocation(self):
        stock_location_id = self.env['ir.config_parameter'].sudo().get_param(
            'config_supplier_csv_cronjob.stock_supplier_id')
        if stock_location_id:
            self.stock_id = int(stock_location_id)
        else:
            self.stock_id = stock_location_id
        return stock_location_id

    def downoladCsvFile(self):
        _logger.warning(f"\n\n CSV URL: {self.csv_url} \n\n")
        _logger.warning(f"\n\n CSV URL: {self.start_update} \n\n")

        if self.start_update:
            self.start_update = False
        if self.start_update is True:
            return

        try:
            res = requests.get(self.csv_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            res.raise_for_status()  # Lève une exception si code != 200
        except requests.exceptions.RequestException as e:
            _logger.error(f"Erreur lors du téléchargement du fichier CSV : {e}")
            raise UserError("Impossible de télécharger le fichier CSV. Vérifiez l'URL ou la connexion réseau.")

        _logger.warning(f"\n\n response: {res} \n\n")

        if res.status_code != 200:
            return

        csv_data = StringIO(res.text)
        sep = detect_separator(csv_data)
        print('Separateur', sep)
        try:
            df = pd.read_csv(csv_data, sep=sep, quotechar='"', on_bad_lines='warn', low_memory=False)
            # df = pd.read_csv('path/to/your/file.csv', sep=sep)
            print(df.head())  # Affiche les premières lignes pour vérifier
        except Exception as e:
            print(f"Échec avec le séparateur '{sep}': {e}")
            df = pd.read_csv(csv_data, sep=sep, quotechar='"', on_bad_lines='warn', low_memory=False)
        _logger.warning(f"\n\n Colonnes lues depuis le CSV: {df.columns.tolist()} \n\n")

        # Définition des catégories à conserver
        selectCategoryName = self.selectCategoryName()
        df['Category1'] = df['Category1'].str.lower()
        selectCategoryName = [cat.lower() for cat in selectCategoryName]
        # df = df[df['Category1'].isin(selectCategoryName)]
        df = df[df['Category1'].isin(selectCategoryName) & df['EAN'].notna() & (df['EAN'] != "")]

        # Sauvegarde le CSV en mémoire (binaire)
        buffer = BytesIO()
        df.to_csv(buffer, index=False, sep=';')
        csv_binary = buffer.getvalue()

        # Convertir en base64 si nécessaire pour Odoo
        csv_base64 = base64.b64encode(csv_binary).decode('utf-8')

        # Stocker dans le champ binaire (exemple avec Odoo)
        self.file_csv = csv_base64
        self.max_products = len(df)
        self.index = 0
        self.start_update = True

    def openViewImportProductHistory(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'google_sheet_update_product_csv_cronjob.action_open_history_action')
        action['res_id'] = 1
        action['target'] = 'current'
        return action

    def deleteHistoryFile(self):
        create_ids = self.env['google.history.create.action'].sudo().search([]).unlink()
        delete_ids = self.env['google.history.deleted.action'].sudo().search([]).unlink()
        update_ids = self.env['google.history.updated.action'].sudo().search([]).unlink()
        update_ids = self.env['google.history.published.action'].sudo().search([]).unlink()

    def resetIndex(self):
        self.index = 0

    def selectCategoryName(self):
        result = []
        for rec in self.category_ids:
            if not rec.categoryCode: continue
            categoryCodeSplit = rec.categoryCode.split(',')
            for category in categoryCodeSplit:
                category = category.strip()
                category = category.lower()
                if not category or category in result: continue
                result.append(category.lower())
        return result

    def actionCreateCsvFile(self, row, date_now):
        historyCreate = self.env['google.history.create.action'].search([
            ('date', "=", date_now)
        ], limit=1)
        if historyCreate:
            # update file csv
            file_decoded = base64.b64decode(historyCreate.file)
            file_io = io.BytesIO(file_decoded)
            df = pd.read_csv(file_io)
            condition = (df[list(row.keys())] == pd.Series(row)).all(axis=1)
            if condition.any():
                df.loc[condition, :] = row
            else:
                df.loc[len(df)] = row
            updated_csv = df.to_csv(index=False)
            updated_csv_encoded = base64.b64encode(updated_csv.encode('utf-8'))
            # Mettre à jour l'enregistrement avec le nouveau fichier
            historyCreate.write({
                'file': updated_csv_encoded,
            })
        else:
            df = pd.DataFrame([row])
            new_csv = df.to_csv(index=False)
            new_csv_encoded = base64.b64encode(new_csv.encode('utf-8'))
            self.env['google.history.create.action'].create({
                'file': new_csv_encoded,
                'file_name': f"File_create_{str(date_now).replace('-', '_')}.csv",
                'google_history_action_id': 1,
                'date': date_now

            })

    def actionDeleteCsvFile(self, row, date_now):
        historyCreate = self.env['google.history.deleted.action'].search([
            ('date', "=", date_now)
        ], limit=1)
        if historyCreate:
            # update file csv
            file_decoded = base64.b64decode(historyCreate.file)
            file_io = io.BytesIO(file_decoded)
            df = pd.read_csv(file_io)
            condition = (df[list(row.keys())] == pd.Series(row)).all(axis=1)
            if condition.any():
                df.loc[condition, :] = row
            else:
                df.loc[len(df)] = row
            updated_csv = df.to_csv(index=False)
            updated_csv_encoded = base64.b64encode(updated_csv.encode('utf-8'))
            # Mettre à jour l'enregistrement avec le nouveau fichier
            historyCreate.write({
                'file': updated_csv_encoded,
            })
        else:
            df = pd.DataFrame([row])
            new_csv = df.to_csv(index=False)
            new_csv_encoded = base64.b64encode(new_csv.encode('utf-8'))
            self.env['google.history.deleted.action'].create({
                'file': new_csv_encoded,
                'file_name': f"File_unpublished_{str(date_now).replace('-', '_')}.csv",
                'google_history_action_id': 1,
                'date': date_now

            })

    def actionUpdateCsvFile(self, row, date_now):
        historyCreate = self.env['google.history.updated.action'].search([
            ('date', "=", date_now)
        ], limit=1)
        if historyCreate:
            # update file csv
            file_decoded = base64.b64decode(historyCreate.file)
            file_io = io.BytesIO(file_decoded)
            df = pd.read_csv(file_io)
            condition = (df[list(row.keys())] == pd.Series(row)).all(axis=1)
            if condition.any():
                df.loc[condition, :] = row
            else:
                df.loc[len(df)] = row
            updated_csv = df.to_csv(index=False)
            updated_csv_encoded = base64.b64encode(updated_csv.encode('utf-8'))
            # Mettre à jour l'enregistrement avec le nouveau fichier
            historyCreate.write({
                'file': updated_csv_encoded,
            })
        else:
            df = pd.DataFrame([row])
            new_csv = df.to_csv(index=False)
            new_csv_encoded = base64.b64encode(new_csv.encode('utf-8'))
            self.env['google.history.updated.action'].create({
                'file': new_csv_encoded,
                'file_name': f"File_update_{str(date_now).replace('-', '_')}.csv",
                'google_history_action_id': 1,
                'date': date_now

            })

    def actionPublishedCsvFile(self, row, date_now):
        historyCreate = self.env['google.history.published.action'].search([
            ('date', "=", date_now)
        ], limit=1)
        if historyCreate:
            # update file csv
            file_decoded = base64.b64decode(historyCreate.file)
            file_io = io.BytesIO(file_decoded)
            df = pd.read_csv(file_io)
            condition = (df[list(row.keys())] == pd.Series(row)).all(axis=1)
            if condition.any():
                df.loc[condition, :] = row
            else:
                df.loc[len(df)] = row
            updated_csv = df.to_csv(index=False)
            updated_csv_encoded = base64.b64encode(updated_csv.encode('utf-8'))
            # Mettre à jour l'enregistrement avec le nouveau fichier
            historyCreate.write({
                'file': updated_csv_encoded,
            })
        else:
            df = pd.DataFrame([row])
            new_csv = df.to_csv(index=False)
            new_csv_encoded = base64.b64encode(new_csv.encode('utf-8'))
            self.env['google.history.published.action'].create({
                'file': new_csv_encoded,
                'file_name': f"File_published_{str(date_now).replace('-', '_')}.csv",
                'google_history_action_id': 1,
                'date': date_now

            })

    def createUpdateCsvFile(self, type, row):
        date_now = date.today()
        if type == "create":
            self.actionCreateCsvFile(row, date_now)
        elif type == "update":
            self.actionUpdateCsvFile(row, date_now)
        elif type == "delete":
            self.actionDeleteCsvFile(row, date_now)
        elif type == "published":
            self.actionPublishedCsvFile(row, date_now)

    def checkStartCron(self):
        datetime_now = datetime.now()
        if not (3 <= datetime_now.hour < 5): return False
        cron_id = self.env['google.product.import.csv'].sudo().browse(1)
        if not cron_id.active: return False
        time.sleep(2)
        cron_id.downoladCsvFile()
        time.sleep(2)
        cron_id.start_update = True

    def checkHourStartCron(self):
        datetime_now = datetime.now()
        if not (6 <= datetime_now.hour < 7): return False
        return True

    def startCronJob(self):
        datetime_now = datetime.now()
        if not (5 <= datetime_now.hour < 7): return False
        cron_id = self.env['google.product.import.csv'].sudo().browse(1)
        if not cron_id.active: return False
        cron_id.startScriptUsingButtonTest()

    def startScript(self, checkDate=None):
        if not checkDate:
            alpha = self.checkHourStartCron()
            if not alpha: return False
        if not self.file_csv: return
        selectCategory = self.selectCategoryName()
        # Décoder le fichier base64
        fichier_decoded = base64.b64decode(self.file_csv)
        # Charger dans un DataFrame pandas
        fichier_io = io.BytesIO(fichier_decoded)
        df = pd.read_csv(fichier_io, delimiter=',')

        df_filtered = df.loc[self.index:]
        # Parcourir les lignes avec iterrows()
        i = 0
        for index, row in df_filtered.iterrows():
            if index >= self.max_products:
                self.start_update = False
            i += 1
            print(index)
            print(len(df_filtered.iterrows()))
            if i >= 1000 or index == df_filtered.iterrows():
                self.index = index
                break
            manufacturerID = f"{row.get('EAN')}"
            print(f'\n\n manufacturerID : {manufacturerID}\n\n')
            manufacturerID = manufacturerID.replace(".0", "")
            if not manufacturerID: continue
            category = row.get('Category1')
            if not isinstance(category, str):
                continue
            if category.lower() not in selectCategory: continue
            availableQuantity = row.get('AvailableQuantity')
            AvailableNextQuantity = row.get('AvailableNextQuantity')
            if not isinstance(availableQuantity, int): continue
            availableQuantity += AvailableNextQuantity
            if availableQuantity > 0:
                # select product on table product.template
                product_id = self.env['product.template'].sudo().search([
                    ('barcode', '=', manufacturerID)
                ], limit=1)
                if not product_id:
                    # create new ligne on file csv create product
                    self.createUpdateCsvFile("create", row)
                    continue
                if product_id.is_published == False:
                    self.createUpdateCsvFile("published", row)
                self.createUpdateCsvFile("update", row)
                qtyStock = self.env['stock.quant'].sudo().search([
                    ("location_id", "=", self.stock_id.id),
                    ("product_id", "=", product_id.product_variant_id.id),
                ], limit=1)
                if not qtyStock:
                    qtyStock = self.env['stock.quant'].sudo().create({
                        "location_id": self.stock_id.id,
                        "product_id": product_id.product_variant_id.id,
                        "inventory_quantity": availableQuantity
                    })
                    qtyStock.sudo().action_apply_inventory()
                    continue
                qtyStock.sudo().write({
                    "inventory_quantity": availableQuantity
                })
                qtyStock.sudo().action_apply_inventory()
                product_id.standard_price = row.get('NetPrice')
                continue
            else:
                # delete and unpublish product
                product_id = self.env['product.template'].sudo().search([
                    ('barcode', '=', manufacturerID)
                ], limit=1)
                if not product_id: continue
                if product_id.qty_available >= 0: continue
                self.createUpdateCsvFile("delete", row)
                product_id.is_published = False

    def updateQtyStockProduct(self, product_id, availableQuantity):
        """ function to update qty product on supplier wherehouse """
        print('UPDATE QTY', availableQuantity)
        stock_id = self.env['stock.quant'].sudo().search([
            ("location_id", "=", self.stock_id.id),
            ("product_id", "=", product_id.product_variant_id.id),
        ], limit=1)
        print('stick', stock_id)
        if stock_id:
            qty = stock_id.quantity + availableQuantity
            print('THE QTY', qty)
            stock_id.sudo().write({
                "inventory_quantity": qty,
                "quantity": availableQuantity
            })
            stock_id.sudo().action_apply_inventory()
        else:
            stock_id = self.env['stock.quant'].sudo().create({
                "location_id": self.stock_id.id,
                "product_id": product_id.product_variant_id.id,
                "inventory_quantity": availableQuantity,
                "quantity": availableQuantity
            })
            stock_id.sudo().action_apply_inventory()
        return True

    def startScriptUsingButtonTest(self):
        if not self.file_csv: return
        if not self.file_csv:
            _logger.warning("Aucun fichier CSV n'est disponible pour le traitement.")
            return
        # Décodage du fichier CSV en base64
        try:
            fichier_decoded = base64.b64decode(self.file_csv)
            fichier_io = io.BytesIO(fichier_decoded)
        except Exception as e:
            _logger.error(f"Erreur lors du décodage du fichier CSV : {e}")
            return
        # Lire le CSV
        try:
            df = pd.read_csv(fichier_io, delimiter=';', encoding='utf-8', low_memory=False, dtype={'ean': str})
        except Exception as e:
            _logger.error(f"Erreur lors de la lecture du fichier CSV : {e}")
            return
        index = self.index if self.index else 0
        print('INDEX', index)
        df_filtered = df.loc[index:]
        i = 0
        selectCategory = self.selectCategoryName()
        print('selectCategory', selectCategory)
        for index, row in df_filtered.iterrows():
            print(f"Index: {index}, ProductID: {row['ProductID']}, ManufacturerID: {row['EAN']}")
            i += 1
            manufacturerID = row.get('EAN')
            manufacturerID = str(manufacturerID).replace(".0", "").replace(".00", "")
            if not manufacturerID or manufacturerID == '': continue
            category = row.get('Category1')
            if not isinstance(category, str):
                continue
            if category.lower() not in selectCategory: continue
            availableQuantity = row.get('AvailableQuantity')
            AvailableNextQuantity = 0
            print(f'\n\n availableQuantity : {availableQuantity}, type :{type(availableQuantity)} \n\n')
            # if not isinstance(availableQuantity, float) or  not isinstance(availableQuantity, int): continue
            print('OK')
            # select product on odoo database
            product_id = self.env['product.template'].sudo().search([
                ('barcode', 'ilike', manufacturerID)
            ], limit=1)
            if product_id and product_id.categ_id:
                categoryCode = product_id.categ_id.categoryCode if product_id.categ_id.categoryCode else ''
                category_split = categoryCode.split(',')
                find = False
                for cat in category_split:
                    if cat.lower() in selectCategory:
                        find = True
                        break
                if not find: product_id = None
            # start the script and logique to update qty and price on wherehouse of supplier
            # strp published
            if product_id and not product_id.is_published and availableQuantity > 0:
                self.createUpdateCsvFile("published", row)
            # step create
            if not product_id:
                # create a new line on file csv create product
                self.createUpdateCsvFile("create", row)
            # step update
            elif product_id and availableQuantity > 0:
                self.createUpdateCsvFile("update", row)
                self.updateQtyStockProduct(product_id, availableQuantity)
                supplier_id = row.get('Supplier')
                if supplier_id:
                    product_id.sudo().supplier_id = supplier_id.lower()
                product_id.sudo().is_published = True
                if product_id.sudo().standard_price == 0 or product_id.sudo().standard_price > convert_comma_decimal_to_float(row.get('NetPrice')):
                    product_id.sudo().standard_price = convert_comma_decimal_to_float(row.get('NetPrice'))
            # step unpublished
            elif availableQuantity <= 0 and product_id and product_id.qty_available <= 0:
                self.createUpdateCsvFile("delete", row)
                self.updateQtyStockProduct(product_id, availableQuantity)
                product_id.sudo().is_published = False
                if product_id.sudo().standard_price == 0 or product_id.sudo().standard_price > convert_comma_decimal_to_float(row.get('NetPrice')):
                    product_id.sudo().standard_price = convert_comma_decimal_to_float(row.get('NetPrice'))

            if i >= 1000 or index + 1 == self.max_products:
                self.index = index + 1
                break


class ProductCategory(models.Model):
    _inherit = "product.category"

    categoryCode = fields.Char("Category code")
