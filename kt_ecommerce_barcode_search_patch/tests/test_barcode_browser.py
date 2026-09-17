# Copyright 2026 Kuvexta. License AGPL-3.0-or-later.
from pathlib import Path

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestBarcodeBrowser(HttpCase):
    def test_patch_javascript_with_simulated_scanner(self):
        """Real headless browser; injected scanner/RPC are not physical hardware."""
        code = Path(__file__).with_name("browser_barcode_patch.js").read_text(encoding="utf-8")
        self.browser_js("/web/login", code, ready="document.readyState === 'complete'", timeout=90)
