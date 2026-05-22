===========================
POS User Access Restriction
===========================

Overview
--------
In standard Odoo, granting a user 'POS User' access allows them to see every Point of Sale configuration and all historical orders across the database. This module solves that security flaw by allowing administrators to explicitly define which POS centers a user is authorized to see and operate.

Configuration
-------------
1. Navigate to **Settings > Users & Companies > Users**.
2. Select a User.
3. Under the **Access Rights** tab, locate the **POS Restrictions** section.
4. Add the specific Point of Sale shops to the `Allowed POS Shops` field.
5. If left empty, the user will be restricted from seeing *any* POS centers until assigned.

Technical Implementation
------------------------
This module relies entirely on standard Odoo Record Rules (`ir.rule`). It does not override standard JavaScript or Python methods, ensuring maximum compatibility with other third-party POS modules.