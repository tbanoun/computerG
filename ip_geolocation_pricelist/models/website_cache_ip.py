# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, SUPERUSER_ID
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

DEFAULT_CACHE_DURATION = 1 # in days

class WebsiteCacheIp(models.Model):
    _name = 'website.cache.ip'
    _description = 'Caching IP during a configurable period'
    _rec_name = 'ip'

    ip = fields.Text(string='IP', index=True)
    country_code = fields.Text(string='Country Code')
    date_cached = fields.Datetime(string='Date of Cache')

    @api.model
    def _website_cache_ip_cleaner(self):
        cache_duration = self.env['ir.config_parameter'].sudo().get_param('ip_geolocation_pricelist.ip_cache_duration', DEFAULT_CACHE_DURATION)
        date_cache_limit = datetime.now() - timedelta(days=cache_duration)
        # Unlink old records
        self.env[self._name].sudo().search([('date_cached', '<', date_cache_limit)]).unlink()
