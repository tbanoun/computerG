odoo.define('web_custumize_computerG.VariantMixin', function (require) {
    'use strict';
    console.log("Custom VariantMixin loading...");
    var VariantMixin = require('sale.VariantMixin');
    var ajax = require('web.ajax');
    var session = require('web.session');

    // Ajout des méthodes personnalisées à VariantMixin
    VariantMixin._insertDelevryRemoteMessageDetailPage = function(productInfo) {
        if (productInfo.messageDelivryTimeRemoteStock) {
            if (productInfo.show_qty) {
                $('#messageQty2').html(`<span>${productInfo.qty_available_wt} Units in Remote Stock |</span>`);
            }

            $('#messageDelevryTime2').html(`<span>${productInfo.messageDelivryTimeRemoteStock}</span>`);

            const $infoMessage = $('#informationQtyMessageDelivery2');
            const infoMessageEl = $infoMessage[0];
            if (infoMessageEl) {
                $infoMessage.removeClass('alert-success').addClass('alert-warning');
                infoMessageEl.style.setProperty('font-family', "'Poppins', sans-serif", 'important');
                infoMessageEl.style.setProperty('font-weight', '500', 'important');
                infoMessageEl.style.setProperty('background', 'rgba(246, 242, 250, 0.5)', 'important');
                infoMessageEl.style.setProperty('padding', '0.4rem 0.6rem', 'important');
//                infoMessageEl.style.setProperty('width', 'fit-content', 'important');
                infoMessageEl.style.setProperty('width', '500px', 'important');
                infoMessageEl.style.setProperty('border-radius', '4px', 'important');
                infoMessageEl.style.setProperty('color', '#6F1152', 'important');
                infoMessageEl.style.setProperty('font-size', '10pt', 'important');
                infoMessageEl.style.setProperty('border', '0.5px solid #6F1152', 'important');
                infoMessageEl.style.setProperty('display', 'block', 'important');
            }
        }
    };

    VariantMixin._insertDelevryMessageDetailPage = function(productInfo) {
        if (productInfo.messageDelivryTimeStock) {
            if (productInfo.show_qty) {
                $('#messageQty1').html(`<span>${productInfo.virtual_available} Units in Stock |</span>`);
            }
            $('#messageDelevryTime1').html(`<span>${productInfo.messageDelivryTimeStock}</span>`);

            const $infoMessage = $('#informationQtyMessageDelivery1');
            const infoMessageEl = $infoMessage[0];if (infoMessageEl) {
                $infoMessage.removeClass('alert-warning').addClass('alert-success');
                infoMessageEl.style.setProperty('font-family', "'Poppins', sans-serif", 'important');
                infoMessageEl.style.setProperty('font-weight', '500', 'important');
                infoMessageEl.style.setProperty('background', 'rgba(242, 250, 246, 0.5)', 'important'); // F2FAF6 avec 50% d'opacité
                infoMessageEl.style.setProperty('padding', '0.4rem 0.6rem', 'important');
//                infoMessageEl.style.setProperty('width', 'fit-content', 'important');
infoMessageEl.style.setProperty('width', '500px', 'important');
                infoMessageEl.style.setProperty('border-radius', '4px', 'important');
                infoMessageEl.style.setProperty('color', '#116F41', 'important');
                infoMessageEl.style.setProperty('font-size', '10pt', 'important');
                infoMessageEl.style.setProperty('border', '0.5px solid #116F41', 'important');
                infoMessageEl.style.setProperty('display', 'block', 'important');
            }
        }
    };

    VariantMixin._insertOutOfStockMessageDetailPage = function(productInfo, qty, continue_seling) {
        if (productInfo.out_of_stock_message) {
            if (continue_seling) {
                if (productInfo.show_qty) {
                    console.log('qty', qty)
                }
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
                infoMessageEl.style.setProperty('font-family', "'Poppins', sans-serif", 'important');
                infoMessageEl.style.setProperty('font-weight', '600', 'important'); // Poppins Semi Bold
                infoMessageEl.style.setProperty('background', 'rgba(255, 232, 238, 0.5)', 'important'); // #FFFCEE avec 50% opacité
                infoMessageEl.style.setProperty('padding', '0.4rem 0.6rem', 'important');
//                infoMessageEl.style.setProperty('width', 'fit-content', 'important');
                infoMessageEl.style.setProperty('width', '500px', 'important');
                infoMessageEl.style.setProperty('border-radius', '4px', 'important');
                infoMessageEl.style.setProperty('color', '#F45454', 'important');
                infoMessageEl.style.setProperty('font-size', '10pt', 'important');
                infoMessageEl.style.setProperty('border', '0.5px solid #F45454', 'important');
                infoMessageEl.style.setProperty('display', 'block', 'important');
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
            }).then(function(productInfo) {
                const $infoMessage1 = $('#informationQtyMessageDelivery1');
                const $infoMessage2 = $('#informationQtyMessageDelivery2');
                const $infoMessage3 = $('#informationQtyMessageDelivery3');
                const infoMessageEl1 = $infoMessage1[0];
                const infoMessageEl2 = $infoMessage2[0];
                const infoMessageEl3 = $infoMessage3[0];

                const showDelivryMessage = productInfo.showDelivryMessage;
                const continue_seling = productInfo.continue_seling;
                const virtual_available_product_tmpl_id = productInfo.virtual_available_product_tmpl_id;

                var virtual_available;
                if (virtual_available_product_tmpl_id > 0) {
                    virtual_available = productInfo.virtual_available > 0 ? productInfo.virtual_available : 0;
                } else {
                    virtual_available = 0;
                }

                var qty_available_wt = 0;
                if (showDelivryMessage) {
                    qty_available_wt = productInfo.qty_available_wt > 0 ? productInfo.qty_available_wt : 0;
                }
                const allQuantity = qty_available_wt + virtual_available;

                if (addQty >= allQuantity && !productInfo.continue_seling) {
                    const addToCartLink = document.querySelector('a.btn.btn-link.float_left.js_add_cart_json');
                    if (addToCartLink) {
                        addToCartLink.style.pointerEvents = 'none';
                        addToCartLink.style.cursor = 'not-allowed';
                        addToCartLink.style.opacity = '0.5';
                    }
                    if (addQty > allQuantity) {
                        $parent.find('input[name="add_qty"]').val(allQuantity);
                        addQty = allQuantity;
                    }
                } else {
                    const addToCartLink = document.querySelector('a.btn.btn-link.float_left.js_add_cart_json');
                    if (addToCartLink) {
                        addToCartLink.style.pointerEvents = 'auto';
                        addToCartLink.style.cursor = 'pointer';
                        addToCartLink.style.opacity = '1';
                    }
                }

                if (!productInfo) {
                    $infoMessage1.html(`<span/>`);
                    return;
                }

                const $outOfStockMsg = $('#out_of_stock_message');
                const $threshold_message = $('#threshold_message');

                if ($outOfStockMsg.length) {
                    $outOfStockMsg.hide();
                }
                if ($threshold_message.length) {
                    $threshold_message.hide();
                }

                const qtyReset = addQty - (virtual_available + qty_available_wt);

                infoMessageEl1.style.setProperty('display', 'none', 'important');
                infoMessageEl2.style.setProperty('display', 'none', 'important');
                infoMessageEl3.style.setProperty('display', 'none', 'important');

                if (virtual_available > 0) {
                    this._insertDelevryMessageDetailPage(productInfo);
                } else if (qty_available_wt > 0 && virtual_available <= 0) {
                    this._insertDelevryRemoteMessageDetailPage(productInfo);
                } else {
                    this._insertOutOfStockMessageDetailPage(productInfo, qtyReset, continue_seling);
                }
            }.bind(this));
        }.bind(this));
    };

    return VariantMixin;
});