from odoo import api, fields, models
import requests
from io import StringIO, BytesIO
import csv
import pandas as pd

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    supplier_id = fields.Selection(
        [
            ('other', 'Other'),
            ('multitech', 'Multitech'),
            ('infoQuest', 'InfoQuest'),
            ('logiCom', 'LogiCom'),
        ], string='Product Condition', default='other')