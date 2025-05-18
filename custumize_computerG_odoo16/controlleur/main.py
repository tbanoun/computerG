from odoo import http
from odoo.http import request
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.osv import expression

class WebsiteSale(payment_portal.PaymentPortal):

    def _get_search_options(
            self, category=None, attrib_values=None, tags=None, min_price=0.0, max_price=0.0,
            conversion_rate=1, **post
    ):
        return {
            'displayDescription': True,
            'displayDetail': True,
            'displayExtraDetail': True,
            'displayExtraLink': True,
            'displayImage': True,
            'allowFuzzy': not post.get('noFuzzy'),
            'category': str(category.id) if category else None,
            'tags': tags,
            'min_price': min_price / conversion_rate,
            'max_price': max_price / conversion_rate,
            'attrib_values': attrib_values,
            'display_currency': post.get('display_currency'),
        }


    def _shop_lookup_products(self, attrib_set, options, post, search, website):
        Product = request.env['product.template']
        domain = options.get('domain', [])

        if search:
            # Recherche sur name, description ET barcode
            search_domain = [
                '|', '|', '|',
                ('name', 'ilike', search),
                ('description', 'ilike', search),
                ('description_sale', 'ilike', search),
                ('barcode', 'ilike', search),  # Ajout du barcode
            ]
            domain = expression.AND([domain, search_domain])

        # ... (le reste de la méthode) ...
        products = Product.search(domain, limit=website.shop_products_limit)
        return search, len(products), products


class WebsiteSale(payment_portal.PaymentPortal):

    def _get_shop_domain(self, search, category, attrib_values, search_in_description=True):
        print('Hello world')
        domains = [request.website.sale_product_domain()]
        if search:
            for srch in search.split(" "):
                subdomains = [
                    [('name', 'ilike', srch)],
                    [('barcode', 'ilike', srch)],
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
