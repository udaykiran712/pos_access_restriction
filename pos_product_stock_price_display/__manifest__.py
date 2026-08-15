# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'POS Product Stock & Price Display',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Display dynamic, formatted sales price and real-time, '
               'location-specific stock on-hand directly on the Point of '
               'Sale product card.',
    'description': """
POS Product Stock & Price Display
==================================

This module enhances the standard Odoo 18 Point of Sale product grid by
enriching each Product Card with additional, at-a-glance information that
cashiers need while ringing up a sale.
    """,
    'author': 'Gardas Uday Kiran',
    'website': 'https://www.linkedin.com/in/udaykirangardas/',
    'license': 'LGPL-3',
    'depends': [
        'point_of_sale',
        'stock',
    ],
    'data': [],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_product_stock_price_display/static/src/app/generic_components/product_card/product_card.js',
            'pos_product_stock_price_display/static/src/app/generic_components/product_card/product_card.xml',
            'pos_product_stock_price_display/static/src/app/generic_components/product_card/product_card.scss',
            'pos_product_stock_price_display/static/src/app/store/pos_store.js',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/pos_screen.png',
        'static/description/error_popup.png',
        'static/description/insuficient_stock.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
