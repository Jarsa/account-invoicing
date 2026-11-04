# Copyright 2023 Jarsa, (<https://www.jarsa.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # The label of journal items depends on the display_default_code context, so
    # calling super with that context would cache the value under another key.
    # Lines with a product compute it here with the product name only.

    def _get_product_name_without_code(self):
        self.ensure_one()
        return self.product_id.with_context(
            lang=self.move_id._get_lang(), display_default_code=False
        ).display_name

    def _compute_label(self):
        product_lines = self.filtered("product_id")
        res = super(AccountMoveLine, self - product_lines)._compute_label()
        for line in product_lines:
            product_name = line._get_product_name_without_code()
            name = line.name
            if name and line.product_id.default_code:
                # Descriptions saved by previous versions may start with the code
                name = name.removeprefix(f"[{line.product_id.default_code}] ")
            if not name:
                line.label = product_name
            elif name.splitlines()[0] == product_name:
                line.label = name
            else:
                line.label = f"{product_name}\n{name}"
        return res

    def _inverse_label(self):
        product_lines = self.filtered(lambda line: line.product_id and line.label)
        res = super(AccountMoveLine, self - product_lines)._inverse_label()
        for line in product_lines:
            line.name = line.label.removeprefix(
                line._get_product_name_without_code()
            ).removeprefix("\n")
        return res
