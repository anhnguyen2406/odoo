# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class MyProject(models.Model):
    _name = "my_project.project"
    _description = "My Project"
    _order = "sequence, name, id"

    def _compute_task_count(self):
        task_data = self.env['my_project.task'].read_group([('project_id', 'in', self.ids)], ['project_id'], ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in task_data)
        for my_project in self:
            my_project.task_count = result.get(my_project.id, 0)

    @api.depends('tasks.state')
    def _compute_task_done_count(self):
        task_done_data = self.env['my_project.task'].read_group(['&',('project_id', 'in', self.ids),('state','=','done')], ['project_id'], ['project_id'])
        task_process_data = self.env['my_project.task'].read_group(['&',('project_id', 'in', self.ids),('state','=','in_progress')], ['project_id'], ['project_id'])
        result_done = dict((data['project_id'][0], data['project_id_count']) for data in task_done_data)
        result_progress = dict((data['project_id'][0], data['project_id_count']) for data in task_process_data)
        for my_project in self:
            my_project.task_done_count = result_done.get(my_project.id, 0)
            my_project.task_progress_count = result_progress.get(my_project.id,0)
            if my_project.task_done_count == 0 and  my_project.task_progress_count == 0:
                my_project.state = 'new'
            if my_project.task_count and my_project.task_count == my_project.task_done_count:
                my_project.state = 'completed'
            if (my_project.task_count > my_project.task_done_count and my_project.task_done_count > 0) or  my_project.task_progress_count > 0:
                my_project.state = 'in_progress'

    name = fields.Char("Name", index=True, required=True)
    description = fields.Char("description", required=False)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    label_tasks = fields.Char(string='Use Tasks as', default='Tasks', help="Label used for the tasks of the project.", translate=True)
    tasks = fields.One2many('my_project.task', 'project_id', string="" )
    task_count = fields.Integer(compute='_compute_task_count', string="Task Count")
    task_done_count = fields.Integer(compute='_compute_task_done_count', string="Task Done")
    task_progress_count = fields.Integer(compute='_compute_task_done_count', string="Task In Progress")
    user_id = fields.Many2one('res.users', string='Project Manager', default=lambda self: self.env.user)
   
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
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
        return super(MyProject, self).write(vals)
