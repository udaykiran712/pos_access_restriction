# -*- coding: utf-8 -*-
"""
Model: res.users
Extension for POS Access Restriction.
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    """
    Extends res.users to add POS shop restrictions.
    Adds a many2many field to limit which POS configurations a user can access,
    and a computed boolean field to control the visibility of that restriction
    based on POS group membership.
    """
    _inherit = 'res.users'

    allowed_pos_ids = fields.Many2many(
        comodel_name='pos.config',
        relation='res_users_pos_config_rel',
        column1='user_id',
        column2='pos_config_id',
        string="Allowed POS Shops",
        help="Select the specific POS shops this user is allowed to access. "
             "Note: You must activate the respective companies in your top-right "
             "company switcher to see their POS centers in this list."
    )

    has_pos_access = fields.Boolean(
        string="Has POS Access",
        compute='_compute_has_pos_access',
        help="Technical field; True if the user belongs to the 'Point of Sale / User' group. "
             "Used to show/hide the allowed_pos_ids field in the user form."
    )

    @api.depends('groups_id')
    def _compute_has_pos_access(self):
        """
        Sets has_pos_access to True only if the user is a member of the
        point_of_sale.group_pos_user security group. Recalculates automatically
        whenever the user's groups are modified.
        """
        pos_group = self.env.ref('point_of_sale.group_pos_user', raise_if_not_found=False)
        for user in self:
            user.has_pos_access = bool(pos_group and pos_group in user.groups_id)

    @api.constrains('allowed_pos_ids', 'company_ids')
    def _check_pos_company_access(self):
        """
        Validates that the assigned POS configurations belong to the companies
        that the user is explicitly allowed to access.

        This acts as a strict backend safeguard, preventing administrators from
        bypassing the XML UI domain restrictions via RPC calls, Python scripts,
        or raw CSV data imports.
        """
        for user in self:
            # Iterate through every POS center currently assigned to the user
            for pos in user.allowed_pos_ids:

                # Check two things:
                # 1. Does this POS center actually belong to a specific company?
                # 2. Is that company missing from the user's 'Allowed Companies' array?
                if pos.company_id and pos.company_id not in user.company_ids:
                    # If both are true, trigger a hard database rollback and alert the admin
                    raise ValidationError(
                        f"Security Violation: You cannot assign the POS '{pos.name}' "
                        f"because it belongs to '{pos.company_id.name}', which is not "
                        f"in this user's Allowed Companies."
                    )
