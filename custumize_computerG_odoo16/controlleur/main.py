from odoo import http
from odoo.http import request
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.osv import expression
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):

    def _shop_lookup_products(self, attrib_set, options, post, search, website):
        ProductTemplate = request.env['product.template'].with_context(bin_size=True)

        # Recherche initiale via fuzzy
        product_count, details, fuzzy_search_term = website._search_with_fuzzy(
            "products_only", search,
            limit=None,
            order=self._get_search_order(post),
            options=options
        )

        search_result = details[0].get('results', ProductTemplate)

        # Recherche complémentaire via code-barres
        if search:
            barcode_products = ProductTemplate.search([('barcode', 'ilike', search)])
            # Fusionner et supprimer les doublons
            combined_ids = list(set((search_result | barcode_products).ids))
            search_result = ProductTemplate.browse(combined_ids)

        return fuzzy_search_term, product_count, search_result