from odoo import api, models, fields


class ResConfigCronJobCsv(models.Model):
    _name = 'cronjob.csv.settings'
    _description = 'Configuration pour le cron de mise à jour CSV'

    # stock_id = fields.Many2one("stock.location")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    stock_supplier_id = fields.Many2one("stock.location",  config_parameter='config_supplier_csv_cronjob.stock_supplier_id')