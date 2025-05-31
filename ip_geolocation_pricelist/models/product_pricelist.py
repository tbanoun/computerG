# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import AccessError, ValidationError, UserError

from collections import OrderedDict

class ProductPricelist(models.Model):
   _inherit = 'product.pricelist'

   country_ids = fields.Many2many(comodel_name='res.country', string="Countries",
                                  compute='_compute_country_ids')

   @api.depends('country_group_ids')
   def _compute_country_ids(self):
      for pricelist in self:
         if pricelist.country_group_ids:
            countries = []
            for country_group in pricelist.country_group_ids.sorted(key=lambda cg: cg.name):
               for country in country_group.country_ids.sorted(key=lambda c: c.name):
                  countries.append(country.id)
            pricelist.country_ids = [(6, 0, list(OrderedDict.fromkeys(countries)))]
         else:
            pricelist.country_ids = [(6, 0, [])]
