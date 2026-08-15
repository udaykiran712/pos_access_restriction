/** @odoo-module */
/* -*- coding: utf-8 -*- */
/* Part of Odoo. See LICENSE file for full copyright and licensing details. */
/**
 *
 *  File: static/src/app/generic_components/product_card/product_card.js
 *
 *  Purpose
 *  -------
 *  dynamically display the sales price of each product on its
 *  Point of Sale ProductCard (``formattedPrice``).
 *
 *  dynamically display the real-time, location-specific stock
 *  on hand for storable products (``stockQty`` / ``formattedStockQty`` /
 *  ``stockStatusClass`` / ``isStorable``).
 *
 *  This file non-destructively patches the core
 *  `point_of_sale.ProductCard` OWL 2 component (defined in
 *  `@point_of_sale/app/generic_components/product_card/product_card`).
 *  All heavy lifting (price formatting, stock computation) is delegated
 *  to the POS store / server layer respectively; this patch only exposes
 *  thin, template-friendly getters.
 */

import {patch} from "@web/core/utils/patch";
import {usePos} from "@point_of_sale/app/store/pos_hook";
import {ProductCard} from "@point_of_sale/app/generic_components/product_card/product_card";

/**
 * Stock quantity threshold, in units, above which a product is
 * considered comfortably "in stock" (green badge). At or below this
 * threshold (but still greater than zero) the product is considered
 * "low stock" (amber badge).
 *
 * @type {number}
 */
const LOW_STOCK_THRESHOLD = 5;

/**
 * Patch `ProductCard.prototype` to add the reactive Point of Sale store
 * hook plus the price and stock getters consumed by product_card.xml.
 *
 * @see ProductCard - Core component defined by the `point_of_sale` module.
 *      Props (relevant subset):
 *        - product {Object}: the `product.product` record (as loaded into
 *          the POS front-end data models) that this card represents.
 *          Includes, thanks to this module's backend override,
 *          `pos_location_qty` (float) - the quantity on hand at the
 *          active POS's specific source stock location.
 */
patch(ProductCard.prototype, {
    /**
     * Extend the component's `setup()` lifecycle hook.
     *
     * Calls the original `setup()` first (via `super.setup()`) so that all
     * native ProductCard behavior/state is preserved untouched, then wires
     * up the `usePos()` hook so this component can reactively read from
     * the global POS store (active pricelist, session currency, tax
     * configuration, etc.).
     *
     * @override
     * @returns {void}
     */
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
    },

    /**
     * Compute the fully formatted, tax-and-pricelist-aware sales price for
     * the product represented by this card.
     *
     * Delegates entirely to `pos.getProductPriceFormatted(product)`, the
     * canonical Odoo 18 POS store method for price formatting, ensuring
     * this badge always matches the price the customer will actually be
     * charged.
     *
     * @returns {string} The human-readable, currency-formatted sales
     *      price (e.g. "$ 19.99"), ready for direct display in the
     *      template.
     */
    get formattedPrice() {
        return this.pos.getProductPriceFormatted(this.props.product);
    },

    /**
     * Whether this card's product is inventory-tracked (storable) and
     * therefore eligible to display a stock badge at all.
     *
     * Consumables and services are never inventory-tracked in Odoo 18, so
     * the stock badge must remain completely hidden for them rather than
     * showing a misleading "0" or empty pill.
     *
     * @returns {boolean} True when the product is a storable product.
     */
    get isStorable() {
        return Boolean(this.props.product.is_storable);
    },

    /**
     * Raw stock-on-hand quantity for this product at the active POS's
     * specific source stock location.
     *
     * Reads `pos_location_qty`, the field populated server-side (in
     * batch, per POS data load) by this module's `product.product`
     * override. Falls back to `0` when the value is missing entirely
     * (e.g. not yet loaded), using nullish coalescing so a legitimate
     * `0` quantity is never mistaken for "no data".
     *
     * @returns {number} The quantity on hand, in the product's unit of
     *      measure, at the active POS's source location.
     */
    get stockQty() {
        return this.props.product.pos_location_qty ?? 0;
    },

    /**
     * Human-readable, compact rendering of `stockQty` for the badge.
     *
     * Whole-number quantities render without decimals (e.g. "15"); any
     * product tracked in a fractional unit of measure (e.g. weight)
     * renders with up to two decimal places (e.g. "1.5").
     *
     * @returns {string} The formatted stock quantity, ready for direct
     *      display in the template.
     */
    get formattedStockQty() {
        const qty = this.stockQty;
        return Number.isInteger(qty) ? String(qty) : qty.toFixed(2);
    },

    /**
     * CSS status class reflecting this product's current stock level, so
     * the badge can be color-coded for instant recognition at the
     * register.
     *
     *   - `pos-stock-in`  : stockQty > 5  (comfortably in stock, green)
     *   - `pos-stock-low` : 0 < stockQty <= 5 (running low, amber)
     *   - `pos-stock-out` : stockQty <= 0 (out of stock, red)
     *
     * @returns {string} One of "pos-stock-in", "pos-stock-low", or
     *      "pos-stock-out".
     */
    get stockStatusClass() {
        const qty = this.stockQty;
        if (qty > LOW_STOCK_THRESHOLD) {
            return "pos-stock-in";
        }
        if (qty > 0) {
            return "pos-stock-low";
        }
        return "pos-stock-out";
    },
});