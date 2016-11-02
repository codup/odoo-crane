# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2014-2016 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, fields, models, _

class crane_repeat_work_order(models.TransientModel):
    _name = 'crane.repeat.work.order'
    _description = 'Repeat Work Order'

    TYPE_SELECTION = [
        ('no', 'No'),
        ('not_safe', 'Only failed'),
        ('all', 'All')
    ]


    @api.model
    def _is_completed(self):
        orders = self.env['crane.work.order']
        for wo in orders.browse(self._context.get('active_id')):
            if wo.state != 'done':
                return False
        return True

    type = fields.Selection(TYPE_SELECTION, 'Repeat Inspection Task', required=True, default='all')
    completed = fields.Boolean('Completed', default=_is_completed)

    @api.multi
    def repeat_wo(self):
        orders = self.env['crane.work.order']
        data = self.read()
        if data: data=data[0]
        else: 
            data={'type':'all'}
        last_id = False
        for wo in orders.browse(self._context.get('active_ids', self.ids)):
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
            last_id = orders.create(values)
        if last_id:
            return {
                'name': _('Work Order'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'crane.work.order',
                'res_id': last_id.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
            }
        return {'type': 'ir.actions.act_window_close',}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: