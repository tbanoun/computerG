from odoo import fields, models
from datetime import datetime, timedelta


class ProductHistoryActions(models.Model):
    _name = "product.import.history"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("name")
    createdActions_ids = fields.One2many("history.create.action", "history_action_id")
    DeletedActions_ids = fields.One2many("history.deleted.action", "history_action_id")
    UpdatedActions_ids = fields.One2many("history.updated.action", "history_action_id")
    publishedActions_ids = fields.One2many("history.published.action", "history_action_id")


    def cleanHistoryFile(self):
        """Supprime les entrées de plus de 7 jours."""
        date_limit = fields.Date.today() - timedelta(days=7)

        models_to_clean = [
            "history.create.action",
            "history.deleted.action",
            "history.updated.action",
            "history.published.action"
        ]

        for model_name in models_to_clean:
            records = self.env[model_name].search([('date', '<', date_limit)])
            if records:
                records.unlink()


class HistoryCreateActions(models.Model):
    _name = "history.create.action"

    file = fields.Binary("CSV File")
    file_name = fields.Char(string="Nom du fichier")
    date = fields.Date("Date")
    history_action_id = fields.Many2one("product.import.history")

class HistoryDeletedActions(models.Model):
    _name = "history.deleted.action"

    file = fields.Binary("CSV File")
    file_name = fields.Char(string="Nom du fichier")
    date = fields.Date("Date")
    history_action_id = fields.Many2one("product.import.history")

class HistoryUpdatedActions(models.Model):
    _name = "history.updated.action"

    file = fields.Binary("CSV File")
    file_name = fields.Char(string="Nom du fichier")
    date = fields.Date("Date")
    history_action_id = fields.Many2one("product.import.history")

class HistoryUpdatedActions(models.Model):
    _name = "history.published.action"

    file = fields.Binary("CSV File")
    file_name = fields.Char(string="Nom du fichier")
    date = fields.Date("Date")
    history_action_id = fields.Many2one("product.import.history")