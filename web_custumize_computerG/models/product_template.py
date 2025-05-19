from odoo import fields, models, api
from bs4 import BeautifulSoup as bs
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    continue_seling = fields.Boolean(default=True)
    barcode2 = fields.Char(related="barcode")

    allow_out_of_stock_order = fields.Boolean(string='Continue selling when out-of-stock',
                                              compute="_computeContinueSelling")
    @api.depends('barcode')
    def _computeBarcode(self):
        for rec in self:
            rec.barcode2 = rec.barcode or ''

    def _computeContinueSelling(self):
        for rec in self:
            qty_available_wt = rec.qty_available_wt if rec.qty_available_wt > 0 else 0
            virtual_available = rec.virtual_available if rec.virtual_available > 0 else 0
            if qty_available_wt + virtual_available <= 0 and not rec.continue_seling:
                rec.allow_out_of_stock_order = False
            elif virtual_available <= 0 and not rec.showDelivryMessage and not rec.continue_seling:
                rec.allow_out_of_stock_order = False
            else:
                rec.allow_out_of_stock_order = True


            _logger.warning(f'Name : {rec.name}')
            _logger.warning(f'virtual_available : {virtual_available}')
            _logger.warning(f'qty_available_wt : {qty_available_wt}')
            _logger.warning(f'continue_seling : {rec.continue_seling}')
            _logger.warning(f'allow_out_of_stock_order : {rec.allow_out_of_stock_order}')
            print('\n\n')
            print(f'Name : {rec.name}')
            print(f'virtual_available : {virtual_available}')
            print(f'qty_available_wt : {qty_available_wt}')
            print(f'continue_seling : {rec.continue_seling}')
            print(f'continue_seling : {rec.allow_out_of_stock_order}')
            print('\n\n')

    out_of_stock_message = fields.Char(string="Out-of-Stock Message")
    showDelivryMessage = fields.Boolean(default=True)
    messageDelivryTimeRemoteStock = fields.Char('Delivery Time – Remote Stock Message', default='Ship 4-8 Days')
    messageDelivryTimeStock = fields.Char('Delivery Time – Stock Message', default='Ship 1-2 Days')

    def _compute_dr_show_out_of_stock(self):
        for product in self:
            product.dr_show_out_of_stock = 'OUT_OF_STOCK'

    # out_of_stock_message_text = fields.Char(compute='_compute_dr_show_out_of_stock', compute_sudo=True)
    out_of_stock_message_text = fields.Text(compute='_compute_out_of_stock_message_text',
                                            string="Out-of-Stock Text Message", default="Ask for Availability",
                                            translate=True)

    def _compute_out_of_stock_message_text(self):
        text = ''
        for rec in self:
            rec.out_of_stock_message_text = ''
            if rec.virtual_available > 0:
                text = rec.messageDelivryTimeStock
                # rec.out_of_stock_message_text = rec.messageDelivryTimeStock
            elif rec.qty_available_wt > 0:
                text = rec.messageDelivryTimeRemoteStock
                # rec.out_of_stock_message_text = rec.messageDelivryTimeRemoteStock
            else:
                text = rec.out_of_stock_message
                # rec.out_of_stock_message_text = rec.out_of_stock_message
            text = str(text)
            soup = bs(text, 'html.parser')
            if soup:
                text_soup = soup.get_text()
            else:
                text_soup = text
            rec.out_of_stock_message_text = text_soup


class ProductProduct(models.Model):
    _inherit = "product.product"

    showDelivryMessage = fields.Boolean(related='product_tmpl_id.showDelivryMessage')
    messageDelivryTimeRemoteStock = fields.Char(related='product_tmpl_id.messageDelivryTimeRemoteStock')
    messageDelivryTimeStock = fields.Char(related='product_tmpl_id.messageDelivryTimeStock')

class Website(models.Model):
    _inherit = "website"

    def _search_exact(self, search_details, search, limit, order):
        """
        Performs a search with a search text

        :param search_details: see :meth:`_search_get_details`
        :param search: text against which to match results
        :param limit: maximum number of results per model type involved in the result
        :param order: order on which to sort results within a model type

        :return: tuple containing:
            - total number of results across all involved models
            - list of results per model made of:
                - initial search_detail for the model
                - count: number of results for the model
                - results: model list equivalent to a `model.search()`
        """
        all_results = []
        total_count = 0
        search_details.append(
            {'model': 'product.template', 'base_domain': [
                ['|','&', ('sale_ok', '=', True), ('barcode2', 'ilike', search), ('website_id', 'in', (False, 2))]],
             'search_fields': ['name', 'barcode2', 'default_code', 'product_variant_ids.default_code', 'description',
                               'description_sale'],
             'fetch_fields': ['id', 'name', 'website_url', 'description', 'description_sale'],
             'mapping': {'name': {'name': 'name', 'type': 'text', 'match': True},
                         'default_code': {'name': 'default_code', 'type': 'text', 'match': True},
                         'product_variant_ids.default_code': {'name': 'product_variant_ids.default_code',
                                                              'type': 'text',
                                                              'match': True},
                         'website_url': {'name': 'website_url', 'type': 'text', 'truncate': False},
                         'image_url': {'name': 'image_url', 'type': 'html'},
                         'description': {'name': 'description_sale', 'type': 'text', 'match': True},
                         'extra_link': {'name': 'category', 'type': 'html'}}, 'icon': 'fa-shopping-cart'}

            # {'model': 'product.template', 'base_domain': [['&', ('sale_ok', '=', True), ('barcode2', 'ilike', search)]],
            #      'search_fields': ['barcode2'], 'fetch_fields': ['id', 'barcode2'],
            #      'mapping': {'name': {'name': 'name', 'type': 'text', 'match': True},
            #                  'website_url': {'name': 'url', 'type': 'text', 'truncate': False},
            #                  'image_url': {'name': 'image_url', 'type': 'html'}}, 'icon': 'fa-folder-o',
            #      'order': 'name asc, id desc'}

        )
        for search_detail in search_details:
            print("Brayane", search_detail)
            model = self.env[search_detail['model']]
            results, count = model._search_fetch(search_detail, search, limit, order)
            search_detail['results'] = results
            total_count += count
            search_detail['count'] = count
            all_results.append(search_detail)

        print(f'\n\n\n results => {all_results} \n\n\n')
        print(f'\n\n\n count => {total_count} \n\n\n')
        return total_count, all_results