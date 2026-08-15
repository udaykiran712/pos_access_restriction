# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

"""
models/product_product.py
==========================
"""

from odoo import api, fields, models


class ProductProduct(models.Model):
    """Extend ``product.product`` with POS-location-specific stock data."""

    _inherit = 'product.product'

    pos_location_qty = fields.Float(
        string='POS Location Stock',
        compute='_compute_pos_location_qty',
        digits='Product Unit of Measure',
        help="Quantity on hand for this product, strictly within internal "
             "stock locations under the source stock location configured "
             "on the active Point of Sale's operation type (Point of Sale "
             "> Settings > Operation Type > Source Location). This is "
             "intentionally NOT the generic, company-wide 'Quantity On "
             "Hand' - it reflects genuine physical stock at the exact "
             "location the POS session will deduct from, excluding "
             "virtual/adjustment locations. The value set by the compute "
             "method below is a placeholder only; the accurate figure is "
             "injected directly by _load_pos_data() via a batched "
             "stock.quant read.",
    )

    def _compute_pos_location_qty(self):
        """Placeholder compute for ``pos_location_qty``.

        This field is intentionally non-stored so it can be whitelisted
        and shipped through the standard POS data-loading pipeline, but
        its authoritative value is never produced here. The accurate,
        physically-correct quantity (restricted to internal locations,
        excluding virtual/adjustment locations) is computed in a single
        batched ``stock.quant._read_group`` call inside
        ``_load_pos_data`` and injected directly into the loaded data
        payload after ``super()`` has run.

        Every record defaults to ``0.0`` here so that any access to this
        field *outside* of the POS data-loading pipeline (e.g. from a
        view or another module) fails safe rather than raising or
        returning a stale/misleading value.

        :return: None. Sets ``pos_location_qty`` to ``0.0`` in place on
            every record of ``self``, per standard Odoo computed-field
            conventions.
        """
        self.pos_location_qty = 0.0

    @api.model
    def _load_pos_data_fields(self, config_id):
        """Whitelist ``pos_location_qty`` for the POS front-end data load.

        :param int config_id: id of the active ``pos.config`` record.
        :return: list[str] - the full set of ``product.product`` field
            names to be loaded into the POS session, including the
            location-specific stock field added by this module.
        """
        fields_list = super()._load_pos_data_fields(config_id)
        if 'pos_location_qty' not in fields_list:
            fields_list.append('pos_location_qty')
        return fields_list

    def _load_pos_data(self, data):
        """Load POS data and overwrite ``pos_location_qty`` with the
        accurate, internal-locations-only stock figure.

        :param dict data: the in-progress POS bootstrap data payload,
            keyed by model name, as built by ``pos.load.mixin``. Must
            already contain a loaded ``pos.config`` entry, as is
            guaranteed by the native Odoo 18 POS loading order.
        :return: dict - the standard ``_load_pos_data`` response for
            ``product.product``, with ``pos_location_qty`` corrected to
            reflect genuine internal-location stock on hand.
        """
        loaded_data = super()._load_pos_data(data)

        config_id = data['pos.config']['data'][0]['id']
        config = self.env['pos.config'].browse(config_id)
        location_id = config.picking_type_id.default_location_src_id.id

        product_ids = [product_vals['id'] for product_vals in loaded_data['data']]

        if location_id and product_ids:
            domain = [
                ('product_id', 'in', product_ids),
                ('location_id', 'child_of', location_id),
                ('location_id.usage', '=', 'internal'),
            ]
            quant_groups = self.env['stock.quant']._read_group(
                domain,
                groupby=['product_id'],
                aggregates=['quantity:sum'],
            )
            qty_by_product_id = {
                product.id: quantity
                for product, quantity in quant_groups
            }
        else:
            qty_by_product_id = {}

        for product_vals in loaded_data['data']:
            product_vals['pos_location_qty'] = qty_by_product_id.get(product_vals['id'], 0.0)

        return loaded_data
