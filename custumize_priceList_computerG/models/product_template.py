from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
import itertools


class ProductTemplate(models.Model):
    _inherit = "product.template"

    class ProductTemplate(models.Model):
        _inherit = "product.template"

        def _create_variant_ids(self):
            if not self:
                return

            self.env.flush_all()
            Product = self.env["product.product"]

            variants_to_create = []
            variants_to_activate = Product
            variants_to_unlink = Product

            for tmpl_id in self:
                lines = tmpl_id.attribute_line_ids

                all_variants = tmpl_id.with_context(active_test=False).product_variant_ids.sorted(
                    lambda p: (p.active, -p.id))

                current_variants_to_create = []
                current_variants_to_activate = Product

                # Ajouter les attributs à valeur unique sur chaque variante
                single_value_lines = lines.filtered(
                    lambda ptal: len(ptal.product_template_value_ids._only_active()) == 1
                )
                if single_value_lines:
                    for variant in all_variants:
                        combination = variant.product_template_attribute_value_ids | single_value_lines.product_template_value_ids._only_active()
                        if (
                                len(combination) == len(lines) and
                                combination.attribute_line_id == lines
                        ):
                            variant.product_template_attribute_value_ids = combination

                # Combinaisons existantes
                existing_variants = {
                    variant.product_template_attribute_value_ids: variant for variant in all_variants
                }

                # Calcul de TOUTES les combinaisons (même pour les attributs en no_variant)
                all_combinations = itertools.product(*[
                    ptal.product_template_value_ids._only_active() for ptal in lines
                ])

                for combination_tuple in all_combinations:
                    combination = self.env['product.template.attribute.value'].concat(*combination_tuple)
                    # Supprimer la vérification _is_combination_possible_by_config ou modifier le paramètre ignore_no_variant
                    is_combination_possible = True  # On force la création de toutes les combinaisons
                    if not is_combination_possible:
                        continue

                    if combination in existing_variants:
                        current_variants_to_activate += existing_variants[combination]
                    else:
                        current_variants_to_create.append(tmpl_id._prepare_variant_values(combination))
                        if len(current_variants_to_create) > 1000:
                            raise UserError(_(
                                'Too many variants to generate. '
                                'Please reduce combinations or use dynamic variants.'
                            ))

                variants_to_create += current_variants_to_create
                variants_to_activate += current_variants_to_activate
                variants_to_unlink += all_variants - current_variants_to_activate

            if variants_to_activate:
                variants_to_activate.write({'active': True})
            if variants_to_create:
                Product.create(variants_to_create)
            if variants_to_unlink:
                variants_to_unlink._unlink_or_archive()
                if self.exists() != self:
                    raise UserError(
                        _("This configuration of product attributes, values, and exclusions would lead to no possible variant. Please archive or delete your product directly if intended."))

            self.env.flush_all()
            self.env.invalidate_all()
            return True

