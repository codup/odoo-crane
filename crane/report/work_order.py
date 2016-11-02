# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2014-2016 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, models
from datetime import datetime, timedelta

class CraneWorkOrderReport(models.AbstractModel):
    _name = 'report.crane.work_order'

    @api.model
    def render_html(self, docids, data=None):
        Report = self.env['report']
        report = Report._get_report_from_name('crane.work_order')
        selected_modules = self.env[report.model].browse(docids)
        docargs = {
            'datetime': datetime,
            'timedelta': timedelta,
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': selected_modules,
        }
        return Report.render('crane.work_order', docargs)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: