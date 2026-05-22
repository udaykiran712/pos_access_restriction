# -*- coding: utf-8 -*-

{
    'name': 'POS User Access Restriction',
    'version': '18.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Restrict POS users to specific Point of Sale shops or registers in Odoo 18.',
    'description': """
POS User Access Restriction for Odoo 18
=======================================
This module enhances database security by allowing administrators to restrict standard 
POS Users to specific Point of Sale configurations. 

Key Features:
-------------
* **Multi-Shop Restriction:** Bind a user to one or multiple specific POS centers.
* **Odoo 18 Dashboard Filtering:** Dynamically filters the newly designed Odoo 18 POS dashboard.
* **Order & Session Security:** Restricts access to backend sessions and historical orders.
* **Manager Clean Bypass:** POS Managers maintain global visibility across all registers.
    """,
    'author': 'Gardas Udaykiran',
    'website': 'https://github.com/udaykiran712',
    'depends': ['point_of_sale'],
    'data': [
        'security/pos_security_rules.xml',
        'views/res_users_views.xml',
    ],
    # Images array is critical for the App Store carousel
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False, # Set to False because it's an extension, not a standalone app
    'auto_install': False,
    'license': 'LGPL-3', # Standard open-source license for free Odoo apps
}
