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

    def get_current_pricelist(self):
        _logger.debug("Calling overridden get_current_pricelist()")
        pricelist = super(Website, self).get_current_pricelist()
        _logger.debug("Default pricelist: %s", pricelist.name if pricelist else "None")
        ip = request.httprequest.remote_addr
        _logger.debug("Request Client IP: %s", ip)
        print(f"\n\n\n\n Request Client IP: {ip} \n\n\n")
        if request and request.session.get('geo_pricelist_id'):
            cached_pl = self.env['product.pricelist'].browse(request.session['geo_pricelist_id']).exists()
            if cached_pl:
                _logger.debug("Returning cached geo pricelist from session: %s", cached_pl.name)
                return cached_pl


        if request.website.enable_geolocation_pricelist:
            _logger.info("Geolocation-based pricelist is enabled")

            if request and not request.session.get('website_sale_current_pl'):
                website_available_pricelist = request.website.get_pricelist_available(show_visible=True)
                _logger.debug("Available website pricelists count: %d", len(website_available_pricelist))

                ip = request.httprequest.remote_addr
                _logger.debug("Request IP: %s", ip)

                ip_caching = self.env[DEFAULT_IP_CACHING_MODEL].sudo().search([('ip', '=', ip)], order='id desc', limit=1)
                if ip_caching and ip_caching[0] and ip_caching[0].country_code:
                    _logger.info("IP cache hit: %s => %s", ip, ip_caching[0].country_code)
                    get_country = self.env['res.country'].sudo().search([('code', '=', ip_caching[0].country_code)])
                    if get_country:
                        _logger.debug("Country found: %s", get_country.name)
                        get_pricelist = website_available_pricelist.filtered(
                            lambda p: get_country.id in p.country_group_ids.country_ids.ids or get_country.id in p.country_ids.ids).sorted(key=lambda p: p.sequence)
                        if get_pricelist:
                            _logger.info("Matching pricelist found: %s", get_pricelist[0].name)
                            return get_pricelist[0]
                        else:
                            _logger.info("No matching pricelist for country, returning default")
                            return pricelist
                    else:
                        _logger.warning("Country code %s not found in res.country", ip_caching[0].country_code)
                        return pricelist
                else:
                    _logger.info("IP not found in cache, calling geolocation API")
                    try:
                        response_json = {}
                        url =  f'http://ip-api.com/json/{ip}'
                        response = requests.get(url, timeout=5)
                        if response.status_code == 200:
                            response_json = response.json()
                        else:
                            url = f'https://ipapi.co/{ip}/json/'
                            response = requests.get(url, timeout=5)
                            if response.status_code == 200:
                                response_json = response.json()
                        _logger.debug("Calling URL: %s", url)
                        _logger.info("API Response: %s", response)
                        _logger.info("API response: %s", response_json)

                        if response_json.get(DEFAULT_COUNTRY_CODE_API_NAME):
                            country_code = response_json.get(DEFAULT_COUNTRY_CODE_API_NAME)
                            _logger.info("Geolocation API returned country code: %s", country_code)

                            self.env[DEFAULT_IP_CACHING_MODEL].sudo().create({
                                'ip': ip,
                                'country_code': country_code,
                                'date_cached': fields.Datetime.now(),
                            })
                            _logger.debug("Cached IP and country code")

                            get_country = self.env['res.country'].sudo().search([('code', '=', country_code)])
                            if get_country:
                                _logger.debug("Country found: %s", get_country.name)
                                get_pricelist = website_available_pricelist.filtered(
                                    lambda p: get_country.id in p.country_group_ids.country_ids.ids or get_country.id in p.country_ids.ids).sorted(key=lambda p: p.sequence)
                                if get_pricelist:
                                    _logger.info("Matching pricelist found: %s", get_pricelist[0].name)
                                    return get_pricelist[0]
                                else:
                                    _logger.info("No matching pricelist for country, returning default")
                                    return pricelist
                            else:
                                _logger.warning("Country code %s not found in res.country", country_code)
                                return pricelist
                        else:
                            _logger.warning("Country code not found in geolocation API response")
                            return pricelist
                    except Exception as e:
                        _logger.exception("Geolocation API request failed: %s", e)
                        return pricelist
        else:
            _logger.info("Geolocation-based pricelist is disabled")

        return pricelist
