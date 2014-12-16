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

from openerp import tools
import time
import calendar
from openerp.tools.translate import _


VALUE_TYPE_SELECTION = [
    ('yes', 'YES/NO'),
    ('ok', 'OK/NOT OK'),
    ('good', 'GOOD/REPAIR/REPLACE')
]

INSPECTION_RESULT_SELECTION = [
    ('safe', 'Safe'),
    ('not_safe', 'Not Safe')
]

class crane_equipment_type(osv.osv):
    _name = 'crane.equipment.type'
    _description = 'Equipment Type'

    _columns = {
        'name': fields.char('Equipment Type Name', size=64, required=True, translate=True),
        'specification_ids': fields.one2many('crane.specification', 'equipment_type_id', 'Feature List'),
        'inspection_ids': fields.one2many('crane.inspection', 'equipment_type_id', 'Inspection Points'),
    }


class crane_specification(osv.osv):
    _name = 'crane.specification'
    _description = 'Specification'

    _columns = {
        'name': fields.char('Feature Name', size=64, required=True, translate=True),
        'equipment_type_id': fields.many2one('crane.equipment.type', 'Equipment Type', ondelete='cascade'),
        'sequence': fields.integer('Order', help="Used to order Features."),
    }

    _order = 'sequence, id'

    _defaults = {
        'sequence': 1,
    }


class crane_inspection(osv.osv):
    _name = 'crane.inspection'
    _description = 'Inspection'

    _columns = {
        'name': fields.char('Point Name', size=64, required=True, translate=True),
        'equipment_type_id': fields.many2one('crane.equipment.type', 'Equipment Type', ondelete='cascade'),
        'header': fields.boolean('Header'),
        'sequence': fields.integer('Order', help="Used to order Inspection Points."),
        # 'value_type': fields.selection(VALUE_TYPE_SELECTION, 'Available Values', required=True),
        'point_type_id': fields.many2one('crane.inspection.point.type', 'Point Type'),
    }

    _order = 'sequence, id'

    _defaults = {
        'sequence': 1,
        # 'value_type': 'ok',
    }


class crane_inspection_point_type(osv.osv):
    _name = 'crane.inspection.point.type'
    _description = 'Inspection Point Type'

    _columns = {
        'name': fields.char('Type Name', size=64, required=True, translate=True),
        'value_line_ids': fields.one2many('crane.inspection.point.value', 'point_type_id', 'Value'),
    }


class crane_inspection_point_value(osv.osv):
    _name = 'crane.inspection.point.value'
    _description = 'Inspection Point Value'

    _columns = {
        'name': fields.char('Value', size=64, required=True, translate=True),
        'result': fields.selection(INSPECTION_RESULT_SELECTION, 'Inspection Result', required=True),
        'point_type_id': fields.many2one('crane.inspection.point.type', 'Inspection Point Type', ondelete='cascade'),
    }


