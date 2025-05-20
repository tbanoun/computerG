from odoo import api, models, fields


class ResConfigCronJobCsv(models.Model):
    _name = 'cronjob.csv.settings'
    _description = 'Configuration pour le cron de mise à jour CSV'

    stock_id = fields.Many2one("stock.location")