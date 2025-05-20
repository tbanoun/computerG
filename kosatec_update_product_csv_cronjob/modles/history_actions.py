from odoo import fields, models
from datetime import datetime, timedelta


class ProductHistoryActions(models.Model):
    _name = "kosatec.product.import.history"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("name")
    createdActions_ids = fields.One2many("kosatec.history.create.action", "kosatec_history_action_id")
    DeletedActions_ids = fields.One2many("kosatec.history.deleted.action", "kosatec_history_action_id")
    UpdatedActions_ids = fields.One2many("kosatec.history.updated.action", "kosatec_history_action_id")
    publishedActions_ids = fields.One2many("kosatec.history.published.action", "kosatec_history_action_id")


    def cleanHistoryFile(self):
        """Supprime les entrées de plus de 7 jours."""
        date_limit = fields.Date.today() - timedelta(days=7)

        models_to_clean = [
            "kosatec.history.create.action",
            "kosatec.history.deleted.action",
            "kosatec.history.updated.action",
            "kosatec.history.published.action"
        ]

        for model_name in models_to_clean:
            records = self.env[model_name].search([('date', '<', date_limit)])
            if records:
                records.unlink()


class HistoryCreateActions(models.Model):
    _name = "kosatec.history.create.action"

    file = fields.Binary("CSV File")
    file_name = fields.Char(string="Nom du fichier")
    date = fields.Date("Date")
    kosatec_history_action_id = fields.Many2one("kosatec.product.import.history")

class HistoryDeletedActions(models.Model):
    _name = "kosatec.history.deleted.action"

    file = fields.Binary("CSV File")
    file_name = fields.Char(string="Nom du fichier")
    date = fields.Date("Date")
    kosatec_history_action_id = fields.Many2one("kosatec.product.import.history")

class HistoryUpdatedActions(models.Model):
    _name = "kosatec.history.updated.action"

    file = fields.Binary("CSV File")
    file_name = fields.Char(string="Nom du fichier")
    date = fields.Date("Date")
    kosatec_history_action_id = fields.Many2one("kosatec.product.import.history")

class HistoryUpdatedActions(models.Model):
    _name = "kosatec.history.published.action"

    file = fields.Binary("CSV File")
    file_name = fields.Char(string="Nom du fichier")
    date = fields.Date("Date")
    kosatec_history_action_id = fields.Many2one("kosatec.product.import.history")