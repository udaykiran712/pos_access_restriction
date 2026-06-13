from odoo import models, api

class PosSession(models.Model):
    """
    Extension of pos.session to handle automated lot and serial number
    lookups based on FEFO/FIFO removal strategies for the active POS location.
    """
    _inherit = 'pos.session'

    @api.model
    def get_fefo_lot_for_pos(self, product_id, config_id, exclude_lots=None, needed_qty=1):
        """
        Retrieves the oldest available lot(s) or serial number(s) for a given product
        within the source location of the current Point of Sale configuration.

        :param int product_id: The ID of the product being added to the cart.
        :param int config_id: The ID of the active pos.config.
        :param list exclude_lots: List of lot/serial names already assigned in the current cart.
        :param int needed_qty: The number of unique serials/lots required to fulfill the cart line.
        :return: A list of lot/serial names assigned to fulfill the requirement.
        :rtype: list
        """
        if exclude_lots is None:
            exclude_lots = []

        # Resolve the specific source location tied to this POS configuration
        config = self.env['pos.config'].browse(config_id)
        location_id = config.picking_type_id.default_location_src_id.id

        if not location_id:
            return []

        # Base query: Find available stock in the POS location that has a defined lot
        domain = [
            ('product_id', '=', product_id),
            ('location_id', 'child_of', location_id),
            ('quantity', '>', 0),
            ('lot_id', '!=', False)
        ]

        # Prevent re-assigning serials that are already sitting in the active draft cart
        if exclude_lots:
            domain.append(('lot_id.name', 'not in', exclude_lots))

        quants = self.env['stock.quant'].search(domain)

        if not quants:
            return []

        # FEFO Strategy: Prioritize lots by expiration or removal date
        valid_quants = quants.filtered(lambda q: q.lot_id.expiration_date or q.lot_id.removal_date)
        sorted_quants = sorted(valid_quants, key=lambda q: q.lot_id.expiration_date or q.lot_id.removal_date)

        # FIFO Fallback: Append remaining lots sorted by creation date if expiry dates are missing
        no_expiry_quants = quants - valid_quants
        sorted_quants.extend(sorted(no_expiry_quants, key=lambda q: q.lot_id.create_date))

        # Aggregate the exact number of unique lots/serials requested by the frontend
        assigned_lots = []
        for quant in sorted_quants:
            if quant.lot_id.name not in assigned_lots:
                assigned_lots.append(quant.lot_id.name)
            if len(assigned_lots) >= needed_qty:
                break

        return assigned_lots