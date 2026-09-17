// Copyright 2026 Kuvexta. License AGPL-3.0-or-later.
// Execute the actual patch methods in Chrome with explicit dependency doubles.
// This does not test the Odoo asset loader, CDN availability or physical camera.
(async () => {
    const check = (condition, message) => { if (!condition) throw new Error(message); };
    const response = await fetch('/kt_ecommerce_barcode_search_patch/static/src/js/website_sale_barcode_patch.js');
    check(response.ok, 'actual patch source must be accessible');
    const source = (await response.text()).replace(/^import .*;\s*$/gm, '');
    const root = document.createElement('div');
    root.innerHTML = '<div id="barcode_id"></div><button class="kt_torch_toggle"></button>' +
        '<div id="barcodeModal"></div><div id="noProductModal"></div>';
    document.body.appendChild(root);
    const $ = (selector) => {
        const nodes = root.querySelectorAll(selector);
        const api = {length: nodes.length};
        for (const [method, action] of [['addClass', 'add'], ['removeClass', 'remove']]) {
            api[method] = (name) => { nodes.forEach(n => n.classList[action](name)); return api; };
        }
        api.toggleClass = (name, enabled) => { nodes.forEach(n => n.classList.toggle(name, enabled)); return api; };
        api.modal = (state) => { nodes.forEach(n => n.dataset.modal = state); return api; };
        return api;
    };
    let definition, resolveLibrary, config, detected, started = 0, stopped = 0, constraints;
    let rejectTorch = false, rpcResult = false, rpcCall;
    const track = {
        getCapabilities: () => ({torch: true}),
        applyConstraints: (value) => {
            constraints = value;
            return rejectTorch ? Promise.reject(new Error('simulated denial')) : Promise.resolve();
        },
    };
    const scanner = {
        init: (value, callback) => { config = value; callback(null); },
        start: () => { started++; }, stop: () => { stopped++; },
        onDetected: (callback) => { detected = callback; },
        CameraAccess: {getActiveTrack: () => track},
    };
    const widget = {prototype: {events: {'click .original': 'original'}}, include: (value) => { definition = value; }};
    const fakeWindow = {Quagga: scanner, location: {href: ''}};
    const loadJS = () => new Promise(resolve => { resolveLibrary = resolve; });
    const rpc = (url, params) => { rpcCall = {url, params}; return Promise.resolve(rpcResult); };
    new Function('publicWidget', 'loadJS', 'rpc', '$', 'navigator', 'document', 'Quagga', 'window', source)(
        {registry: {WebsiteSaleBarcode: widget}}, loadJS, rpc, $,
        {mediaDevices: {getUserMedia: () => {}}, hardwareConcurrency: 2}, document, scanner, fakeWindow
    );
    const instance = {...definition, _super: () => {}};
    instance.init();
    check(instance.events['click .original'] === 'original', 'preserve inherited events');
    instance.load_quagga();
    check(started === 0 && config === undefined, 'wait for library promise');
    resolveLibrary();
    await new Promise(resolve => setTimeout(resolve, 0));
    check(started === 1, 'start scanner after library loads');
    check(config.decoder.readers.includes('ean_reader') && config.decoder.readers.includes('code_128_reader'), 'reader formats');
    check(config.inputStream.constraints.video.facingMode.exact === 'environment', 'rear camera request');
    check(!root.querySelector('.kt_torch_toggle').classList.contains('d-none'), 'torch capability visible');
    detected({codeResult: {code: 'SYNTHETIC'}});
    await new Promise(resolve => setTimeout(resolve, 0));
    check(stopped === 1 && rpcCall.url === '/shop/barcode/product' && rpcCall.params.last_code === 'SYNTHETIC', 'detected code forwarded');
    check(root.querySelector('#barcodeModal').dataset.modal === 'hide', 'scanner modal hidden');
    check(root.querySelector('#noProductModal').dataset.modal === 'show', 'not-found feedback');
    rpcResult = {url: '/shop/synthetic?extra_param=true'};
    detected({codeResult: {code: 'SYNTHETIC'}});
    await new Promise(resolve => setTimeout(resolve, 0));
    check(fakeWindow.location.href === rpcResult.url, 'successful lookup redirect');
    instance.kt_toggle_torch();
    await new Promise(resolve => setTimeout(resolve, 0));
    check(instance.kt_torch_on && constraints.advanced[0].torch, 'torch enabled');
    rejectTorch = true;
    instance.kt_toggle_torch();
    await new Promise(resolve => setTimeout(resolve, 0));
    check(instance.kt_torch_on, 'failed torch request restores prior state');
    root.remove();
    console.log('test successful');
})().catch(error => console.error(error));
