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
        _logger.info("=== DEBUT get_current_pricelist ===")
        pricelist = super(Website, self).get_current_pricelist()
        _logger.info(f"Pricelist de base: {pricelist.id if pricelist else 'Aucun'}")

        if request.website.enable_geolocation_pricelist:
            _logger.info("Geolocation pricelist est activé")

            if request and not request.session.get('website_sale_current_pl'):
                _logger.info("Pas de pricelist en session, vérification par géolocalisation")
                website_available_pricelist = request.website.get_pricelist_available(show_visible=True)
                _logger.info(f"Pricelists disponibles: {website_available_pricelist.ids}")

                # Vérification du cache IP
                ip_caching = self.env[DEFAULT_IP_CACHING_MODEL].sudo().search(
                    [('ip', '=', request.httprequest.remote_addr)],
                    order='id desc',
                    limit=1
                )
                _logger.info(f"IP du client: {request.httprequest.remote_addr}")
                _logger.info(f"Résultat cache IP: {ip_caching.country_code if ip_caching else 'Aucun cache trouvé'}")

                if ip_caching and ip_caching[0] and ip_caching[0].country_code:
                    _logger.info(f"Cache trouvé - Code pays: {ip_caching[0].country_code}")
                    get_country = self.env['res.country'].sudo().search([('code', '=', ip_caching[0].country_code)])

                    if get_country:
                        _logger.info(f"Pays trouvé: {get_country.name} (ID: {get_country.id})")
                        _logger.info(f'website_available_pricelist {website_available_pricelist}')
                        get_pricelist = website_available_pricelist.filtered(
                            lambda p: get_country.id in p.country_group_ids.country_ids.ids
                        ).sorted(key=lambda p: p.sequence)

                        if get_pricelist:
                            _logger.info(f"Pricelist correspondant trouvé: {get_pricelist[0].id}")
                            return get_pricelist[0]
                        else:
                            _logger.info("Aucun pricelist ne correspond à ce pays")
                            return pricelist
                    else:
                        _logger.info("Aucun pays ne correspond à ce code")
                        return pricelist
                else:  # Appel à l'API de géolocalisation
                    _logger.info("Appel à l'API de géolocalisation")
                    ip = '129.45.120.244'
                    try:
                        url = 'https://ipapi.co/' + ip + '/json/'
                        _logger.info(f"URL API: {url}")
                        response = requests.get(url, timeout=5).text
                        _logger.info(f"Réponse API: {response}")
                        response_json = json.loads(response)

                        if response_json.get(DEFAULT_COUNTRY_CODE_API_NAME):
                            _logger.info(f"Code pays de l'API: {response_json.get(DEFAULT_COUNTRY_CODE_API_NAME)}")
                            # Ajout au cache IP
                            cache_data = {
                                'ip': ip,
                                'country_code': response_json.get(DEFAULT_COUNTRY_CODE_API_NAME),
                                'date_cached': fields.Datetime.now(),
                            }
                            self.env[DEFAULT_IP_CACHING_MODEL].sudo().create(cache_data)
                            _logger.info(f"Cache IP créé: {cache_data}")

                            get_country = self.env['res.country'].sudo().search(
                                [('code', '=', response_json.get(DEFAULT_COUNTRY_CODE_API_NAME))]
                            )

                            if get_country:
                                _logger.info(f"Pays trouvé: {get_country.name} (ID: {get_country.id})")
                                _logger.info(f'website_available_pricelist {website_available_pricelist}')
                                for price in website_available_pricelist:
                                    print(price.name)
                                get_pricelist = website_available_pricelist.filtered(
                                    lambda p: get_country.id in p.country_group_ids.country_ids.ids
                                ).sorted(key=lambda p: p.sequence)

                                if get_pricelist:
                                    _logger.info(f"Pricelist correspondant trouvé: {get_pricelist[0].id}")
                                    return get_pricelist[0]
                                else:
                                    _logger.info("Aucun pricelist ne correspond à ce pays")
                                    return pricelist
                            else:
                                _logger.info("Aucun pays ne correspond à ce code")
                                return pricelist
                        else:
                            _logger.info("L'API n'a pas retourné de code pays")
                            return pricelist
                    except Exception as e:
                        _logger.error(f"Erreur lors de l'appel API: {str(e)}")
                        return pricelist
            else:
                _logger.info("Pricelist déjà en session ou requête non disponible")
        else:
            _logger.info("Geolocation pricelist est désactivé")

        _logger.info(f"Retour du pricelist par défaut: {pricelist.id if pricelist else 'Aucun'}")
        _logger.info("=== FIN get_current_pricelist ===")
        return pricelist