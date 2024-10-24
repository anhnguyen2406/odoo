# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import ast
from collections import defaultdict
from datetime import timedelta
from random import randint

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv.expression import OR
from odoo.tools.misc import get_lang

class MyProject(models.Model):
    _name = "my_project.project"
    _description = "My Project"
    _order = "sequence, name, id"

    def _compute_task_count(self):
        task_data = self.env['my_project.task'].read_group([('project_id', 'in', self.ids)], ['project_id'], ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in task_data)
        for my_project in self:
            my_project.task_count = result.get(my_project.id, 0)

    name = fields.Char("Name", index=True, required=True)
    description = fields.Char("description", required=False)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10, help="Gives the sequence order when displaying a list of Projects.")
    label_tasks = fields.Char(string='Use Tasks as', default='Tasks', help="Label used for the tasks of the project.", translate=True)
    tasks = fields.One2many('my_project.task', 'project_id', string="Task Activities")
    task_count = fields.Integer(compute='_compute_task_count', string="Task Count")
    task_ids = fields.One2many('my_project.task', 'project_id', string='Tasks',
                               domain=[])
    user_id = fields.Many2one('res.users', string='Project Manager', default=lambda self: self.env.user)
   
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'), 
    ],required = True, default = 'new')

    @api.onchange('start_date', 'end_date')
    def _onchange_dates(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            return {
                'warning': {
                    'title': "Date Error",
                    'message': "Start date must be less than end date!",
                }
            }

    @api.model
    def create(self, vals):
        self = self.with_context(mail_create_nosubscribe=True)
        if 'start_date' in vals and 'end_date' in vals:
            if vals['start_date'] > vals['end_date']:
                raise ValidationError("Start date must be less than end date!")
        project = super(MyProject, self).create(vals)
        return project
    def write(self, vals):
        if 'start_date' not in vals and 'end_date' in vals: 
            for project in self:
                if project.start_date.strftime('%Y-%m-%d')  > vals['end_date']: 
                    raise ValidationError("Start date must be less than end date!")
        if 'end_date' not in vals and 'start_date' in vals:
            for project in self:
                if project.end_date.strftime('%Y-%m-%d') < vals['start_date']: 
                    raise ValidationError("Start date must be less than end date!")
        if 'start_date' in vals and 'end_date' in vals:
            if vals['start_date'] > vals['end_date']:
                raise ValidationError("Start date must be less than end date!")
        res = super(MyProject, self).write(vals) if vals else True

        if 'active' in vals:
            self.with_context(active_test=False).mapped('tasks').write({'active': vals['active']})
        if vals.get('partner_id') or vals.get('privacy_visibility'):
            for project in self.filtered(lambda project: project.privacy_visibility == 'portal'):
                project.allowed_user_ids |= project.partner_id.user_ids

        return res

    def action_unlink(self):
        wizard = self.env['project.delete.wizard'].create({
            'project_ids': self.ids
        })

        return {
            'name': _('Confirmation'),
            'view_mode': 'form',
            'res_model': 'project.delete.wizard',
            'views': [(self.env.ref('project.project_delete_wizard_form').id, 'form')],
            'type': 'ir.actions.act_window',
            'res_id': wizard.id,
            'target': 'new',
            'context': self.env.context,
        }

    def unlink(self):
        # Check project is empty
        for project in self.with_context(active_test=False):
            if project.tasks:
                raise UserError(_('You cannot delete a project containing tasks. You can either archive it or first delete all of its tasks.'))
        result = super(MyProject, self).unlink()
        return result

class MyTask(models.Model):
    _name = "my_project.task"
    _description = "Task"
    _date_name = "date_assign"
    _order = "sequence, id desc"

    def _get_state_color(self):
        colors = {
            'to_do': 'gray',
            'in_progress': 'blue',
            'done': 'green',
        }
        return colors.get(self.state, 'white')

    name = fields.Char(string='Title', required=True, index=True)
    description = fields.Html(string='Description')
    sequence = fields.Integer(string='Sequence', index=True, default=10, help="Gives the sequence order when displaying a list of tasks.")
    create_date = fields.Datetime("Created On", readonly=True, index=True)
    write_date = fields.Datetime("Last Updated On", readonly=True, index=True)
    date_assign = fields.Datetime(string='Assigning Date', index=True, copy=False, readonly=True)
    project_id = fields.Many2one('my_project.project', string='Project', compute='_compute_project_id', store=True, readonly=False, index=True, change_default=True)
    user_id = fields.Many2one('res.users', string='Assigned to', default=lambda self: self.env.uid, index=True)
    manager_id = fields.Many2one('res.users', string='Project Manager', related='project_id.user_id', readonly=True)
    state = fields.Selection([
        ('to_do', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ], required=True, default='to_do')

    @api.model
    def write(self, vals):  
        for r in self:
            r.sequence += 1
        return super(MyTask, self).write(vals)

    def unlink(self):
        if any(self.mapped('recurrence_id')):
            # TODO: show a dialog to stop the recurrence
            raise UserError(_('You cannot delete recurring tasks. Please, disable the recurrence first.'))
        return super().unlink()

    def action_assign_to_me(self):
        self.write({'user_id': self.env.user.id})

    def _rating_get_parent_field_name(self):
        return 'project_id'
