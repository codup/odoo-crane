# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2014-2016 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo import tools
import time
import calendar


VALUE_TYPE_SELECTION = [
    ('yes', 'YES/NO'),
    ('ok', 'OK/NOT OK'),
    ('good', 'GOOD/REPAIR/REPLACE')
]

INSPECTION_RESULT_SELECTION = [
    ('safe', 'Safe'),
    ('not_safe', 'Not Safe')
]

class crane_equipment_type(models.Model):
    _name = 'crane.equipment.type'
    _description = 'Equipment Type'

    name = fields.Char('Equipment Type Name', size=64, required=True, translate=True)
    specification_ids = fields.One2many('crane.specification', 'equipment_type_id', 'Feature List')
    inspection_ids = fields.One2many('crane.inspection', 'equipment_type_id', 'Inspection Points')


class crane_specification(models.Model):
    _name = 'crane.specification'
    _description = 'Specification'

    name = fields.Char('Feature Name', size=64, required=True, translate=True)
    equipment_type_id = fields.Many2one('crane.equipment.type', 'Equipment Type', ondelete='cascade')
    sequence = fields.Integer('Order', help="Used to order Features.", default=1)

    _order = 'sequence, id'


class crane_inspection(models.Model):
    _name = 'crane.inspection'
    _description = 'Inspection'

    name = fields.Char('Point Name', size=64, required=True, translate=True)
    equipment_type_id = fields.Many2one('crane.equipment.type', 'Equipment Type', ondelete='cascade')
    header = fields.Boolean('Header')
    sequence = fields.Integer('Order', help="Used to order Inspection Points.", default=1)
    point_type_id =  fields.Many2one('crane.inspection.point.type', 'Point Type')

    _order = 'sequence, id'


class crane_inspection_point_type(models.Model):
    _name = 'crane.inspection.point.type'
    _description = 'Inspection Point Type'

    name = fields.Char('Type Name', size=64, required=True, translate=True)
    value_line_ids = fields.One2many('crane.inspection.point.value', 'point_type_id', 'Value')


class crane_inspection_point_value(models.Model):
    _name = 'crane.inspection.point.value'
    _description = 'Inspection Point Value'

    name = fields.Char('Value', size=64, required=True, translate=True)
    result = fields.Selection(INSPECTION_RESULT_SELECTION, 'Inspection Result', required=True)
    point_type_id = fields.Many2one('crane.inspection.point.type', 'Inspection Point Type', ondelete='cascade')


