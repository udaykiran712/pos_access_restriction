# POS Product Stock & Price Display

![Odoo Version](https://img.shields.io/badge/Odoo-18.0-714B67?style=flat-square&logo=odoo&logoColor=white)
![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue.svg?style=flat-square)
![Point of Sale](https://img.shields.io/badge/App-Point%20of%20Sale-2563EB?style=flat-square)
![Inventory](https://img.shields.io/badge/App-Inventory-16A34A?style=flat-square)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=flat-square)

**Technical Name:** `pos_product_stock_price_display`
**Author:** Uday Odoo Apps (Uday Kiran Gardas)
**Website:** [linkedin.com/in/udaykirangardas](https://www.linkedin.com/in/udaykirangardas/)
**License:** LGPL-3

---

## Executive Summary

`pos_product_stock_price_display` is a lightweight, non-invasive Odoo 18
Point of Sale extension that gives cashiers live, location-accurate
pricing and stock visibility directly on the product grid, and enforces
strict stock validation before a sale can be completed. It was built and
diagnosed against a live Odoo 18 database, not just in isolation - see
[Verification & Testing](#verification--testing) for the exact edge case
that shaped its architecture.

## Feature Highlights

| # | Feature | Summary |
|---|---------|---------|
| 1 | **Live Price Badge** | Top-left pill on every Product Card, computed via `pos.getProductPriceFormatted()` - always matches pricelist, tax mode, and currency actually charged. |
| 2 | **Location-Specific Stock Badge** | Bottom-right color-coded badge (🟢 In Stock `> 5`, 🟠 Low Stock `1-5`, 🔴 Out of Stock `≤ 0`), computed strictly from **internal** stock quants at the POS's source location. |
| 3 | **Out-of-Stock Sale Blocker** | Single guarded entry point (`PosStore.addLineToCurrentOrder`) blocks tile taps, barcode scans, and search-based additions alike when stock is exhausted or insufficient, via a native `AlertDialog`. Refunds/returns are always exempt. |

## Technical Stack & Design Decisions

- **Frontend:** OWL 2 (Odoo 18's native component framework).
  - `patch()` from `@web/core/utils/patch` for all component/store
    extensions - no core file overrides.
  - `t-inherit-mode="extension"` for all QWeb template changes - fully
    additive, upgrade-safe.
  - `usePos()` hook (`@point_of_sale/app/store/pos_hook`) for reactive
    access to the POS store.
  - `AlertDialog` (`@web/core/confirmation_dialog/confirmation_dialog`)
    via the native `dialog` service for the stock blocker's modal.
- **Backend:** Standard Odoo ORM, `product.product` model extension.
  - `pos_location_qty` is a non-stored `Float` field, whitelisted into
    the POS front-end payload via `_load_pos_data_fields`.
  - The authoritative stock figure is computed with a **single batched**
    `stock.quant._read_group` call per POS session load - not a
    per-product loop - keeping the module's performance flat regardless
    of catalog size.
  - The query is explicitly scoped to `location_id.usage = 'internal'`
    quants under the POS's configured source location. This was a
    deliberate correction after live diagnostics showed the naive
    `_compute_quantities_dict` approach nets out physical stock against
    virtual/inventory-adjustment location entries, producing `0.0` for
    products that were, in fact, fully stocked on the shelf.
- **Data Loading Pipeline:** Standard `pos.load.mixin` overrides
  (`_load_pos_data`, `_load_pos_data_fields`) - no custom controllers or
  RPC endpoints introduced.

## Installation & Configuration

1. Copy the `pos_product_stock_price_display` folder into your Odoo 18
   addons path.
2. Update the apps list: