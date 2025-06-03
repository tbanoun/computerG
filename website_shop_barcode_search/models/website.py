from odoo import models,fields,api

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
        user = self.env.user
        currency = user.company_id.currency_id
        all_results = []
        total_count = 0
        search_details_copy = []
        for val in search_details:
            model = val.get('model')
            if model == 'product.template': continue
            search_details_copy.append(
                val
            )
        search_details_copy.append(
            {'model': 'product.template',
             'base_domain': [['|','&', ('sale_ok', '=', True), ('barcode2', 'ilike', search), ('website_id', 'in', (False, 2))]],
             'search_fields': ['name', 'barcode2','default_code', 'product_variant_ids.default_code', 'description',
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
                         'detail': {'name': 'price', 'type': 'html', 'display_currency': currency},
                         'detail_strike': {'name': 'list_price', 'type': 'html', 'display_currency': currency},
                         'extra_link': {'name': 'category', 'type': 'html'}}, 'icon': 'fa-shopping-cart'}
        )

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


        )
        for search_detail in search_details_copy:
            model = self.env[search_detail['model']]
            results, count = model._search_fetch(search_detail, search, limit, order)
            search_detail['results'] = results
            total_count += count
            search_detail['count'] = count
            all_results.append(search_detail)

        return total_count, all_results



class ProductTemplate(models.Model):
    _inherit = "product.template"

    barcode2 = fields.Char(related="barcode")
    out_of_stock_message = fields.Char(string="Out-of-Stock Message")
    qty_available_wt = fields.Float(string="Qty Available WT")
    
    @api.depends('barcode')
    def _computeBarcode(self):
        for rec in self:
            rec.barcode2 = rec.barcode or ''