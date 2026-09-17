# Changelog — kt_ecommerce_barcode_search_patch

## Cobertura funcional — TASK-000066

* Añadidas pruebas originales HTTP anónimas y lógica JavaScript en Chrome con
  escáner/RPC simulados. Sin cambio de comportamiento del controlador ni de
  licencia. Casos, límites y ejecución en MANUAL_ES.md; estado real en PR/tarea.
* Se conserva el historial de migración y se registra un nuevo árbol de pruebas
  y documentación. La cámara física y la integración completa de assets no
  quedan acreditadas por los dobles del navegador.

## 19.0.1.0.3 (22/08/2026)

* Doc-only / gobierno: se corrige `PARCHE_KUVEXTA.md`, que todavía decía
  `LGPL-3` en su sección final aunque el manifest y la política ya habían
  sido alineados a `AGPL-3` en 19.0.1.0.2. El addon permanece `AGPL-3` por
  depender y extender directamente `ecommerce_barcode_search` de Cybrosys
  (AGPL-3). No cambia comportamiento funcional ni copyright upstream.

## 19.0.1.0.2 (21/08/2026)

* Corrección de gobierno/licencia: el manifest declaraba `LGPL-3` aunque el
  módulo extiende directamente `ecommerce_barcode_search` de Cybrosys,
  clasificado y distribuido como `AGPL-3`. Se alinea el addon Kuvexta a
  `AGPL-3`, coherente con `MODULE_POLICY.json` (`derived_agpl`) y con la
  arquitectura Community. No cambia comportamiento funcional.
* Se añade nota explícita de copyright Kuvexta sin alterar ni sustituir el
  copyright del módulo upstream de Cybrosys.

## 19.0.1.0.1 (15/08/2026)

* Doc-only: se estandarizó `README.rst` al patrón de carpeta `readme/`
  (`DESCRIPTION.rst`, `CONFIGURE.rst`, `USAGE.rst`) que usa el resto
  del repositorio, en vez de un `README.rst` autocontenido. Sin
  cambios de comportamiento.

## 19.0.1.0.0 (03/08/2026)

**Primera versión.** Parche de la Opción B (`ecommerce_barcode_search`,
Cybrosys AGPL-3) sin modificar el módulo original — 6 correcciones reales
aplicadas aparte: autenticación pública, condición de carrera, formatos
de código ampliados, control de linterna, entre otras (ver
`PARCHE_KUVEXTA.md` para el detalle exacto de cada bug y su fix).
Preferir `kt_camera_scan_website` (Opción A) para instalaciones nuevas —
ver `docs/COMPARATIVA_ESCANEO_CAMARA.md`.
