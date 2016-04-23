# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-2016 CodUP (<http://codup.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Crane & Hoist',
    'version': '1.1',
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
    'depends': ['report_webkit','mail'],
    'demo': ['crane_demo.xml'],
    'data': [
        'wizard/repeat_work_order_view.xml',
        'wizard/see_photo.xml',
        'crane_view.xml',
        'users_view.xml',
        'res_config_view.xml',
        'crane_sequence.xml',
        'crane_data.xml',
        'report/crane_report.xml',
        'wizard/email_work_order_data.xml',
    ],
    'css': ['static/src/css/crane.css'],
    'installable': True,
    'application': True,
    'price': 9,
    'currency': 'EUR',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
