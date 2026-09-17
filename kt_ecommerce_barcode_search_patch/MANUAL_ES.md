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

## Pruebas automatizadas del comportamiento (TASK-000066)

Pruebas originales Kuvexta bajo AGPL-3, sin copiar tests upstream. Se ejecutan
como `post_install`, excluyendo `at_install`, en el paquete `tests` del addon.
Community es propietario de los casos; Integration los ejecuta con el Odoo y
dependencias fijados. Los cuatro contratos AST/texto del repositorio permanecen
como un control diferente: no sustituyen HTTP ni navegador.

| Comportamiento existente / fuente | Prueba | Resultado esperado |
|---|---|---|
| Ruta pública y acción del controlador | POST JSON-RPC anónimo, producto publicado sintético | Acción act_url con slug del producto y extra_param=true, sin login |
| Guardia de entrada vacía | Parámetro ausente, cadena vacía y null | False, sin error JSON-RPC |
| Sin coincidencia | Código sintético inexistente | False |
| Visibilidad de website_sale | Productos sin publicar o no vendibles | No visibles para usuario público, conforme a ir_rules.xml del Odoo fijado |
| Búsqueda limitada | Petición HTTP real, observación del ORM sin sustituir su resultado | limit=1 y usuario público; no se eluden restricciones creando códigos duplicados inválidos |
| Carga asíncrona JS | Chrome con promesa Quagga controlada | No inicializa antes de resolver la promesa |
| Detección/feedback | Métodos JS reales, dobles de Quagga/RPC | Código reenviado, modal cerrado, feedback sin producto o URL devuelta |
| Linterna | Track simulado con permiso aceptado/rechazado | Aplica restricción y restaura estado al rechazar |

No se inventa un contrato para objetos/listas no vacíos enviados como código:
el controlador no define validación de tipos para esas entradas. Multiwebsite,
políticas adicionales de visibilidad y dispositivos reales necesitan casos y
evidencias específicos; esta matriz no sustituye decisiones de seguridad.

### Ejecución aislada

Requisitos: entorno efímero de Integration con PostgreSQL, Odoo del lock,
Community candidato o integrado y upstream exacto de `UPSTREAM_SOURCES.json`.
No usa bases reales. Desde la raíz de Integration, tras preparar ese entorno:

```bash
python3 scripts/run_odoo_stack_smoke.py --workspace .stack-workspace --profile community
```

El selector `/kt_ecommerce_barcode_search_patch` descubre las pruebas del addon.
Los logs deben nombrar `TestBarcodePublicHttp` y `TestBarcodeBrowser`, mostrar
su ejecución y un resumen sin fallos. Un skip de navegador no acredita Chrome.
Los SHA y ejecuciones realmente comprobados se registran en PR/tarea; esta
instrucción no declara de antemano la suite exitosa. La ejecución crea config/log
y base efímera del perfil; no ejecutarla sobre staging/producción ni copiar la
configuración con contraseña a Git.

El test de navegador usa Chrome real y carga el archivo JS real, pero inyecta
dependencias de widget, cargador, RPC y escáner. Comprueba lógica en navegador;
**no** acredita ensamblado completo de assets Odoo, CDN, Bootstrap, Quagga real,
permiso de cámara, lectura óptica, linterna física ni dispositivo. No contacta
el CDN ni requiere cámara. HTTP se verifica separadamente con peticiones reales.

### Mantenimiento y recuperación

No hay instalación adicional para los tests: viajan en el addon, se habilitan
solo en el entorno de pruebas. Mantener casos y manual junto al controlador;
actualizar el recibo de árbol desde Git sin alterar recibos históricos. Para
retirar o corregir pruebas, PR aditivo revisado; no cambiar expectativas para
ocultar defectos. No borrar ni restaurar bases como efecto de este procedimiento.
Un candidato probado no está integrado hasta que el lock institucional incluya
su merge. El estado de ese paso se consulta en Coordination, no en este manual.

## Autoridad documental y mejora continua

- Código y operación de este addon: `Kuvexta/kuvexta-odoo-community@19.0`.
- Investigación, diseños, FAQ/PQR, incidentes y lecciones transversales:
  `Kuvexta/kuvexta-odoo-knowledge` mediante `INDEX.yaml` y `CATALOG.yaml`.
- Composición instalable y rollback: bundle exacto de
  `Kuvexta/kuvexta-odoo-integration`.

La copia retenida en Source es evidencia congelada. Toda mejora se propone aquí
y debe actualizar manual, pruebas y comprobante del árbol cuando corresponda.
Los ensayos externos aplicables no se consideran cerrados por una prueba local.
