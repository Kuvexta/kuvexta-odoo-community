# Parche Kuvexta — `ecommerce_barcode_search`

> **Estado (06/08/2026):** opción **B (legada)**. La opción **A
> recomendada** para tienda/web pública es
> [`kt_camera_scan_website`](../kt_camera_scan_website/) (motor
> `kt_camera_scan_widget`, sin Quagga/CDN). Ver
> [`docs/COMPARATIVA_ESCANEO_CAMARA.md`](../docs/COMPARATIVA_ESCANEO_CAMARA.md).
> Puede mantener este parche solo mientras migra; con A instalado el
> botón de Cybrosys se oculta para no duplicar.

Este módulo (`kt_ecommerce_barcode_search_patch`) corrige y mejora el
módulo `ecommerce_barcode_search` de **Cybrosys Techno Solutions**
(licencia **AGPL-3**, sin relación de autoría con Kuvexta) **sin
modificar ningún archivo del original** — usando los mecanismos
estándar de Odoo para extender otro módulo (herencia de controlador,
`Class.include()` en JavaScript, herencia de vista XML).

**Fuente original, sin tocar:** `CybroOdoo/CybroAddons`, rama `19.0`,
carpeta `ecommerce_barcode_search/` — incluida sin ninguna
modificación en este mismo repositorio, en la carpeta hermana
`ecommerce_barcode_search/`.
https://github.com/CybroOdoo/CybroAddons/tree/19.0/ecommerce_barcode_search

**Por qué dos módulos separados, en vez de modificar el original
directamente:** así, si Cybrosys publica una actualización futura de
su módulo, se puede reemplazar la carpeta `ecommerce_barcode_search/`
completa sin perder ninguna de estas correcciones — quedan aplicadas
por encima, de forma independiente.

---

## Las 6 correcciones, con su causa real

### 1. `auth="user"` → `auth="public"`

**Archivo:** `controllers/web_product_qr_scan_patch.py`

Con `auth="user"`, la búsqueda por código de barras desde la cámara
solo funcionaba para visitantes que ya iniciaron sesión en el
sitio — en una tienda en línea abierta al público, la gran mayoría
de clientes navegan **sin haber iniciado sesión**. Sin este cambio,
la función prácticamente no serviría para el caso de uso real.

### 2. Validar código vacío + `limit=1`

**Archivo:** `controllers/web_product_qr_scan_patch.py`

**Error real encontrado en producción:**
```
ValueError: Expected singleton: product.product(63, 3, 49, 22, ...)
```

**Causa:** el original llamaba a `search()` **sin `limit=1`** — si el
código coincidía con más de un producto (ej. varios con `barcode`
vacío en la base de datos), el resultado era un recordset de VARIOS
registros, y `.id` sobre varios registros a la vez lanza justo este
error. Además, no había ninguna validación de que el código detectado
no viniera vacío — si la cámara mandaba un valor vacío antes de
detectar algo real, el código buscaba literalmente `barcode = ''`,
coincidiendo con múltiples productos con el código de barras vacío.

**Corrección:** validación temprana (si `input_data` está vacío, no
se busca nada) + `limit=1` en la búsqueda.

### 3. Formatos de código de barras ampliados

**Archivo:** `static/src/js/website_sale_barcode_patch.js`

**Problema real reportado:** "la cámara es muy difícil que detecte
el código de barras" — la causa no era la cámara ni la iluminación:
la configuración original de Quagga2 solo tenía activado el lector
**Code128**:
```js
decoder: { readers: ["code_128_reader"] }
```
La gran mayoría de productos reales usan códigos **EAN-13** — con la
configuración original, esos códigos nunca podían detectarse.

**Corrección:** se amplió `readers` a `ean_reader` (EAN-13),
`ean_8_reader` (EAN-8), `code_128_reader` (se mantiene), `upc_reader`
(UPC-A), e `i2of5_reader` (ITF-14). También se agregó resolución de
cámara explícita (1280x720) y ajustes del localizador
(`patchSize`, `halfSample`) — mejoran la detección real en
condiciones normales de cámara de celular.

**Limitación que no se puede corregir con configuración:** Quagga2
es una librería de códigos **lineales únicamente** — nunca podrá leer
QR ni GS1-DataMatrix, sin importar el ajuste.

### 4. Contenedor de video sin tamaño definido

**Archivo nuevo:** `static/src/css/barcode_scan.css` (no existía
ningún CSS propio en el módulo original)

El contenedor `#barcode_id` no tenía ningún tamaño definido — Quagga2
inyecta el `<video>`/`<canvas>` con el tamaño que resulte de la
resolución de cámara, sin que el contenedor los restrinja. Esto se
veía como una franja diminuta e inutilizable, a veces cortada por el
borde de la pantalla.

**Corrección:** alto fijo y responsivo (usando `min()` de CSS para
nunca exceder el alto disponible de pantalla), video/canvas
posicionados absolutos llenando el 100% del contenedor con
`object-fit: cover`, y scroll de respaldo en el cuerpo del modal por
si aún así no cabe en una pantalla muy pequeña.

### 5. Condición de carrera al cargar Quagga2

**Archivo:** `static/src/js/website_sale_barcode_patch.js`

**Error real reportado en producción:**
```
ReferenceError: Quagga is not defined
```

**Causa:** el original disparaba la carga del script de Quagga2 sin
esperar a que terminara — si el usuario hacía clic en "Escanear
código" antes de que el navegador terminara de descargar el script
desde el CDN (más probable en conexiones de celular más lentas),
`Quagga` todavía no existía como variable global.

**Corrección:** se guarda la promesa que devuelve `loadJS()` (en vez
de solo dispararla), y `load_quagga` espera esa promesa antes de
tocar `Quagga` para cualquier cosa.

### 6. Botón de linterna

**Archivos:** `views/website_sale_template_patch.xml` (agrega el
botón vía herencia de vista) + `static/src/js/website_sale_barcode_patch.js`
(la lógica)

El módulo original no traía ninguna forma de encender el flash de la
cámara al escanear en lugares con poca luz — Quagga2 tampoco lo trae
integrado de fábrica.

**Implementado:** botón en el pie del modal de escaneo, **oculto por
defecto** — solo se muestra si el dispositivo realmente soporta
encender el flash (se detecta con `track.getCapabilities().torch`
justo después de iniciar la cámara). Usa
`track.applyConstraints({advanced: [{torch: true/false}]})` — la API
real del navegador para esto. El mismo botón alterna entre encender y
apagar (no son dos botones separados).

---

## Requisitos

- Módulo `website_sale` (Ventas en línea / e-commerce) instalado y
  activo.
- Conexión a internet del **navegador del cliente** (no del
  servidor) — la librería de escaneo (Quagga2) se carga dinámicamente
  desde un CDN público (`cdn.jsdelivr.net`), sin necesitar ninguna
  instalación en el servidor.

## Confirmado funcionando con datos reales

Probado en producción (`nexoferretero.com`) — detección de códigos
EAN-13 reales, linterna encendiendo/apagando correctamente en
dispositivos compatibles, sin ninguno de los 3 errores reales
documentados arriba (los 2 primeros del controlador, el tercero de
JavaScript) volviendo a aparecer tras las correcciones.

## Licencia

El código del parche mantenido por Kuvexta en
`kt_ecommerce_barcode_search_patch` se distribuye bajo **AGPL-3**.
Depende y extiende directamente `ecommerce_barcode_search` de Cybrosys,
que también permanece bajo **AGPL-3**. El copyright y la licencia del
módulo original de Cybrosys no se modifican ni se sustituyen.
