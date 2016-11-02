# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2014-2016 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, fields, models, _

class crane_see_photo(models.TransientModel):
    _name = 'crane.see.photo'
    _description = 'See Photo'

    @api.model
    def get_inspection_point(self):
        return self._context.get('active_id')

    inspection_point_id = fields.Many2one('crane.task.inspection.line', 'Inspection Point', default=get_inspection_point)
    photo = fields.Binary(related='inspection_point_id.image')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: