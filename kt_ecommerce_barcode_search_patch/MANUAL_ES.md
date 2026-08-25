# Manual operativo — KT Ecommerce Barcode Search Patch

## Propósito y licencia

Correcciones Kuvexta sobre el addon externo `ecommerce_barcode_search` sin
modificar su código. Ambos se distribuyen bajo AGPL-3; el upstream se obtiene del
commit fijado en `UPSTREAM_SOURCES.json`, no se copia dentro de este repositorio.

## Instalación

1. Instale exactamente el upstream fijado y compruebe su huella.
2. Añada este repositorio al `addons_path`.
3. Instale `kt_ecommerce_barcode_search_patch`.
4. Actualice assets y pruebe con sesión anónima en un sitio de staging.

## Verificación

Pruebe código vacío, código inexistente, resultado único, formatos admitidos,
permiso/cancelación de cámara, carga lenta de la librería y linterna cuando el
dispositivo la soporte. La búsqueda de códigos alternos requiere el bridge
separado correspondiente; no se debe acoplar a Professional desde Community.

Código/manual: `Kuvexta/kuvexta-odoo-community@19.0`; FAQ y lecciones comunes:
`Kuvexta/kuvexta-odoo-knowledge`.
## Autoridad documental y mejora continua

- Código y operación de este addon: `Kuvexta/kuvexta-odoo-community@19.0`.
- Investigación, diseños, FAQ/PQR, incidentes y lecciones transversales:
  `Kuvexta/kuvexta-odoo-knowledge` mediante `INDEX.yaml` y `CATALOG.yaml`.
- Composición instalable y rollback: bundle exacto de
  `Kuvexta/kuvexta-odoo-integration`.

La copia retenida en Source es evidencia congelada. Toda mejora se propone aquí
y debe actualizar manual, pruebas y comprobante del árbol cuando corresponda.
Los ensayos externos aplicables no se consideran cerrados por una prueba local.
