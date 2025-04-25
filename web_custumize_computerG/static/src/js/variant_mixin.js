odoo.define('web_custumize_computerG.VariantMixin', function (require) {
    'use strict';
     console.log("Custom VariantMixin loading...");
    var VariantMixin = require('sale.VariantMixin');
    var ajax = require('web.ajax');
    var session = require('web.session');

    // Ajout des méthodes personnalisées à VariantMixin
    VariantMixin._insertDelevryRemoteMessageDetailPage = function(productInfo) {
        if (productInfo.messageDelivryTimeRemoteStock) {
            $('#messageQty2').html(`<span>${productInfo.qty_available_wt} Pcs In Remote Stock</span>`);
            $('#messageDelevryTime2').html(`<span>${productInfo.messageDelivryTimeRemoteStock}</span>`);

            const $infoMessage = $('#informationQtyMessageDelivery2');
            const infoMessageEl = $infoMessage[0];
            if (infoMessageEl) {
                $infoMessage.removeClass('alert-success').addClass('alert-warning');
                infoMessageEl.style.setProperty('background', '#FFF0E8', 'important');
                infoMessageEl.style.setProperty('display', 'block', 'important');
                infoMessageEl.style.setProperty('color', '#803D19', 'important');
                infoMessageEl.style.setProperty('border', '1px solid #803D19', 'important');
                infoMessageEl.style.setProperty('font-weight', '500', 'important');
                infoMessageEl.style.setProperty('padding', '0.4rem', 'important');
                infoMessageEl.style.setProperty('width', 'fit-content', 'important');
                infoMessageEl.style.setProperty('border-radius', '0.2rem', 'important');
            }
        }
    };

    VariantMixin._insertDelevryMessageDetailPage = function(productInfo) {
        if (productInfo.messageDelivryTimeStock) {
            $('#messageQty1').html(`<span>${productInfo.virtual_available} Pcs In Stock</span>`);
            $('#messageDelevryTime1').html(`<span>${productInfo.messageDelivryTimeStock}</span>`);

            const $infoMessage = $('#informationQtyMessageDelivery1');
            const infoMessageEl = $infoMessage[0];
            if (infoMessageEl) {
                $infoMessage.removeClass('alert-warning').addClass('alert-success');
                infoMessageEl.style.setProperty('background', '#e5ffe978', 'important');
                infoMessageEl.style.setProperty('display', 'block', 'important');
                infoMessageEl.style.setProperty('color', '#067d24', 'important');
                infoMessageEl.style.setProperty('border', '1px solid #19a22f', 'important');
                infoMessageEl.style.setProperty('font-weight', '500', 'important');
                infoMessageEl.style.setProperty('padding', '0.4rem', 'important');
                infoMessageEl.style.setProperty('width', 'fit-content', 'important');
                infoMessageEl.style.setProperty('border-radius', '0.2rem', 'important');
            }
        }
    };

    VariantMixin._insertOutOfStockMessageDetailPage = function(productInfo, qty, continue_seling) {
        const $outOfStockMsg = $('#out_of_stock_message');
        if ($outOfStockMsg.length) {
            $outOfStockMsg.remove();
        }
        if (productInfo.out_of_stock_message) {
            if (continue_seling) {
                $('#messageQty3').html(`<span>${qty} Pcs</span>`);
            }
            $('#messageDelevryTime3').html(`<span class='cls-sahrane'>${productInfo.out_of_stock_message}</span>`);

            //update style delivery message
            const $infoMessage = $('#informationQtyMessageDelivery3');
            const infoMessageEl = $infoMessage[0];
            if (infoMessageEl) {
                $infoMessage
                    .removeClass('alert-success')
                    .addClass('alert-warning');
                infoMessageEl.removeAttribute('style');
                infoMessageEl.style.setProperty('background', '#fcf2f2', 'important');
                infoMessageEl.style.setProperty('display', 'block', 'important');
                infoMessageEl.style.setProperty('color', '#DA020E', 'important');
                infoMessageEl.style.setProperty('border', '1px solid #DA020E', 'important');
                infoMessageEl.style.setProperty('font-weight', '500', 'important');
                infoMessageEl.style.setProperty('padding', '0.4rem', 'important');
                infoMessageEl.style.setProperty('width', 'fit-content', 'important');
                infoMessageEl.style.setProperty('border-radius', '0.2rem', 'important');
            }
        }
    };

    // Surcharge de la méthode _getCombinationInfo
    var originalGetCombinationInfo = VariantMixin._getCombinationInfo;
    VariantMixin._getCombinationInfo = function(ev) {
        if ($(ev.target).hasClass('variant_custom_value')) {
            return Promise.resolve();
        }

        const $parent = $(ev.target).closest('.js_product');
        if (!$parent.length) {
            return Promise.resolve();
        }

        return originalGetCombinationInfo.apply(this, arguments).then(function(combinationData) {
            if (this._shouldIgnoreRpcResult()) {
                return;
            }

            const productId = this._getProductId($parent);
            var addQty = parseInt($parent.find('input[name="add_qty"]').val());

            return ajax.jsonRpc('/api/get_product_info', 'call', {
                product_id: productId,
            }).then((productInfo) => {
            const $infoMessage1 = $('#informationQtyMessageDelivery1');
            const $infoMessage2 = $('#informationQtyMessageDelivery2');
            const $infoMessage3 = $('#informationQtyMessageDelivery3');
            const infoMessageEl1 = $infoMessage1[0];
            const infoMessageEl2 = $infoMessage2[0];
            const infoMessageEl3 = $infoMessage3[0];

            const showDelivryMessage = productInfo.showDelivryMessage;
            const continue_seling = productInfo.continue_seling;
            const virtual_available_product_tmpl_id = productInfo.virtual_available_product_tmpl_id;
            if (virtual_available_product_tmpl_id > 0){
                var virtual_available = productInfo.virtual_available > 0 ? productInfo.virtual_available : 0;
            }
            else{
                var virtual_available = 0;
            }

            var qty_available_wt = 0;
            if (showDelivryMessage){
            var qty_available_wt = productInfo.qty_available_wt > 0 ? productInfo.qty_available_wt : 0;
           }
            const allQuantity = qty_available_wt + virtual_available

            if (addQty  >= allQuantity && !productInfo.continue_seling){
               const addToCartLink = document.querySelector('a.btn.btn-link.float_left.js_add_cart_json');
                    // Applique les styles pour le désactiver
                    if (addToCartLink) {
                        addToCartLink.style.pointerEvents = 'none';
                        addToCartLink.style.cursor = 'not-allowed';
                        // Optionnel : Ajouter un style visuel (grisé)
                        addToCartLink.style.opacity = '0.5';
                    }
                    if (addQty > allQuantity) {
                        $parent.find('input[name="add_qty"]').val(allQuantity);
                        addQty = allQuantity
                    }
            }
            else{
                    const addToCartLink = document.querySelector('a.btn.btn-link.float_left.js_add_cart_json');
                    // Applique les styles pour le désactiver
                    if (addToCartLink) {
                        addToCartLink.style.pointerEvents = 'auto';
                        addToCartLink.style.cursor = 'pointer';
                        addToCartLink.style.opacity = '1';
                    }
            }
            if (!productInfo) {
                $infoMessage.html(`<span/>`);
                return;
            }

            console.log('allQuantity', allQuantity)
            console.log('addQty', addQty)
            const qtyReset = addQty - (virtual_available + qty_available_wt);
            console.log('virtual_available', virtual_available)
            console.log('qty_available_wt', qty_available_wt)
            console.log('qtyReset', qtyReset)
            infoMessageEl1.style.setProperty('display', 'none', 'important');
            infoMessageEl2.style.setProperty('display', 'none', 'important');
            infoMessageEl3.style.setProperty('display', 'none', 'important');
            if (virtual_available > 0) {
                this._insertDelevryMessageDetailPage(productInfo);
                if (qty_available_wt > 0) {
                    this._insertDelevryRemoteMessageDetailPage(productInfo);
                    if (qtyReset > 0) {
                        this._insertOutOfStockMessageDetailPage(productInfo, qtyReset, continue_seling);
                    }
                }else if(addQty > virtual_available){
                    this._insertOutOfStockMessageDetailPage(productInfo, qtyReset, continue_seling);
                }
            }else if (qty_available_wt > 0 && virtual_available <= 0) {
                this._insertDelevryRemoteMessageDetailPage(productInfo);
                if (addQty > (virtual_available + qty_available_wt)) {
                    this._insertOutOfStockMessageDetailPage(productInfo, qtyReset, continue_seling);
                }
            }
            else {
                this._insertOutOfStockMessageDetailPage(productInfo, qtyReset, continue_seling);
            }
            });
        }.bind(this));
    };

    return VariantMixin;
});