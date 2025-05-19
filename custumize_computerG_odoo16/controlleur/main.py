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

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        domains = [request.website.sale_product_domain()]
        if search:
            for srch in search.split(" "):
                subdomains = [
                    [('product_variant_ids.barcode', 'ilike', srch)],
                    [('product_variant_ids.default_code', 'ilike', srch)]
                ]
                if search_in_description:
                    subdomains.append([('website_description', 'ilike', srch)])
                    subdomains.append([('description_sale', 'ilike', srch)])
                extra_subdomain = self._add_search_subdomains_hook(srch)
                if extra_subdomain:
                    subdomains.append(extra_subdomain)
                domains.append(expression.OR(subdomains))

        if category:
            domains.append([('public_categ_ids', 'child_of', int(category))])

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domains.append([('attribute_line_ids.value_ids', 'in', ids)])
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domains.append([('attribute_line_ids.value_ids', 'in', ids)])

        return expression.AND(domains)