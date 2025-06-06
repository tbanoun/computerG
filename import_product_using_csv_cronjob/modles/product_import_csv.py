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
_logger = logging.getLogger(__name__)


class ImportProductConfig(models.Model):
    _name = "product.import.csv"
    _rec_name = "stock_id"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    csv_url = fields.Char()
    file_csv = fields.Binary()
    category_ids = fields.Many2many("product.category")
    stock_id = fields.Many2one("stock.location")
    index = fields.Integer()
    max_products = fields.Integer()
    active = fields.Boolean(default=True)
    start_update = fields.Boolean(default=False)

    def downoladCsvFile(self):
        _logger.warning(f"\n\n CSV URL: {self.csv_url} \n\n")
        _logger.warning(f"\n\n CSV URL: {self.start_update} \n\n")

        if self.start_update:
            self.start_update = False
        if self.start_update is True:
            return

        res = requests.get(self.csv_url)
        _logger.warning(f"\n\n response: {res} \n\n")

        if res.status_code != 200:
            return

        csv_data = StringIO(res.text)
        df = pd.read_csv(csv_data, sep=';', low_memory=False)

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
            'import_product_using_csv_cronjob.action_open_history_action')
        action['res_id'] = 1
        action['target'] = 'current'
        return action

    def deleteHistoryFile(self):
        create_ids = self.env['history.create.action'].sudo().search([]).unlink()
        delete_ids = self.env['history.deleted.action'].sudo().search([]).unlink()
        update_ids = self.env['history.updated.action'].sudo().search([]).unlink()
        update_ids = self.env['history.published.action'].sudo().search([]).unlink()

    def resetIndex(self):
        self.index = 0

    def selectCategoryName(self):
        result = []
        for rec in self.category_ids:
            if not rec.categoryCode or rec.categoryCode in result: continue
            result.append(rec.categoryCode.lower())
        return result

    def actionCreateCsvFile(self, row, date_now):
        historyCreate = self.env['history.create.action'].search([
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
            self.env['history.create.action'].create({
                'file': new_csv_encoded,
                'file_name': f"File_create_{str(date_now).replace('-', '_')}.csv",
                'history_action_id': 1,
                'date': date_now

            })

    def actionDeleteCsvFile(self, row, date_now):
        historyCreate = self.env['history.deleted.action'].search([
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
            self.env['history.deleted.action'].create({
                'file': new_csv_encoded,
                'file_name': f"File_unpublished_{str(date_now).replace('-', '_')}.csv",
                'history_action_id': 1,
                'date': date_now

            })

    def actionUpdateCsvFile(self, row, date_now):
        historyCreate = self.env['history.updated.action'].search([
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
            self.env['history.updated.action'].create({
                'file': new_csv_encoded,
                'file_name': f"File_update_{str(date_now).replace('-', '_')}.csv",
                'history_action_id': 1,
                'date': date_now

            })

    def actionPublishedCsvFile(self, row, date_now):
        historyCreate = self.env['history.published.action'].search([
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
            self.env['history.published.action'].create({
                'file': new_csv_encoded,
                'file_name': f"File_published_{str(date_now).replace('-', '_')}.csv",
                'history_action_id': 1,
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
        cron_id = self.env['product.import.csv'].sudo().browse(1)
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
        cron_id = self.env['product.import.csv'].sudo().browse(1)
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
            manufacturerID = manufacturerID.replace(".0", "")
            if not manufacturerID: continue
            category = row.get('Category1')
            if not isinstance(category, str):
                continue
            if category.lower() not in selectCategory: continue
            availableQuantity = row.get('AvailableQuantity')
            if not isinstance(availableQuantity, int): continue
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
        stock_id = self.env['stock.quant'].sudo().search([
            ("location_id", "=", self.stock_id.id),
            ("product_id", "=", product_id.product_variant_id.id),
        ], limit=1)
        if stock_id:
            stock_id.sudo().write({
                "inventory_quantity": availableQuantity
            })
            stock_id.sudo().action_apply_inventory()
        else:
            stock_id = self.env['stock.quant'].sudo().create({
                "location_id": self.stock_id.id,
                "product_id": product_id.product_variant_id.id,
                "inventory_quantity": availableQuantity
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
            df = pd.read_csv(fichier_io, delimiter=';', encoding='utf-8', low_memory=False)
        except Exception as e:
            _logger.error(f"Erreur lors de la lecture du fichier CSV : {e}")
            return
        index = self.index if self.index else 0
        df_filtered = df.loc[index:]
        i = 0
        selectCategory = self.selectCategoryName()
        for index, row in df_filtered.iterrows():
            # print(f"Index: {index}, ProductID: {row['ProductID']}, ManufacturerID: {row['ManufacturerID']}")
            i += 1
            manufacturerID = row.get('EAN')
            if not manufacturerID: continue
            if manufacturerID is None or math.isnan(manufacturerID):
                manufacturerID = 0  # Remplacez NaN par une valeur par défaut
            else:
                manufacturerID = int(manufacturerID)

            manufacturerID = str(manufacturerID).replace(".0", "").replace(".00", "")
            if not manufacturerID or manufacturerID == '': continue
            category = row.get('Category1')
            if not isinstance(category, str):
                continue
            if category.lower() not in selectCategory: continue
            availableQuantity = row.get('AvailableQuantity')
            if not isinstance(availableQuantity, int): continue
            # select product on odoo database
            product_id = self.env['product.template'].sudo().search([
                ('barcode', 'ilike', manufacturerID)
            ], limit=1)
            if product_id and product_id.categ_id:
                categoryCode = product_id.categ_id.categoryCode if product_id.categ_id.categoryCode else ''
                if categoryCode.lower() not in selectCategory:
                    product_id = None
            #start the script and logique to update qty and price on wherehouse of supplier
            # strp published
            if product_id and not product_id.is_published and availableQuantity > 0:
                self.createUpdateCsvFile("published", row)
            # step create
            if not product_id:
                # create a new line on file csv create product
                self.createUpdateCsvFile("create", row)
            #step update
            elif product_id and availableQuantity > 0:
                self.createUpdateCsvFile("update", row)
                self.updateQtyStockProduct(product_id, availableQuantity)
                product_id.sudo().is_published = True
                product_id.sudo().standard_price = row.get('NetPrice')
            # step unpublished
            elif availableQuantity <= 0 and product_id and product_id.qty_available <= 0:
                self.createUpdateCsvFile("delete", row)
                self.updateQtyStockProduct(product_id, availableQuantity)
                product_id.sudo().is_published = False
                product_id.sudo().standard_price = row.get('NetPrice')


            if i >= 1000 or index+1 == self.max_products:
                self.index = index +1
                break



class ProductCategory(models.Model):
    _inherit = "product.category"

    categoryCode = fields.Char("Category code")
