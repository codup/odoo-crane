# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2014-2018 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, models
from datetime import datetime, timedelta

class CraneWorkOrderReport(models.AbstractModel):
    _name = 'report.crane.work_order'

    @api.multi
    def _get_report_values(self, docids, data=None):
        docs = self.env['crane.work.order'].browse(docids)
        return {
            'datetime': datetime,
            'timedelta': timedelta,
            'doc_ids': docs.ids,
            'doc_model': 'crane.work.order',
            'docs': docs
        }
