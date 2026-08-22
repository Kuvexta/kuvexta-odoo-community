# -*- coding: utf-8 -*-
"""
Hereda `WebsiteProductBarcode` del módulo original
(`ecommerce_barcode_search`, Cybrosys) SIN modificar ningún archivo
de ese módulo — el original se puede reemplazar/actualizar
libremente en el futuro sin perder estas correcciones.

Nota técnica honesta: a diferencia de un parche de JavaScript (donde
`Class.include()` permite envolver solo una parte de la lógica y
llamar a `this._super()` para el resto), un método de controlador con
`@http.route` decorado de nuevo REEMPLAZA la ruta completa — Python no
permite "insertar" una corrección a mitad de un método heredado sin
volver a escribirlo completo. Por eso el cuerpo de `product_barcode`
se repite aquí casi entero — es una limitación real de cómo funciona
la herencia de controladores en Odoo, no una elección de diseño.
El archivo ORIGINAL sigue sin tocarse en absoluto.
"""
from odoo import http
from odoo.addons.ecommerce_barcode_search.controllers.web_product_qr_scan import (
    WebsiteProductBarcode,
)
from odoo.http import request


class KtWebsiteProductBarcodePatch(WebsiteProductBarcode):

    @http.route(
        ["/shop/barcode/product"],
        type="jsonrpc",
        auth="public",
        website=True,
        methods=["GET", "POST"],
    )
    def product_barcode(self, **kwargs):
        """Corrección Kuvexta (01-02/08/2026) — dos cambios reales
        sobre el original:
        1. `auth="public"` en vez de `"user"` — funciona también para
           visitantes que no iniciaron sesión (la mayoría en una
           tienda pública).
        2. Validación de código vacío + `limit=1` — evita el error
           real "Expected singleton" encontrado en producción cuando
           la cámara mandaba un valor vacío antes de detectar algo, y
           varios productos coincidían con `barcode` vacío."""
        input_data = kwargs.get("last_code")
        if not input_data:
            return False
        slug = request.env["ir.http"]._slug
        barcode_product = request.env["product.product"].search(
            [("barcode", "=", input_data)], limit=1
        )
        request.session["barcode"] = input_data
        request.session["barcode_product"] = barcode_product.id
        if barcode_product:
            return {
                "type": "ir.actions.act_url",
                "url": "/shop/%s?extra_param=true"
                % slug(barcode_product.product_tmpl_id),
            }
        return False
