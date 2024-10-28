from odoo import  fields, models

class MyTask(models.Model):
    _name = "my_project.task"
    _description = "Task"
    _order = "sequence, id desc"

    name = fields.Char(string='Title', required=True, index=True)
    description = fields.Html(string='Description')
    sequence = fields.Integer(string='Sequence', index=True, default=10, help="Gives the sequence order when displaying a list of tasks.")
    create_date = fields.Datetime("Created On", readonly=True, index=True)
    write_date = fields.Datetime("Last Updated On", readonly=True, index=True)
    date_assign = fields.Datetime(string='Assigning Date', index=True, copy=False, readonly=True)
    project_id = fields.Many2one('my_project.project', string='Project', readonly=False, index=True, change_default=True, ondelete ='cascade')
    user_id = fields.Many2one('res.users', string='Assigned to', default=lambda self: self.env.uid, index=True)
    manager_id = fields.Many2one('res.users', string='Project Manager', related='project_id.user_id', readonly=True)
    state = fields.Selection([
        ('to_do', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ], required=True, default='to_do')

    def write(self, vals):  
        result = super(MyTask, self).write(vals)
        return result

    def unlink(self):
        return super(MyTask, self).unlink()