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

from openerp.osv import fields, osv
from openerp.tools.translate import _

class crane_see_photo(osv.osv_memory):
    _name = 'crane.see.photo'
    _description = 'See Photo'

    def get_inspection_point_photo(self, cr, uid, context=None):
        if context is None:
            context = {}
        inspection_point = self.pool.get('crane.task.inspection.line').browse(cr, uid, context.get('active_ids', [])[0])
        return inspection_point.image

    _columns = {
        'inspection_point_id': fields.many2one('crane.task.inspection.line', 'Inspection Point'),
 		'photo': fields.related('inspection_point_id', 'image', type="binary"),
    }

    _defaults = {
        'photo': get_inspection_point_photo,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: