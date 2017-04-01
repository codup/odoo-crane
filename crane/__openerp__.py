# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2014-2016 CodUP (<http://codup.com>).
#
##############################################################################

{
    'name': 'Crane & Hoist',
    'version': '1.3',
    'summary': 'Inspection and Service System',
    'description': """
Inspection and Service System for Crane & Hoist.
================================================
Support following feature:
    * Manage Customers
    * Manage Equipment
    * Work Orders and Tasks
    * Inspection and Service
    * Work Order and Inspection Report
    """,
    'author': 'CodUP',
    'website': 'http://codup.com',
    'category': 'Industries',
    'sequence': 0,
    'depends': ['mail'],
    'demo': ['crane_demo.xml'],
    'data': [
        'security/crane_security.xml',
        'security/ir.model.access.csv',
        'views/crane.xml',
        'wizard/repeat_work_order_view.xml',
        'wizard/see_photo.xml',
        'crane_view.xml',
        'users_view.xml',
        'res_config_view.xml',
        'crane_sequence.xml',
        'crane_data.xml',
        'report/crane_report.xml',
        'report/work_order.xml',
        'wizard/email_work_order_data.xml',
    ],
    'installable': True,
    'application': True,
    'price': 9,
    'currency': 'EUR',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: