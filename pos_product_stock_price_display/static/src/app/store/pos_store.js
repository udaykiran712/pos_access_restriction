/** @odoo-module */
/* -*- coding: utf-8 -*- */
/* Part of Odoo. See LICENSE file for full copyright and licensing details. */
/**
 * ---------------------------------------------------------------------------
 *
 *  File: static/src/app/store/pos_store.js
 *
 *  Purpose
 *  -------
 *  Strict Out-of-Stock Sale Blocker.
 *
 *  Prevents cashiers from adding a storable product to the current order
 *  once its location-specific stock on hand (``pos_location_qty``,
 *  populated server-side by Feature 2) is exhausted, or once adding the
 *  requested quantity would push the cart past what is actually
 *  available at the active POS's source stock location.
 *
 *  Why patch `PosStore.addLineToCurrentOrder`
 *  --------------------------------------------
 *  `PosStore.prototype.addLineToCurrentOrder` is the single, canonical
 *  entry point every product-addition workflow in Odoo 18 POS funnels
 *  through, regardless of how the cashier triggered it:
 *    - Tapping a ProductCard tile in the product grid.
 *    - Scanning a barcode.
 *    - Selecting a product from the search bar.
 *
 *  Patching this one method therefore creates a single, airtight
 *  validation barrier across every input vector, with no risk of a
 *  workflow silently bypassing the check. When validation fails, this
 *  patch shows a blocking `AlertDialog` and returns *without* calling
 *  `super.addLineToCurrentOrder()`, which aborts line creation entirely
 *  - the product is never added to the order.
 *
 *  Business rules enforced (in order)
 *  -------------------------------------
 *  1. Non-storable bypass: services and consumables are never stock
 *     tracked, so validation is skipped entirely for them.
 *  2. Refund / return protection: validation only applies when the
 *     quantity being added is strictly positive. Negative quantities
 *     (refunds/returns) are always allowed through, even at zero stock.
 *  3. Condition A - Out of Stock: if the location's available stock is
 *     zero or negative, block immediately.
 *  4. Condition B - Insufficient Stock: if the quantity already in the
 *     cart for this product, plus the quantity being added, would
 *     exceed the available stock, block and inform the cashier exactly
 *     how many units are available and how many they already hold.
 *
 *  Note on imports
 *  -----------------
 *  `this.dialog` (the `dialog` service) is already initialized by the
 *  native `PosStore.prototype.setup()` (via `useService("dialog")`), and
 *  remains available on `this` after that `setup()` runs. This patch
 *  therefore reads `this.dialog` directly rather than importing
 *  `useService` from `@web/core/utils/hooks` a second time, avoiding a
 *  redundant service lookup.
 */

import {patch} from "@web/core/utils/patch";
import {AlertDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {_t} from "@web/core/l10n/translation";
import {PosStore} from "@point_of_sale/app/store/pos_store";

/**
 * Patch `PosStore.prototype` to intercept every product addition and
 * enforce location-specific stock availability before the line is ever
 * created.
 *
 * @see PosStore - The global, reactive Point of Sale store/state
 *      container. `addLineToCurrentOrder` is its single canonical entry
 *      point for adding an order line, regardless of trigger source
 *      (product grid, barcode scanner, or search bar).
 */
patch(PosStore.prototype, {
    /**
     * Validate location-specific stock availability before delegating to
     * the native line-creation logic.
     *
     * @override
     * @param {Object} vals - Order line values for the line about to be
     *      created. Expected to include:
     *        - product_id {Object}: the `product.product` record being
     *          added, including `is_storable` and `pos_location_qty`
     *          (the latter populated server-side by this module's
     *          Feature 2 `product.product` override).
     *        - qty {number}: the quantity being added by this call. May
     *          be negative for refunds/returns, or omitted (defaults to
     *          `1`) for a simple tap/scan addition.
     * @param {Object} [opts={}] - Additional native options forwarded
     *      unmodified to `super.addLineToCurrentOrder()` when
     *      validation passes.
     * @param {boolean} [configure=true] - Native flag controlling
     *      whether product configuration (attributes, etc.) runs;
     *      forwarded unmodified to `super.addLineToCurrentOrder()` when
     *      validation passes.
     * @returns {Promise<*>|undefined} The native method's return value
     *      when validation passes and the line is created; `undefined`
     *      (with no line created) when validation fails and a blocking
     *      dialog is shown instead.
     */
    async addLineToCurrentOrder(vals, opts = {}, configure = true) {
        const product = vals.product_id;

        // Rule 1 - Non-storable bypass: services and consumables are
        // never inventory-tracked, so they are always allowed through.
        if (product && product.is_storable) {
            const addedQty = vals.qty ?? 1;

            // Rule 2 - Refund / return protection: only validate when
            // the quantity being added is strictly positive. Negative
            // quantities (refunds/returns) must never be blocked, even
            // when the location has zero stock.
            if (addedQty > 0) {
                const order = this.get_order();
                const orderLines = (order && order.lines) || [];

                // Cart Aggregation: sum quantities across every existing
                // line for this same product (handles split orderlines,
                // e.g. distinct lines created by different discounts or
                // notes on the same product).
                const currentCartQty = orderLines
                    .filter((line) => line.product_id && line.product_id.id === product.id)
                    .reduce((total, line) => total + line.qty, 0);

                const availableStock = product.pos_location_qty ?? 0;

                // Condition A - Zero / Negative Stock.
                if (availableStock <= 0) {
                    this.dialog.add(AlertDialog, {
                        title: _t("Out of Stock"),
                        body: _t("This product is out of stock in this POS location."),
                    });
                    return;
                }

                // Condition B - Exceeds Available Stock.
                if (currentCartQty + addedQty > availableStock) {
                    this.dialog.add(AlertDialog, {
                        title: _t("Insufficient Stock"),
                        body: _t(
                            "Only %s unit(s) available in this location. You already have %s in your cart.",
                            availableStock,
                            currentCartQty
                        ),
                    });
                    return;
                }
            }
        }

        return await super.addLineToCurrentOrder(vals, opts, configure);
    },
});