class crane_equipment(osv.osv):
    _name = 'crane.equipment'
    _description = 'Equipment'

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    def onchange_type(self, cr, uid, ids, type_id, feature_lines):
        equipment_type = self.pool.get('crane.equipment.type').browse(cr, uid, type_id)
        new_feature_lines = [[2,line[1],line[2]] for line in feature_lines if line[0]]
        for line in equipment_type.specification_ids:
            new_feature_lines.append([0,0,{
                'name': line.name,
                'sequence': line.sequence,
                }])
        return {'value': {
            'feature_line_ids': new_feature_lines,
        }}

    _columns = {
        'name': fields.char('Equipment Name', size=64, required=True, translate=True),
        'equipment_type_id': fields.many2one('crane.equipment.type', 'Equipment Type', required=True, ondelete='restrict'),
        'customer_id': fields.many2one('res.partner', 'Customer', required=True, ondelete='restrict'),
        'certificate': fields.char('Certificate Number', size=64),
        'image': fields.binary("Image",
            help="This field holds the image used as image for the asset, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image",
            store={
                'crane.equipment': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized image of the asset. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved, "\
                 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized image", type="binary", multi="_get_image",
            store={
                'crane.equipment': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized image of the asset. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
        'feature_line_ids': fields.one2many('crane.equipment.feature.line', 'equipment_id', 'Feature List'),
        'notes': fields.text('Notes'),
    }

    def create(self, cr, uid, vals, context=None):
        if vals.get('certificate','/')=='/':
            vals['certificate'] = self.pool.get('ir.sequence').get(cr, uid, 'crane.equipment') or '/'
        return super(crane_equipment, self).create(cr, uid, vals, context=context)


class crane_equipment_feature_line(osv.osv):
    _name = 'crane.equipment.feature.line'
    _description = 'Equipment feature line'

    _columns = {
        'name': fields.char('Feature', size=64, translate=True),
        'value': fields.char('Value', size=64, translate=True),
        'equipment_id': fields.many2one('crane.equipment', 'Equipment', select=True, ondelete='cascade'),
        'sequence': fields.integer('Order', help="Used to order Features."),
    }

    _order = 'sequence, id'


class crane_work_order(osv.osv):
    _name = 'crane.work.order'
    _description = 'Work Order'
    _inherit = ['mail.thread']

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('in_process', 'In Process'),
        ('done', 'Done')
    ]

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    def onchange_customer(self, cr, uid, ids, customer):
        customer = self.pool.get('res.partner').browse(cr, uid, customer)
        return {'value': {
            'location': customer.contact_address,
        }}

    _columns = {
        'name': fields.char('Work Order', size=64),
        'state': fields.selection(STATE_SELECTION, 'Status'),
        'customer_id': fields.many2one('res.partner', 'Customer', domain="[('is_company','=',1)]", ondelete='restrict'),
        'location': fields.related('customer_id', 'contact_address', string="Location", type="char", readonly=True),
        'date': fields.date('Date'),
        'origin': fields.char('Source Document', size=64),
        'po_number': fields.char('PO Number', size=64),
        'reviewed': fields.boolean('Reviewed'),
        'customer_person_id': fields.many2one('res.partner', 'Reviewed by Customer', domain="[('is_company','=',0)]", ondelete='restrict'),
        'image': fields.binary("Image",
            help="This field holds the image used as image for the sign, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image",
            store={
                'crane.work.order': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized image of the sign. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved, "\
                 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized image", type="binary", multi="_get_image",
            store={
                'crane.work.order': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized image of the sign. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
        'task_ids': fields.one2many('crane.task', 'wo_id', 'Task'),
        'task_copy_ids': fields.one2many('crane.task', 'wo_id', 'Task'),
        'description': fields.text('Description'),
        'company_id': fields.many2one('res.company','Company',required=True),
    }

    _defaults = {
        'date': fields.date.context_today,
        'state': 'draft',
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'crane.work.order', context=c),
    }

    def confirm_order(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'in_process'})
        task = self.pool.get('crane.task')
        task_ids = task.search(cr, uid, [('wo_id', 'in', ids)])
        task.write(cr, uid, task_ids, {'state': 'in_progress'})
        return True

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'crane.work.order') or '/'
        return super(crane_work_order, self).create(cr, uid, vals, context=context)

    def send_email(self, cr, uid, ids, context=None):
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'crane', 'email_template_work_order')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'crane', 'crane_email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        ctx.update({
            'default_model': 'crane.work.order',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


class crane_task(osv.osv):
    _name = 'crane.task'
    _description = 'Task'

    STATE_SELECTION = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    ]

    TASK_TYPE_SELECTION = [
        ('ins', 'Inspection'),
        ('serv', 'Service')
    ]

    def _get_total(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for line in task.labor_line_ids:
                total += line.duration
            res[task.id] = total
        return res

    def _get_subtype(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            res[task.id] = len([insp for insp in task.inspection_line_ids if insp.header == True])
        return res

    _columns = {
        'name': fields.char('Task', size=64),
        'state': fields.selection(STATE_SELECTION, 'Status'),
		'type': fields.selection(TASK_TYPE_SELECTION, 'Type', required=True),
        'wo_id': fields.many2one('crane.work.order', 'Work Order', ondelete='cascade'),
		'equipment_id': fields.many2one('crane.equipment', 'Equipment', select=True, required=True, ondelete='restrict'),
		'equipment_type': fields.related('equipment_id', 'equipment_type_id', type="many2one", relation="crane.equipment.type", string="Equipment Type", readonly=True),
		'certificate': fields.related('equipment_id', 'certificate', type="char", string="Equipment Certificate Number", readonly=True),
		'completion_date': fields.date('Completion Date'),
		'result': fields.selection(INSPECTION_RESULT_SELECTION, 'Inspection Result'),
        'total_labor': fields.function(_get_total, method=True, string='Total Labor h:m'),
        'subtype': fields.function(_get_subtype, method=True, string='Subtype'),
 		'equipment_feature': fields.related('equipment_id', 'feature_line_ids', type="one2many", relation="crane.equipment.feature.line", string="Equipment Features", readonly=True),
        'inspection_line_ids': fields.one2many('crane.task.inspection.line', 'task_id', 'Inspection Points'),
        'labor_line_ids': fields.one2many('crane.task.labor.line', 'task_id', 'Labor'),
		'part_line_ids': fields.one2many('crane.task.part.line', 'task_id', 'Parts'),
        'description': fields.text('Description'),
		'notes': fields.text('Notes'),
        'approve_uid':  fields.many2one('res.users', 'Approved by'),
    }

    _defaults = {
        'state': 'new',
        'completion_date': fields.date.context_today,
    }

    def onchange_equipment(self, cr, uid, ids, type, equipment_id, inspection_lines):
        v = {}
        new_inspection_lines = [[2,line[1],line[2]] for line in inspection_lines if line[0]]
        if equipment_id:
            equipment = self.pool.get('crane.equipment').browse(cr, uid, equipment_id)
            v['certificate'] = equipment.certificate
            new_feature_lines = []
            for line in equipment.feature_line_ids:
                new_feature_lines.append([0,0,{
                    'name': line.name,
                    'value': line.value,
                    }])
            v['equipment_feature'] = new_feature_lines
            equipment_type = equipment.equipment_type_id
            v['equipment_type'] = equipment_type.id
            if type == 'ins':
                for line in equipment_type.inspection_ids:
                    new_inspection_lines.append([0,0,{
                        'name': line.name,
                        'header': line.header,
                        'sequence': line.sequence,
                        'point_type_id': line.point_type_id.id,
                        }])
        v['inspection_line_ids'] = new_inspection_lines
        return {'value': v}

    def onchange_labor(self, cr, uid, ids, labor):
        total = 0
        for labor in self.resolve_2many_commands(cr, uid, 'labor_line_ids', labor, context=None):
            total += labor.get('duration')
        return {'value': {
            'total_labor': total,
        }}

    def done_task(self, cr, uid, ids, context=None):
        for task in self.browse(cr, uid, ids, context=context):
            result = 'safe'
            if task.type == 'ins':
                safe = True
                for line in task.inspection_line_ids:
                    if not line.header:
                        if not line.point_value_id:
                            raise osv.except_osv(_('Error!'), _('Before work Done, You must fill all Inspection Points!'))
                        else:
                            if safe and line.point_value_id.result == 'not_safe': safe = False
                if not safe: result = 'not_safe'
            self.write(cr, uid, task.id, {'state':'done','completion_date':time.strftime('%Y-%m-%d'),'result':result,'approve_uid':uid})
        wos_ids = set()
        for order in self.read(cr, uid, ids, ['wo_id'], context=context):
            wos_ids.add(order['wo_id'][0])
        wo_ids = []
        for id in wos_ids: wo_ids.append(id)
        wo = self.pool.get('crane.work.order')
        done_wo_ids = []
        for order in wo.browse(cr, uid, wo_ids, context=context):
            done = True
            for task in order.task_ids:
                if task.state != 'done':
                    done = False
                    break
            if done: done_wo_ids.append(order.id)
        wo.write(cr, uid, done_wo_ids, {'state': 'done','date': time.strftime('%Y-%m-%d')})
        return True

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'crane.task') or '/'
        return super(crane_task, self).create(cr, uid, vals, context=context)


class crane_task_inspection_line(osv.osv):
    _name = 'crane.task.inspection.line'
    _description = 'Inspection Line'

    STATUS_SELECTION = [
        ('ok', 'OK'),
        ('not_ok', 'NOT OK'),
        ('good', 'GOOD'),
        ('repair', 'REPAIR'),
        ('replace', 'REPLACE'),
        ('yes', 'YES'),
        ('no', 'NO')
    ]

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    _columns = {
        'name': fields.char('Point Name', size=64, required=True, translate=True),
        'task_id': fields.many2one('crane.task', 'Task', ondelete='cascade'),
		# 'status': fields.selection(STATUS_SELECTION, 'Status'),
        'point_value_id': fields.many2one('crane.inspection.point.value', 'Status', ondelete='restrict'),
        'comment': fields.char('Comment', size=64),
        'header': fields.boolean('Header'),
        'sequence': fields.integer('Order', help="Used to order Inspection Points."),
        # 'value_type': fields.selection(VALUE_TYPE_SELECTION, 'Available Values'),
        'point_type_id': fields.many2one('crane.inspection.point.type', 'Point Type', ondelete='restrict'),
        'image': fields.binary("Image", help="This field holds the photo of inspection point, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Photo", type="binary", multi="_get_image",
            store={
                'crane.task.inspection.line': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            }),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized image", type="binary", multi="_get_image",
            store={
                'crane.task.inspection.line': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized image of the sign. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
    }

    _order = 'sequence, id'


class crane_task_labor_line(osv.osv):
    _name = 'crane.task.labor.line'
    _description = 'Labor Line'

    WORK_TYPE_SELECTION = [
        ('regular', 'R'),
		('overtime', 'O'),
        ('double', 'D')
    ]

    def onchange_time(self, cr, uid, ids, start, end, duration):
        if start and end:
            start = 1.0*calendar.timegm(time.strptime(start, "%Y-%m-%d %H:%M:%S"))
            end = 1.0*calendar.timegm(time.strptime(end, "%Y-%m-%d %H:%M:%S"))
            return {'value': {
                'duration': (end - start)/3600,
            }}
        if start:
            end = 1.0*calendar.timegm(time.strptime(start, "%Y-%m-%d %H:%M:%S")) + 3600*duration
            return {'value': {
            'end_date': time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(end)),
            }}
        if end:
            start = 1.0*calendar.timegm(time.strptime(end, "%Y-%m-%d %H:%M:%S")) - 3600*duration
            return {'value': {
            'start_date': time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(start)),
            }}
        return {}

    def onchange_duration(self, cr, uid, ids, start, end, duration):
        if start:
            end = 1.0*calendar.timegm(time.strptime(start, "%Y-%m-%d %H:%M:%S")) + 3600*duration
            return {'value': {
            'end_date': time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(end)),
            }}
        if end:
            start = 1.0*calendar.timegm(time.strptime(end, "%Y-%m-%d %H:%M:%S")) - 3600*duration
            return {'value': {
            'start_date': time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(start)),
            }}
        return {}

    _columns = {
        'name': fields.char('Labor Work', size=64),
        'task_id': fields.many2one('crane.task', 'Task', ondelete='cascade'),
        'user_id': fields.many2one('res.users', 'Serviceman', ondelete='restrict'),
		'start_date': fields.datetime('Start'),
		'end_date': fields.datetime('End'),
		'duration': fields.float('Duration h:m'),
		'type': fields.selection(WORK_TYPE_SELECTION, 'Type'),
        'comment': fields.char('Comment', size=64),
    }


class crane_task_part_line(osv.osv):
    _name = 'crane.task.part.line'
    _description = 'Part Line'

    _columns = {
        'name': fields.char('Part Number', size=64),
        'task_id': fields.many2one('crane.task', 'Task', ondelete='cascade'),
		'description': fields.char('Description', size=64),
		'qty': fields.float('Quantity'),
    }	

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: