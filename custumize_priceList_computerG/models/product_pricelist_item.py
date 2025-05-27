from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError
import math


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    margin = fields.Float(string="Margin (%)", default=0,
                          digits=(16, 2))

    rule_tip = fields.Char(compute='_compute_rule_tip')

    @api.depends_context('lang')
    @api.depends('compute_price', 'price_discount', 'price_surcharge', 'base', 'price_round')
    def _compute_rule_tip(self):
        base_selection_vals = {elem[0]: elem[1] for elem in self._fields['base']._description_selection(self.env)}
        self.rule_tip = False
        for item in self:
            if item.compute_price != 'formula':
                continue
            base_amount = 100
            discount_factor = (100 - item.price_discount) / 100
            margin = item.margin
            discounted_price = base_amount * discount_factor
            if item.price_round:
                discounted_price = tools.float_round(discounted_price, precision_rounding=item.price_round)
            surcharge = tools.format_amount(item.env, item.price_surcharge, item.currency_id)
            typePrice = 'cost'
            if self.base == 'list_price':
                typePrice = 'Sales Price'
            item.rule_tip = _(
                "%(base)s with a profit margin %(margin)s and with a %(discount)s %% discount and %(surcharge)s extra fee\n"
                f"Example: ((%(base)s +(%(base)s * Profit Margin)) + Extra Fee)",
                base=base_selection_vals[item.base],
                discount=item.price_discount,
                surcharge=surcharge,
                amount=tools.format_amount(item.env, 100, item.currency_id),
                discount_charge=discount_factor,
                price_surcharge=surcharge,
                margin=margin,
                total_amount=tools.format_amount(
                    item.env, discounted_price + item.price_surcharge, item.currency_id),
            )

    def _compute_price(self, product, quantity, uom, date, currency=None):
        user = self.env.user
        print('\n\n\n _compute_price \n')
        print(f"Utilisateur connecté : {user.name} (ID: {user.id})\n\n\n")
        product.ensure_one()
        uom.ensure_one()

        currency = currency or self.currency_id
        currency.ensure_one()

        product_uom = product.uom_id
        convert = lambda p: product_uom._compute_price(p, uom) if product_uom != uom else p

        # 1. Get the actual product (variant or template)
        actual_product = product
        if product._name == 'product.template':
            # In Odoo 16.0, use product_variant_ids[0] if exists
            actual_product = product.product_variant_ids[0] if product.product_variant_ids else product

        # 2. Calculate base price (normal price)
        base_price, extraPrice = self._compute_base_price_duplicate(actual_product, quantity, uom, date, currency)
        # 3. Add price_extra from product variant if exists
        # if hasattr(actual_product, 'price_extra') and self.compute_price != 'formula':
        #     base_price += convert(actual_product.price_extra)
        # elif hasattr(actual_product, 'price_extra') and self.compute_price == 'formula':
        #     # extraPrice += convert(actual_product.price_extra)
        #     pass

        # 4. Add price_extra from selected attributes (for both templates and variants)
        # if hasattr(product, 'product_template_attribute_value_ids') and self.compute_price != 'formula':
        #     attribute_extras = sum(
        #         convert(attr.price_extra)
        #         for attr in product.product_template_attribute_value_ids
        #         # Include all attributes or only no_variant ones
        #         # if attr.attribute_id.create_variant == 'no_variant'
        #     )
        #     base_price += attribute_extras
        # elif hasattr(product, 'product_template_attribute_value_ids') and self.compute_price == 'formula':
        #     attribute_extras = sum(
        #         convert(attr.price_extra)
        #         for attr in product.product_template_attribute_value_ids
        #         # Include all attributes or only no_variant ones
        #         # if attr.attribute_id.create_variant == 'no_variant'
        #     )
        #     print('HELLOOO extraPrice 1', extraPrice)
        #     # base_price += attribute_extras
        #     print('HELLOOO attribute_extras', extraPrice)
        #     print('HELLOOO extraPrice 2', extraPrice)

        # print('SAMIA attribute_extras', attribute_extras)
        # 5. Apply pricing rules
        if self.compute_price == 'fixed':
            price = convert(self.fixed_price)
        elif self.compute_price == 'percentage':
            price = (base_price - (base_price * (self.percent_price / 100))) or 0.0
        elif self.compute_price == 'formula':
            print(f'The Bingo price {base_price}')
            price = (base_price - (base_price * (self.price_discount / 100))) or 0.0
            if self.price_round:
                price = tools.float_round(price, precision_rounding=self.price_round)
            if self.price_surcharge:
                price += convert(self.price_surcharge)
            if self.margin:
                price = math.ceil(price + ((self.margin / 100) * base_price))
        else:
            price = base_price
        # if  self.compute_price == 'formula':
        price += extraPrice
        return price

    def _compute_base_price_duplicate(self, product, quantity, uom, date, target_currency):
        """ Compute the base price for a given rule

        :param product: recordset of product (product.product/product.template)
        :param float qty: quantity of products requested (in given uom)
        :param uom: unit of measure (uom.uom record)
        :param datetime date: date to use for price computation and currency conversions
        :param target_currency: pricelist currency

        :returns: base price, expressed in provided pricelist currency
        :rtype: float
        """
        target_currency.ensure_one()
        priceExtra = 0
        rule_base = self.base or 'list_price'
        if rule_base == 'pricelist' and self.base_pricelist_id:
            price = self.base_pricelist_id._get_product_price(product, quantity, uom, date)
            src_currency = self.base_pricelist_id.currency_id
        elif rule_base == "standard_price":
            src_currency = product.cost_currency_id
            priceObject = product.price_computeGostumize(rule_base, uom=uom, date=date)
            price = product.price_computeGostumize(rule_base, uom=uom, date=date)[product.id]
            priceExtra = 0
            if 'priceExtra' in product.price_computeGostumize(rule_base, uom=uom, date=date):
                priceExtra = product.price_computeGostumize(rule_base, uom=uom, date=date)['priceExtra']

        else:  # list_price
            src_currency = product.currency_id
            price = product.price_computeGostumize(rule_base, uom=uom, date=date)[product.id]
            priceObject = product.price_computeGostumize(rule_base, uom=uom, date=date)

            price = product.price_computeGostumize(rule_base, uom=uom, date=date)[product.id]
            priceExtra = 0
            if 'priceExtra' in product.price_computeGostumize(rule_base, uom=uom, date=date):
                priceExtra = product.price_computeGostumize(rule_base, uom=uom, date=date)['priceExtra']
        if src_currency != target_currency:
            price = src_currency._convert(price, target_currency, self.env.company, date, round=False)
        return price, priceExtra


