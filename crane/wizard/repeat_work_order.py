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

class crane_repeat_work_order(osv.osv_memory):
    _name = 'crane.repeat.work.order'
    _description = 'Repeat Work Order'

    TYPE_SELECTION = [
        ('no', 'No'),
        ('not_safe', 'Only failed'),
        ('all', 'All')
    ]

    def _is_completed(self, cr, uid, context=None):
        if context is None:
            context = {}
        orders = self.pool.get('crane.work.order')
        for wo in orders.browse(cr, uid, context.get('active_ids', []), context=context):
            if wo.state != 'done':
                return False
        return True

    _columns = {
        'type': fields.selection(TYPE_SELECTION, 'Repeat Inspection Task', required=True),
        'completed': fields.boolean('Completed'),
    }

    _defaults = {
        'type': 'all',
        'completed': _is_completed,
    }

    def repeat_wo(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        orders = self.pool.get('crane.work.order')
        data = self.read(cr, uid, ids)
        if data: data=data[0]
        else: 
            data={'type':'all'}
            context = {'active_ids':ids}
        last_id = False
        for wo in orders.browse(cr, uid, context.get('active_ids', []), context=context):
            values = {
                    'customer_id': wo.customer_id.id,
                    'origin': wo.name,
                }
            if data['type'] in ('not_safe','all'):
                new_task_lines = []
                for line in wo.task_ids:
                    if line.type == 'ins' and (data['type'] != 'not_safe' or line.result == 'not_safe'):
                        new_inspection_lines = []
                        line.equipment_id.equipment_type_id
                        for iline in line.equipment_id.equipment_type_id.inspection_ids:
                            new_inspection_lines.append([0,0,{
                                'name': iline.name,
                                'header': iline.header,
                                'sequence': iline.sequence,
                                'point_type_id': iline.point_type_id.id,
                                }])
                        new_task_lines.append([0,0,{
                            'type': line.type,
                            'wo_id': wo.id,
                            'equipment_id': line.equipment_id.id,
                            'inspection_line_ids': new_inspection_lines,
                            }])
                values['task_ids'] = new_task_lines
            last_id = orders.create(cr, uid, values, context=context)
        if last_id:
            return {
                'name': _('Work Order'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'crane.work.order',
                'res_id': int(last_id),
                'view_id': False,
                'type': 'ir.actions.act_window',
            }
        return {'type': 'ir.actions.act_window_close',}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: