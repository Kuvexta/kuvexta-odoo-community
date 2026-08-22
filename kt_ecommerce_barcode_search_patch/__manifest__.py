# -*- coding: utf-8 -*-
# Copyright 2026 Kuvexta
# This addon extends ecommerce_barcode_search (Cybrosys, AGPL-3) and is
# distributed under AGPL-3. Upstream Cybrosys copyright remains unchanged.
{
    "name": "KT Ecommerce Barcode Search - Parches Kuvexta",
    "summary": "Correcciones y mejoras sobre ecommerce_barcode_search (Cybrosys), sin modificar el módulo original",
    "description": """
Este módulo NO modifica ningún archivo de `ecommerce_barcode_search`
(Cybrosys, AGPL-3) — lo extiende usando los mecanismos estándar de
Odoo para esto (herencia de controlador, `Class.include()` en
JavaScript, herencia de vista XML), para que las actualizaciones
futuras del módulo original de Cybrosys se puedan aplicar libremente
sin perder ninguna de estas correcciones.

Correcciones y mejoras incluidas (ver README.md para el detalle
completo de cada una):

1. Ruta `/shop/barcode/product`: auth pública en vez de solo
   usuarios autenticados.
2. Validación de código vacío + límite de un solo resultado (evita
   el error real "Expected singleton" encontrado en producción).
3. Más formatos de código de barras reconocidos (antes solo Code128).
4. Resolución de cámara y ajustes de detección mejorados.
5. Tamaño de video correctamente definido (antes se veía como una
   franja diminuta).
6. Corrección de una condición de carrera al cargar la librería de
   escaneo (evita el error real "Quagga is not defined").
7. Botón de linterna (encendido/apagado), solo visible en
   dispositivos que lo soportan.
8. Búsqueda por código de barras alterno conectada de forma nativa
   con `kt_product_multi_barcode` (vía el módulo puente
   `kt_multi_barcode_website_sale`, instalado por separado).
    """,
    "version": "19.0.1.0.3",
    "category": "Website/Website",
    "author": "Kuvexta",
    "website": "https://kuvexta.com",
    "license": "AGPL-3",
    "depends": [
        "ecommerce_barcode_search",
    ],
    "data": [
        "views/website_sale_template_patch.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "kt_ecommerce_barcode_search_patch/static/src/css/barcode_scan.css",
            "kt_ecommerce_barcode_search_patch/static/src/js/website_sale_barcode_patch.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
