Corrige y mejora el módulo ``ecommerce_barcode_search`` (Cybrosys
Techno Solutions, AGPL-3, incluido sin modificar en la carpeta
hermana ``ecommerce_barcode_search/`` de este mismo repositorio) —
**sin tocar ningún archivo del original**, usando los mecanismos
estándar de Odoo para extender otro módulo.

**Detalle completo de las 6 correcciones, con su causa real
verificada contra el código fuente:** ver ``PARCHE_KUVEXTA.md`` en
la raíz de este módulo.

**Instalar siempre junto con** ``ecommerce_barcode_search`` — nunca
uno sin el otro.

El módulo original de Cybrosys, tal como se descarga de su
repositorio público, tiene varios errores reales que impiden su
funcionamiento correcto — desde no funcionar en absoluto para
visitantes sin sesión, hasta fallar por completo con un error de
JavaScript en conexiones de celular más lentas. Este módulo corrige
todo eso, además de agregar un botón de linterna para escanear en
lugares con poca luz.

Resumen de las 6 correcciones (detalle completo en
``PARCHE_KUVEXTA.md``):

1. Ruta ``/shop/barcode/product``: acceso público, no solo usuarios
   con sesión iniciada.
2. Validación de código vacío + límite de un solo resultado (evita
   un error real de producción, "Expected singleton").
3. Más formatos de código de barras reconocidos (antes solo Code128,
   nunca reconocía EAN-13).
4. Tamaño de video correctamente definido (antes se veía como una
   franja diminuta).
5. Corrección de una condición de carrera al cargar la librería de
   escaneo (evita un error real, "Quagga is not defined").
6. Botón de linterna, solo visible en dispositivos que lo soportan.

Por qué dos módulos separados: así, si Cybrosys publica una
actualización de su módulo original en el futuro, se puede reemplazar
la carpeta ``ecommerce_barcode_search/`` completa sin perder ninguna
de estas correcciones.

Créditos del módulo original: ``ecommerce_barcode_search`` (el módulo
que este parche corrige) es de **Cybrosys Techno Solutions**,
licenciado AGPL-3.
https://github.com/CybroOdoo/CybroAddons/tree/19.0/ecommerce_barcode_search
