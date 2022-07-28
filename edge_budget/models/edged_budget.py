from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv.expression import AND
from odoo.exceptions import UserError

class EdgedBudgetPost(models.Model):
    _name = "edged.budget.post"
    _order = "name"
    _description = "Sales Budgetary Position"

    name = fields.Char('Name', required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True,
        default=lambda self: self.env.company)


    @api.model
    def create(self, vals):
        return super(SalesBudgetPost, self).create(vals)

    def write(self, vals):
        return super(SalesBudgetPost, self).write(vals)


class EdgedBudget(models.Model):
    _name = "edged.budget"
    _description = "Edged Budget"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Budget Name', required=True, states={'done': [('readonly', True)]})
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user)
    date_from = fields.Date('Start Date', required=True, states={'done': [('readonly', True)]})
    date_to = fields.Date('End Date', required=True, states={'done': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('validate', 'Validated'),
        ('done', 'Done')
        ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, tracking=True)
    edged_budget_line = fields.One2many('edged.budget.lines', 'edged_budget_id', 'Edged Budget Lines',
        states={'done': [('readonly', True)]}, copy=True)
    company_id = fields.Many2one('res.company', 'Company', required=True,
        default=lambda self: self.env.company)
    monthly_sales_target = fields.Float('Monthly Sales Target', default=570000.00, required="1")

    def action_budget_confirm(self):
        self.write({'state': 'confirm'})

    def action_budget_draft(self):
        self.write({'state': 'draft'})

    def action_budget_validate(self):
        self.write({'state': 'validate'})

    def action_budget_cancel(self):
        self.write({'state': 'cancel'})

    def action_budget_done(self):
        self.write({'state': 'done'})


class EdgedBudgetLines(models.Model):
    _name = "edged.budget.lines"
    _description = "Edged Budget Line"

    edged_budget_id = fields.Many2one('edged.budget', 'Edged Budget', ondelete='cascade', index=True)
    date_from = fields.Date('Start Date', related="edged_budget_id.date_from")
    date_to = fields.Date('End Date', related="edged_budget_id.date_to")
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user)
    account_id = fields.Many2one('account.account', string="Account")
    budget_amount = fields.Float('Budget Amount')
    achieved_budget = fields.Float('Achieved', compute=lambda self: self._compute_line_archived())

    company_id = fields.Many2one(related='edged_budget_id.company_id', comodel_name='res.company',
        string='Company', store=True, readonly=True)
    edged_budget_state = fields.Selection(related='edged_budget_id.state', string='Edged Budget State', store=True, readonly=True)

    @api.depends("account_id", "date_from", "date_to")
    @api.model
    def _compute_line_archived(self):
        for record in self:
            objinvln = self.env['account.move.line'].search(
                [('account_id', '=', record.account_id.id), ('move_id.type', 'in', ('out_invoice','out_refund')),
                 ('move_id.state', 'in', ('posted','reconciled'))
                    ,('move_id.invoice_date', '>=', record.date_from),('move_id.invoice_date', '<=', record.date_to)
                 ])
            if objinvln:
                for salrec in objinvln:
                    record.achieved_budget += salrec.price_total
