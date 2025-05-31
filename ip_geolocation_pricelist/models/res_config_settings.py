# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import AccessError, ValidationError, UserError

DEFAULT_CACHE_DURATION = 1 # in days

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_geolocation_pricelist = fields.Boolean(string='Set pricelist based on customer\'s geolocation',
                                                  readonly=False, related='website_id.enable_geolocation_pricelist')
    ip_cache_duration = fields.Integer('Duration of IP caching (in days)')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            ip_cache_duration = self.env['ir.config_parameter'].sudo().get_param('ip_geolocation_pricelist.ip_cache_duration', DEFAULT_CACHE_DURATION),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ip_cache_duration = self.ip_cache_duration or DEFAULT_CACHE_DURATION
        self.env['ir.config_parameter'].sudo().set_param('ip_geolocation_pricelist.ip_cache_duration', ip_cache_duration)
