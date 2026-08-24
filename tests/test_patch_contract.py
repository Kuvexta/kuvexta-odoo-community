from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "kt_ecommerce_barcode_search_patch"
CONTROLLER = ADDON / "controllers" / "web_product_qr_scan_patch.py"
MANIFEST = ADDON / "__manifest__.py"


class PatchContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.controller_source = CONTROLLER.read_text(encoding="utf-8")
        cls.controller_tree = ast.parse(cls.controller_source)
        cls.manifest = ast.literal_eval(MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_remains_agpl_and_depends_on_pinned_upstream(self):
        self.assertEqual(self.manifest.get("license"), "AGPL-3")
        self.assertIn("ecommerce_barcode_search", self.manifest.get("depends", []))

    def test_route_remains_public_jsonrpc(self):
        method = next(
            node
            for node in ast.walk(self.controller_tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "product_barcode"
        )
        route = next(
            decorator
            for decorator in method.decorator_list
            if isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Attribute)
            and decorator.func.attr == "route"
        )
        keywords = {kw.arg: ast.literal_eval(kw.value) for kw in route.keywords}
        self.assertEqual(keywords.get("auth"), "public")
        self.assertEqual(keywords.get("type"), "jsonrpc")
        self.assertTrue(keywords.get("website"))

    def test_empty_barcode_guard_precedes_request_access(self):
        source = self.controller_source
        guard = 'if not input_data:\n            return False'
        self.assertIn(guard, source)
        self.assertLess(source.index(guard), source.index('request.env["ir.http"]'))

    def test_product_search_is_bounded_to_one_record(self):
        calls = [node for node in ast.walk(self.controller_tree) if isinstance(node, ast.Call)]
        search_calls = [
            call
            for call in calls
            if isinstance(call.func, ast.Attribute) and call.func.attr == "search"
        ]
        self.assertTrue(search_calls, "Expected a product search call")
        self.assertTrue(
            any(
                any(
                    kw.arg == "limit"
                    and isinstance(kw.value, ast.Constant)
                    and kw.value.value == 1
                    for kw in call.keywords
                )
                for call in search_calls
            ),
            "Barcode product search must retain limit=1",
        )


if __name__ == "__main__":
    unittest.main()
