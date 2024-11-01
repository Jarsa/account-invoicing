# Copyright 2023 Jarsa, (<https://www.jarsa.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _compute_name(self):
        res = super()._compute_name()
        if self.product_id.default_code:
            self.name = self.name.replace(f"[{self.product_id.default_code}] ", "").strip()
        return res
