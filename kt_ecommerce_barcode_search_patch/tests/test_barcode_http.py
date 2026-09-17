# Copyright 2026 Kuvexta. License AGPL-3.0-or-later.
"""Original regression tests of the Kuvexta controller, not copied upstream."""
from unittest.mock import patch

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestBarcodePublicHttp(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.published = cls.env["product.product"].create({
            "name": "Kuvexta HTTP fixture published",
            "barcode": "KVX-HTTP-PUBLISHED",
            "sale_ok": True,
            "website_published": True,
        })
        cls.hidden = cls.env["product.product"].create({
            "name": "Kuvexta HTTP fixture hidden",
            "barcode": "KVX-HTTP-HIDDEN",
            "sale_ok": True,
            "website_published": False,
        })
        cls.not_for_sale = cls.env["product.product"].create({
            "name": "Kuvexta HTTP fixture not for sale",
            "barcode": "KVX-HTTP-NOT-FOR-SALE",
            "sale_ok": False,
            "website_published": True,
        })

    def setUp(self):
        super().setUp()
        self.authenticate(None, None)

    def barcode_request(self, params):
        response = self.url_open("/shop/barcode/product", json={
            "jsonrpc": "2.0", "method": "call", "id": 1, "params": params,
        })
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertNotIn("error", payload, payload)
        self.assertIn("result", payload)
        return payload["result"]

    def test_public_valid_barcode_redirects_to_expected_product(self):
        # No employee login and no mocked controller/ORM result.
        result = self.barcode_request({"last_code": self.published.barcode})
        slug = self.env["ir.http"]._slug(self.published.product_tmpl_id)
        self.assertEqual(result, {
            "type": "ir.actions.act_url", "url": f"/shop/{slug}?extra_param=true",
        })

    def test_missing_empty_and_null_barcode_return_false(self):
        for params in [{}, {"last_code": ""}, {"last_code": None}]:
            with self.subTest(params=params):
                self.assertIs(self.barcode_request(params), False)

    def test_unknown_barcode_returns_false(self):
        self.assertIs(self.barcode_request({"last_code": "KVX-HTTP-ABSENT"}), False)

    def test_unpublished_product_is_not_visible_to_public(self):
        self.assertIs(self.barcode_request({"last_code": self.hidden.barcode}), False)

    def test_product_not_for_sale_is_not_visible_to_public(self):
        self.assertIs(self.barcode_request({"last_code": self.not_for_sale.barcode}), False)

    def test_http_search_is_bounded_and_uses_public_user(self):
        product_class = type(self.env["product.product"])
        original_search = product_class.search
        observed = []

        def observe_search(records, domain, *args, **kwargs):
            if ("barcode", "=", self.published.barcode) in domain:
                observed.append((kwargs.get("limit"), records.env.user._is_public()))
            return original_search(records, domain, *args, **kwargs)

        # Observe the real ORM call, without bypassing record rules or fabricating
        # duplicate barcodes contrary to Odoo's constraints.
        with patch.object(product_class, "search", observe_search):
            self.barcode_request({"last_code": self.published.barcode})
        self.assertEqual(observed, [(1, True)])