class crane_equipment(models.Model):
    _name = 'crane.equipment'
    _description = 'Equipment'

    @api.onchange('equipment_type_id')
    def onchange_type(self):
        new_feature_lines = []
        for line in self.equipment_type_id.specification_ids:
            new_feature_lines.append([0,0,{
                'name': line.name,
                'sequence': line.sequence,
                }])
        self.feature_line_ids = new_feature_lines

    name = fields.Char('Equipment Name', size=64, required=True, translate=True)
    equipment_type_id = fields.Many2one('crane.equipment.type', 'Equipment Type', required=True, ondelete='restrict')
    customer_id = fields.Many2one('res.partner', 'Customer', required=True, ondelete='restrict')
    certificate = fields.Char('Certificate Number', size=64)
    image = fields.Binary("Image")
    image_small = fields.Binary("Small-sized image")
    image_medium = fields.Binary("Medium-sized image")
    feature_line_ids = fields.One2many('crane.equipment.feature.line', 'equipment_id', 'Feature List')
    notes = fields.Text('Notes')

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        if vals.get('certificate','/')=='/':
            vals['certificate'] = self.env['ir.sequence'].next_by_code('crane.equipment') or '/'
        return super(crane_equipment, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(crane_equipment, self).write(vals)


class crane_equipment_feature_line(models.Model):
    _name = 'crane.equipment.feature.line'
    _description = 'Equipment feature line'

    name = fields.Char('Feature', size=64, translate=True)
    value = fields.Char('Value', size=64, translate=True)
    equipment_id = fields.Many2one('crane.equipment', 'Equipment', select=True, ondelete='cascade')
    sequence = fields.Integer('Order', help="Used to order Features.")

    _order = 'sequence, id'


class crane_work_order(models.Model):
    _name = 'crane.work.order'
    _description = 'Work Order'

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('in_process', 'In Process'),
        ('done', 'Done')
    ]

    @api.onchange('customer_id')
    def onchange_customer(self):
        self.location = self.customer_id.contact_address

    name = fields.Char('Work Order', size=64)
    state = fields.Selection(STATE_SELECTION, 'Status', default='draft')
    customer_id = fields.Many2one('res.partner', 'Customer', domain="[('is_company','=',1)]", ondelete='restrict')
    location = fields.Char(related='customer_id.contact_address', string="Location", readonly=True)
    date = fields.Date('Date', default=fields.Date.today)
    origin = fields.Char('Source Document', size=64)
    po_number = fields.Char('PO Number', size=64)
    reviewed = fields.Boolean('Reviewed')
    customer_person_id = fields.Many2one('res.partner', 'Reviewed by Customer', domain="[('is_company','=',0)]", ondelete='restrict')
    image = fields.Binary("Image")
    image_medium = fields.Binary("Medium-sized image")
    image_small = fields.Binary("Small-sized image")
    task_ids = fields.One2many('crane.task', 'wo_id', 'Task')
    task_copy_ids = fields.One2many('crane.task', 'wo_id', 'Task')
    description = fields.Text('Description')
    company_id = fields.Many2one('res.company','Company',required=True, default=lambda self: self.env['res.company']._company_default_get('crane.work.order'))

    @api.multi
    def confirm_order(self):
        self.write({'state': 'in_process'})
        task = self.env['crane.task']
        task_ids = task.search([('wo_id', 'in', self.ids)])
        task_ids.write({'state': 'in_progress'})
        return True

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        if vals.get('name','/')=='/':
            vals['name'] = self.env['ir.sequence'].next_by_code('crane.work.order') or '/'
        return super(crane_work_order, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(crane_work_order, self).write(vals)

    @api.multi
    def send_email(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('crane', 'email_template_work_order')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'crane.work.order',
            'default_res_id': self.ids[0],
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


class crane_task(models.Model):
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


    @api.depends('labor_line_ids', 'labor_line_ids.duration')
    def _get_total(self):
        for task in self:
            total = 0.0
            for line in task.labor_line_ids:
                total += line.duration
            task.total_labor = total

    @api.depends('inspection_line_ids','inspection_line_ids.header')
    def _get_subtype(self):
        for task in self:
            task.subtype = len([insp for insp in task.inspection_line_ids if insp.header == True])

    name = fields.Char('Task', size=64)
    state = fields.Selection(STATE_SELECTION, 'Status', default='new')
    type = fields.Selection(TASK_TYPE_SELECTION, 'Type', required=True)
    wo_id = fields.Many2one('crane.work.order', 'Work Order', ondelete='cascade')
    equipment_id = fields.Many2one('crane.equipment', 'Equipment', select=True, required=True, ondelete='restrict')
    equipment_type = fields.Many2one(related='equipment_id.equipment_type_id', string="Equipment Type", readonly=True)
    certificate = fields.Char(related='equipment_id.certificate', string="Equipment Certificate Number", readonly=True)
    completion_date = fields.Date('Completion Date', default=fields.Date.today)
    result = fields.Selection(INSPECTION_RESULT_SELECTION, 'Inspection Result')
    total_labor = fields.Float(compute="_get_total", string='Total Labor h:m')
    subtype = fields.Integer(compute="_get_subtype", string='Subtype')
    equipment_feature = fields.One2many(related='equipment_id.feature_line_ids', string="Equipment Features", readonly=True)
    inspection_line_ids = fields.One2many('crane.task.inspection.line', 'task_id', 'Inspection Points')
    labor_line_ids = fields.One2many('crane.task.labor.line', 'task_id', 'Labor')
    part_line_ids = fields.One2many('crane.task.part.line', 'task_id', 'Parts')
    description = fields.Text('Description')
    notes = fields.Text('Notes')
    approve_uid = fields.Many2one('res.users', 'Approved by')


    @api.onchange('type','equipment_id','inspection_line_ids')
    def onchange_equipment(self):
        new_inspection_lines = []
        if self.equipment_id:
            equipment = self.equipment_id
            self.certificate = equipment.certificate
            new_feature_lines = []
            for line in equipment.feature_line_ids:
                new_feature_lines.append([0,0,{
                    'name': line.name,
                    'value': line.value,
                    }])
            self.equipment_feature = new_feature_lines
            equipment_type = equipment.equipment_type_id
            self.equipment_type = equipment_type.id
            if self.type == 'ins':
                for line in equipment_type.inspection_ids:
                    new_inspection_lines.append([0,0,{
                        'name': line.name,
                        'header': line.header,
                        'sequence': line.sequence,
                        'point_type_id': line.point_type_id.id,
                        }])
        self.inspection_line_ids = new_inspection_lines

    @api.onchange('labor_line_ids')
    def onchange_labor(self):
        total = 0
        for labor in self.labor_line_ids:
            total += labor.duration
        self.total_labor = total

    @api.multi
    def done_task(self):
        for task in self:
            result = 'safe'
            if task.type == 'ins':
                safe = True
                for line in task.inspection_line_ids:
                    if not line.header:
                        if not line.point_value_id:
                            raise UserError(_('Before work Done, You must fill all Inspection Points!'))
                        else:
                            if safe and line.point_value_id.result == 'not_safe': safe = False
                if not safe: result = 'not_safe'
            task.write({'state':'done','completion_date':time.strftime('%Y-%m-%d'),'result':result,'approve_uid':self.env.user.id})
        wos_ids = set()
        for task in self:
            wos_ids.add(task.wo_id.id)
        wo_ids = []
        for id in wos_ids: wo_ids.append(id)
        wo = self.env['crane.work.order']
        for order in wo.browse(wo_ids):
            done = True
            for task in order.task_ids:
                if task.state != 'done':
                    done = False
                    break
            if done: wo = wo | order
        wo.write({'state': 'done','date': time.strftime('%Y-%m-%d')})

    @api.model
    def create(self, vals):
        if vals.get('name','/')=='/':
            vals['name'] = self.env['ir.sequence'].next_by_code('crane.task') or '/'
        return super(crane_task, self).create(vals)


class crane_task_inspection_line(models.Model):
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

    name = fields.Char('Point Name', size=64, required=True, translate=True)
    task_id = fields.Many2one('crane.task', 'Task', ondelete='cascade')
    point_value_id = fields.Many2one('crane.inspection.point.value', 'Status', ondelete='restrict')
    comment = fields.Char('Comment', size=64)
    header = fields.Boolean('Header')
    sequence = fields.Integer('Order', help="Used to order Inspection Points.")
    point_type_id = fields.Many2one('crane.inspection.point.type', 'Point Type', ondelete='restrict')
    image = fields.Binary("Image")
    image_medium = fields.Binary("Medium-sized image")
    image_small = fields.Binary("Small-sized image")

    _order = 'sequence, id'

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(crane_task_inspection_line, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(crane_task_inspection_line, self).write(vals)


class crane_task_labor_line(models.Model):
    _name = 'crane.task.labor.line'
    _description = 'Labor Line'

    WORK_TYPE_SELECTION = [
        ('regular', 'R'),
		('overtime', 'O'),
        ('double', 'D')
    ]

    @api.onchange('start_date','end_date')        
    def onchange_time(self):
        if self.start_date and self.end_date:
            start = 1.0*calendar.timegm(time.strptime(self.start_date, "%Y-%m-%d %H:%M:%S"))
            end = 1.0*calendar.timegm(time.strptime(self.end_date, "%Y-%m-%d %H:%M:%S"))
            self.duration = (end - start)/3600
            return
        if self.start_date:
            end = 1.0*calendar.timegm(time.strptime(self.start_date, "%Y-%m-%d %H:%M:%S")) + 3600*self.duration
            self.end_date = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(end))
            return
        if self.end_date:
            start = 1.0*calendar.timegm(time.strptime(self.end_date, "%Y-%m-%d %H:%M:%S")) - 3600*self.duration
            self.start_date = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(start))

    @api.onchange('duration')
    def onchange_duration(self):
        if self.start_date:
            end = 1.0*calendar.timegm(time.strptime(self.start_date, "%Y-%m-%d %H:%M:%S")) + 3600*self.duration
            self.end_date = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(end))
            return
        if self.end_date:
            start = 1.0*calendar.timegm(time.strptime(self.end_date, "%Y-%m-%d %H:%M:%S")) - 3600*self.duration
            self.start_date = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(start))

    name = fields.Char('Labor Work', size=64)
    task_id = fields.Many2one('crane.task', 'Task', ondelete='cascade')
    user_id = fields.Many2one('res.users', 'Serviceman', ondelete='restrict')
    start_date = fields.Datetime('Start')
    end_date = fields.Datetime('End')
    duration = fields.Float('Duration h:m')
    type = fields.Selection(WORK_TYPE_SELECTION, 'Type')
    comment = fields.Char('Comment', size=64)


class crane_task_part_line(models.Model):
    _name = 'crane.task.part.line'
    _description = 'Part Line'

    name = fields.Char('Part Number', size=64)
    task_id = fields.Many2one('crane.task', 'Task', ondelete='cascade')
    description = fields.Char('Description', size=64)
    qty = fields.Float('Quantity')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: