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

    def updateProduct(self, is_line, row, id_value):
        try:
            product_template = self.env.ref(id_value)
        except Exception as e:
            return False
        print('product', product_template)
        if is_line:
            # update product line
            print('update product line')
            pass
        else:
            # update product attribute
            print('update product attribute')
            pass
        return True

    @api.constrains('file_name')
    def _check_file_extension(self):
        for record in self:
            if record.file_name:
                if not (record.file_name.lower().endswith('.xlsx') or record.file_name.lower().endswith('.csv')):
                    raise ValidationError("Le fichier doit être au format .csv ou .xlsx")

    def importProductLigne(self):
        # Décoder le fichier base64
        fichier_decoded = base64.b64decode(self.file_xls)

        # Charger dans un DataFrame pandas
        fichier_io = io.BytesIO(fichier_decoded)
        df = pd.read_excel(fichier_io)
        # Parcourir les lignes
        is_line = True
        id_value = ""
        error = 0
        update_index = 0
        for index, row in df.iterrows():
            id = row.get('id')
            if pd.isna(id):
                is_line = False
            else:
                id_value = id
                is_line = True
            update = self.updateProduct(is_line, row, id_value)
            if update and is_line:
                update_index += 1
            elif not update and is_line:
                error += 1

        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Succès'),
                'type': 'info',
                'message': f"{update_index} products have been updated with {error} error(s)!",
                'sticky': True,
            }
        }
        return notification
