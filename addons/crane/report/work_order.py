# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 CodUP (<http://codup.com>).
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

from openerp.addons.report_webkit.webkit_report import webkit_report_extender
from datetime import datetime, timedelta

@webkit_report_extender("crane.report_crane_work_order")
def extend_demo(pool, cr, uid, localcontext, context):
    localcontext.update({
        "datetime": datetime,
        "timedelta": timedelta,
    })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: