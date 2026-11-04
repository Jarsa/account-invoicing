# Copyright 2026 Jarsa, (<https://www.jarsa.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo.fields import Command
from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceProductCodeRemove(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.coded_product = cls.env["product.product"].create(
            {
                "name": "Coded Product",
                "type": "service",
                "default_code": "TEST-CODE",
                "description_sale": "Sale description",
                "description_purchase": "Purchase description",
            }
        )
        cls.plain_coded_product = cls.env["product.product"].create(
            {
                "name": "Plain Coded Product",
                "type": "service",
                "default_code": "PLAIN-CODE",
            }
        )
        cls.no_code_product = cls.env["product.product"].create(
            {"name": "No Code Product", "type": "service"}
        )

    def _create_invoice_with_product(self, product, move_type="out_invoice"):
        return self._create_invoice(
            move_type=move_type,
            partner_id=self.partner_a,
            invoice_line_ids=[Command.create({"product_id": product.id})],
        )

    def test_customer_invoice_label_without_default_code(self):
        line = self._create_invoice_with_product(self.coded_product).invoice_line_ids
        self.assertEqual(line.name, "Sale description")
        self.assertEqual(line.label, "Coded Product\nSale description")

    def test_vendor_bill_label_without_default_code(self):
        line = self._create_invoice_with_product(
            self.coded_product, move_type="in_invoice"
        ).invoice_line_ids
        self.assertEqual(line.name, "Purchase description")
        self.assertEqual(line.label, "Coded Product\nPurchase description")

    def test_label_without_description(self):
        line = self._create_invoice_with_product(
            self.plain_coded_product
        ).invoice_line_ids
        self.assertFalse(line.name)
        self.assertEqual(line.label, "Plain Coded Product")

    def test_label_with_display_default_code_context(self):
        line = self._create_invoice_with_product(self.coded_product).invoice_line_ids
        self.assertEqual(
            line.with_context(display_default_code=True).label,
            "Coded Product\nSale description",
        )
        self.assertEqual(
            line.with_context(display_default_code=False).label,
            "Coded Product\nSale description",
        )

    def test_label_product_without_default_code(self):
        line = self._create_invoice_with_product(self.no_code_product).invoice_line_ids
        self.assertEqual(line.label, "No Code Product")

    def test_label_line_without_product(self):
        invoice = self._create_invoice(
            partner_id=self.partner_a,
            invoice_line_ids=[
                Command.create({"name": "[TEST-CODE] Free text", "price_unit": 10.0})
            ],
        )
        self.assertEqual(invoice.invoice_line_ids.label, "[TEST-CODE] Free text")

    def test_inverse_label(self):
        line = self._create_invoice_with_product(self.coded_product).invoice_line_ids
        line.label = "Coded Product\nCustom description"
        self.assertEqual(line.name, "Custom description")
        self.assertEqual(line.label, "Coded Product\nCustom description")

    def test_inverse_label_only_product_name(self):
        line = self._create_invoice_with_product(self.coded_product).invoice_line_ids
        line.label = "Coded Product"
        self.assertFalse(line.name)
        self.assertEqual(line.label, "Coded Product")

    def test_label_from_previous_versions(self):
        line = self._create_invoice_with_product(self.coded_product).invoice_line_ids
        # Description saved by Odoo 17.0 with this module installed
        line.name = "Coded Product\nSale description"
        self.assertEqual(line.label, "Coded Product\nSale description")
        # Description saved by Odoo 17.0 without this module
        line.name = "[TEST-CODE] Coded Product\nSale description"
        self.assertEqual(line.label, "Coded Product\nSale description")

    def test_invoice_form(self):
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        move_form.partner_id = self.partner_a
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.coded_product
            self.assertEqual(line_form.label, "Coded Product\nSale description")
        invoice = move_form.save()
        self.assertEqual(invoice.invoice_line_ids.name, "Sale description")
        self.assertEqual(
            invoice.invoice_line_ids.label, "Coded Product\nSale description"
        )

    def test_invoice_report(self):
        invoice = self._create_invoice_with_product(self.coded_product)
        invoice.action_post()
        html = (
            self.env["ir.actions.report"]
            ._render_qweb_html("account.report_invoice", invoice.ids)[0]
            .decode()
        )
        self.assertIn("Coded Product", html)
        self.assertNotIn("[TEST-CODE]", html)
