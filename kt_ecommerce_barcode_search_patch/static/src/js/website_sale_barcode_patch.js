/** @odoo-module **/
/**
 * Extiende (NO modifica) `publicWidget.registry.WebsiteSaleBarcode`
 * del módulo original `ecommerce_barcode_search` (Cybrosys), usando
 * `Class.include()` — el mecanismo estándar de Odoo para esto. El
 * archivo original (`WebsiteSaleBarcode.js`) permanece sin ningún
 * cambio; puede reemplazarse libremente con futuras actualizaciones
 * de Cybrosys.
 *
 * Nota técnica honesta: `init()` sí puede delegar limpiamente a
 * `this._super(...)` (solo se le agrega estado nuevo después). En
 * cambio, `load_quagga` necesita reescribirse casi por completo,
 * porque las correcciones (formatos de código, resolución de
 * cámara, localizador, detección de linterna) modifican valores que
 * están DENTRO del objeto de configuración que se le pasa a
 * `Quagga.init(...)` en el método original — JavaScript no permite
 * "meterse a mitad" de un objeto literal ya escrito en otra función
 * sin reescribir esa función completa. Es una limitación real, no
 * una elección de diseño.
 */
import publicWidget from "@web/legacy/js/public/public_widget";
import { loadJS } from "@web/core/assets";
import { rpc } from "@web/core/network/rpc";

const originalEvents = publicWidget.registry.WebsiteSaleBarcode.prototype.events;

publicWidget.registry.WebsiteSaleBarcode.include({
    // Se combina con los eventos originales — Class.include()
    // reemplazaría el objeto completo si no se hace así, perdiendo
    // el "click .o_wsale_apply_barcode" original.
    events: Object.assign({}, originalEvents, {
        "click .kt_torch_toggle": "kt_toggle_torch",
    }),

    init() {
        this._super(...arguments);
        // Estado propio de la linterna.
        this.kt_torch_on = false;
        // Se vuelve a pedir la carga del script (el original ya lo
        // hizo en su propio init() vía this._super(), pero sin
        // guardar la promesa) — cargar la MISMA URL una segunda vez
        // es inofensivo (el navegador la sirve de caché / no la
        // vuelve a descargar), y así sí tenemos la promesa propia
        // para esperarla correctamente en nuestro load_quagga.
        this.quaggaLoaded = loadJS(
            "https://cdn.jsdelivr.net/npm/@ericblade/quagga2@1.8.4/dist/quagga.min.js"
        );
    },

    load_quagga: function (ev) {
        var self = this;
        this.kt_torch_on = false;
        $(".kt_torch_toggle")
            .addClass("d-none")
            .removeClass("btn-warning")
            .addClass("btn-outline-secondary");

        this.quaggaLoaded.then(function () {
            if (
                $("#barcode_id").length > 0 &&
                navigator.mediaDevices &&
                typeof navigator.mediaDevices.getUserMedia === "function"
            ) {
                Quagga.init(
                    {
                        inputStream: {
                            name: "Live",
                            type: "LiveStream",
                            constraints: {
                                video: {
                                    facingMode: {
                                        exact: "environment",
                                    },
                                    width: { ideal: 1280 },
                                    height: { ideal: 720 },
                                },
                            },
                            numOfWorkers: navigator.hardwareConcurrency || 2,
                            target: document.querySelector("#barcode_id"),
                        },
                        decoder: {
                            readers: [
                                "ean_reader",
                                "ean_8_reader",
                                "code_128_reader",
                                "upc_reader",
                                "i2of5_reader",
                            ],
                        },
                        locator: {
                            patchSize: "medium",
                            halfSample: true,
                        },
                        locate: true,
                    },
                    function (err) {
                        if (err) {
                            console.log(err);
                            return;
                        }
                        Quagga.start();
                        var track = Quagga.CameraAccess.getActiveTrack();
                        if (track && typeof track.getCapabilities === "function") {
                            var capabilities = track.getCapabilities();
                            if (capabilities && capabilities.torch) {
                                $(".kt_torch_toggle").removeClass("d-none");
                            }
                        }
                    }
                );
                let last_result = [];
                Quagga.onDetected(function (result) {
                    let last_code = result.codeResult.code;
                    last_result.push(last_code);
                    last_result = [];
                    Quagga.stop();
                    rpc("/shop/barcode/product", { last_code: last_code }).then(function (result) {
                        $("#barcodeModal").modal("hide");
                        if (!result) {
                            $("#noProductModal").modal("show");
                        } else {
                            window.location.href = result["url"];
                        }
                    });
                });
            }
        });
    },

    kt_toggle_torch: function (ev) {
        var track = window.Quagga && Quagga.CameraAccess.getActiveTrack();
        if (!track) {
            return;
        }
        var self = this;
        this.kt_torch_on = !this.kt_torch_on;
        track
            .applyConstraints({ advanced: [{ torch: this.kt_torch_on }] })
            .then(function () {
                $(".kt_torch_toggle").toggleClass("btn-warning", self.kt_torch_on);
                $(".kt_torch_toggle").toggleClass("btn-outline-secondary", !self.kt_torch_on);
            })
            .catch(function (err) {
                console.log(err);
                self.kt_torch_on = !self.kt_torch_on;
            });
    },
});
