# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, SUPERUSER_ID

from odoo.http import request
import json
import requests
_logger = logging.getLogger(__name__)

DEFAULT_COUNTRY_CODE_API_NAME = 'country_code'
DEFAULT_IP_CACHING_MODEL = 'website.cache.ip'

class Website(models.Model):
    _inherit = 'website'

    enable_geolocation_pricelist = fields.Boolean(string='Set pricelist based on customer\'s geolocation')

    # Override 'get_current_pricelist()' function
    def get_current_pricelist(self):
        pricelist = super(Website, self).get_current_pricelist()

        if request.website.enable_geolocation_pricelist:
            if request and not request.session.get('website_sale_current_pl'):
                website_available_pricelist = request.website.get_pricelist_available(show_visible=True)
                # IP caching retrieval
                ip_caching = self.env[DEFAULT_IP_CACHING_MODEL].sudo().search([('ip', '=', request.httprequest.remote_addr)], order='id desc', limit=1)
                if ip_caching and ip_caching[0] and ip_caching[0].country_code:
                    get_country = self.env['res.country'].sudo().search([('code', '=', ip_caching[0].country_code)])
                    if get_country:
                        get_pricelist = website_available_pricelist.filtered(lambda p: get_country.id in p.country_group_ids.country_ids.ids).sorted(key=lambda p: p.sequence)
                        if get_pricelist:
                            return get_pricelist[0]
                        else:
                            return pricelist
                    else:
                        return pricelist
                else: # Call API Service Location
                    try:
                        url = 'https://ipapi.co/' + request.httprequest.remote_addr + '/json/'
                        response = requests.get(url, timeout=5).text
                        response_json = json.loads(response)
                        if response_json.get(DEFAULT_COUNTRY_CODE_API_NAME):
                            # Add IP / Country Code to IP Caching
                            self.env[DEFAULT_IP_CACHING_MODEL].sudo().create({
                                'ip': request.httprequest.remote_addr,
                                'country_code': response_json.get(DEFAULT_COUNTRY_CODE_API_NAME),
                                'date_cached': fields.Datetime.now(),
                            })
                            get_country = self.env['res.country'].sudo().search([('code', '=', response_json.get(DEFAULT_COUNTRY_CODE_API_NAME))])
                            if get_country:
                                # Get Pricelist
                                get_pricelist = website_available_pricelist.filtered(lambda p: get_country.id in p.country_group_ids.country_ids.ids).sorted(key=lambda p: p.sequence)
                                if get_pricelist:
                                    return get_pricelist[0]
                                else:
                                    return pricelist
                            else:
                                return pricelist
                        else:
                            return pricelist
                    except:
                        return pricelist
        else:
            return pricelist
        return pricelist