class ProductProduct(models.Model):
    _inherit = "product.product"

    standard_price_with_cost = fields.Float(
        'Sales Price with Cost', compute='_compute_product_standard_price',
        digits='Product Price',
        help="The sale price is managed from the product template. Click on the 'Configure Variants' button to set the extra attribute prices.")

    @api.depends('standard_price', 'price_extra')
    def _compute_product_standard_price(self):
        print(f'\n\n price_extra \n\n')
        to_uom = None
        if 'uom' in self._context:
            to_uom = self.env['uom.uom'].browse(self._context['uom'])

        for product in self:
            print(f'\n\n price_extra {product.price_extra} \n\n')
            if to_uom:
                standard_price = product.uom_id._compute_price(product.standard_price, to_uom)
            else:
                standard_price = product.product_tmpl_id.standard_price
            product.standard_price_with_cost = standard_price + product.price_extra

    def price_computeGostumize(self, price_type, uom=None, currency=None, company=None, date=False):
        company = company or self.env.company
        date = date or fields.Date.context_today(self)
        # price_type = 'list_price'
        self = self.with_company(company)
        # if price_type == 'standard_price':
        #     # standard_price field can only be seen by users in base.group_user
        #     # Thus, in order to compute the sale price from the cost for users not in this group
        #     # We fetch the standard price as the superuser
        #     self = self.sudo()

        prices = dict.fromkeys(self.ids, 0.0)
        for product in self:
            price = product[price_type] or 0.0
            price_currency = product.currency_id
            if price_type == 'standard_price':
                priceExtra = 0
                price_currency = product.cost_currency_id
                priceExtra += product.price_extra
                if self._context.get('no_variant_attributes_price_extra'):
                    # # we have a list of price_extra that comes from the attribute values, we need to sum all that
                    # price += sum(self._context.get('no_variant_attributes_price_extra'))
                    priceExtra += sum(self._context.get('no_variant_attributes_price_extra'))
            if price_type == 'list_price':
                priceExtra = 0
                priceExtra += product.price_extra

                # price += product.price_extra
                # we need to add the price from the attributes that do not generate variants
                # (see field product.attribute create_variant)
                if self._context.get('no_variant_attributes_price_extra'):
                    # we have a list of price_extra that comes from the attribute values, we need to sum all that
                    priceExtra += sum(self._context.get('no_variant_attributes_price_extra'))
            if uom:
                price = product.uom_id._compute_price(price, uom)
            # Convert from current user company currency to asked one
            # This is right cause a field cannot be in more than one currency
            if currency:
                price = price_currency._convert(price, currency, company, date)

            prices[product.id] = price
            if price_type in ['standard_price', 'list_price']:
                prices['priceExtra'] = priceExtra

        return prices



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pass