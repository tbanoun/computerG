from odoo import fields, models, api, _
import pandas as pd
import base64
import io
import logging
from odoo.exceptions import ValidationError




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
        fichier_decoded = base64.b64decode(self.file_xls)
        # Charger dans un DataFrame pandas
        fichier_io = io.BytesIO(fichier_decoded)
        # df = pd.read_csv(fichier_io, delimiter=',')
        df = pd.read_excel(fichier_io)
        print(df)
        # Parcourir les lignes avec iterrows()
        i = 0
        for index, row in df.iterrows():
            pass
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Succès'),
                'type': 'info',
                'message': "The product import has been successfully completed.",
                'sticky': True,
            }
        }
        return notification
