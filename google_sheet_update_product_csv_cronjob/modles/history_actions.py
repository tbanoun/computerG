from odoo import fields, models
from datetime import datetime, timedelta


class ProductHistoryActions(models.Model):
    _name = "google.product.import.history"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("name")
    createdActions_ids = fields.One2many("google.history.create.action", "google_history_action_id")
    DeletedActions_ids = fields.One2many("google.history.deleted.action", "google_history_action_id")
    UpdatedActions_ids = fields.One2many("google.history.updated.action", "google_history_action_id")
    publishedActions_ids = fields.One2many("google.history.published.action", "google_history_action_id")


    def cleanHistoryFile(self):
        """Supprime les entrées de plus de 7 jours."""
        date_limit = fields.Date.today() - timedelta(days=7)

        models_to_clean = [
            "google.history.create.action",
            "google.history.deleted.action",
            "google.history.updated.action",
            "google.history.published.action"
        ]

        for model_name in models_to_clean:
            records = self.env[model_name].search([('date', '<', date_limit)])
            if records:
                records.unlink()


class HistoryCreateActions(models.Model):
    _name = "google.history.create.action"

    file = fields.Binary("CSV File")
    file_name = fields.Char(string="Nom du fichier")
    date = fields.Date("Date")
    google_history_action_id = fields.Many2one("google.product.import.history")

class HistoryDeletedActions(models.Model):
    _name = "google.history.deleted.action"

    file = fields.Binary("CSV File")
    file_name = fields.Char(string="Nom du fichier")
    date = fields.Date("Date")
    google_history_action_id = fields.Many2one("google.product.import.history")

class HistoryUpdatedActions(models.Model):
    _name = "google.history.updated.action"

    file = fields.Binary("CSV File")
    file_name = fields.Char(string="Nom du fichier")
    date = fields.Date("Date")
    google_history_action_id = fields.Many2one("google.product.import.history")

class HistoryUpdatedActions(models.Model):
    _name = "google.history.published.action"

    file = fields.Binary("CSV File")
    file_name = fields.Char(string="Nom du fichier")
    date = fields.Date("Date")
    google_history_action_id = fields.Many2one("google.product.import.history")