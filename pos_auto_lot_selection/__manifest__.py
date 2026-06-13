{
    'name': 'POS Auto Lot/Serial Selection',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Automatically assigns the oldest lot/serial (FEFO/FIFO) in POS without popup interruptions.',
    'description': """
POS Auto Lot/Serial Selection
=============================
This module enhances the Point of Sale checkout flow by automatically assigning 
the oldest available lot or serial number to tracked products based on FEFO 
(First Expired, First Out) or FIFO (First In, First Out) strategies.

Features:
---------
* Completely bypasses the native Odoo lot selection popup when stock is available.
* Supports both unique Serial Numbers and batch Lots.
* Dynamically handles multi-quantity increments at the POS counter.
* Automatically filters out serials already present in the active draft cart.
* Gracefully falls back to the manual selection popup if stock is depleted or untracked.
    """,
    'author': 'Gardas Udaykiran',
    'website': 'https://github.com/udaykiran712',
    'depends': ['point_of_sale', 'stock'],
    'data': [],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_auto_lot_selection/static/src/js/pos_order_patch.js',
        ],
    },
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
