# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime



class AmcContract(models.Model):
    _name = 'amc.contract'
    _inherit = ['mail.thread.cc','mail.activity.mixin']


    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), track_visibility='onchange')
    contract_name = fields.Char()
    partner_id = fields.Many2one('res.partner', string='Partner', track_visibility='onchange')
    sales_agent_id = fields.Many2one('res.users', string='Sales Agent', default=lambda self: self.env.user, track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company Name', default=lambda self: self.env.company.id, track_visibility='onchange')
    start_date = fields.Date(string='Start Date', track_visibility='onchange')
    end_date = fields.Date(string='End Date', track_visibility='onchange')
    date = fields.Date(string='Date', track_visibility='onchange', default=datetime.today())
    total_amount = fields.Float(compute='_get_total_amount', string='Total Amount', track_visibility='onchange', store=True)
    contract_state = fields.Selection([('draft', 'Draft'), ('cancel', 'Cancelled'),
                              ('confirm', 'Confirmed'),('valid', 'Validated'), ('done', 'Done'), ('expired', 'Expired')], 
                              default='draft', string="Contract Status", track_visibility='onchange')
    contract_line_ids = fields.One2many('amc.contract.line', 'contract_id', string="Contract Lines", track_visibility='onchange')
    callout_line_ids = fields.One2many('callback.contract.line', 'contract_id', string="Callout Lines", track_visibility='onchange')
    description = fields.Text(string='Description', track_visibility='onchange')
    area_id = fields.Many2one('mis.area', string='Area', track_visibility='onchange')
    unit_no = fields.Char(string='Unit No', track_visibility='onchange')
    building_name = fields.Char(string='Building Name', track_visibility='onchange')


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('amc.contract') or _('New')
        res = super(AmcContract, self).create(vals)
        return res


    def action_confirm(self):
        if self.contract_state == 'draft':
            self.contract_state = 'confirm'


    def action_cancel(self):
        if self.contract_state in ('confirm', 'valid', 'done'):
            self.contract_state = 'cancel'

    def action_set_draft(self):
        if self.contract_state == 'cancel':
            self.contract_state = 'draft'

    def action_callout(self):

        return {

            'name': 'AMC Details',
            'view_mode': 'form',
            'res_model': 'callback.contract.line',
            'view_id': self.env.ref('amc_contract_details.callback_line_view_form').id,
            'context': {'default_contract_id': self.id},
            'target': 'new',
            'type': 'ir.actions.act_window',
            }



    def action_send_by_email(self):
       self.ensure_one()
       ir_model_data = self.env['ir.model.data']
       template = self.env['mail.template'].search([('name', '=', 'AMC Contract: Send by email')])
       try:
           template_id = \
               ir_model_data.get_object_reference('amc_contract', 'amc_contract_email_template')[1]
       except ValueError:
           template_id = False
       try:
           compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
       except ValueError:
           compose_form_id = False
       ctx = {
           'default_model': 'amc.contract',
           'default_res_id': self.ids[0],
           'default_use_template': bool(template_id),
           'default_template_id': template.id,
           'default_composition_mode': 'comment',
       }
       return {
           'name': _('Compose Email'),
           'type': 'ir.actions.act_window',
           'view_mode': 'form',
           'res_model': 'mail.compose.message',
           'views': [(compose_form_id, 'form')],
           'view_id': compose_form_id,
           'target': 'new',
           'context': ctx,
       }
       
    def create_lead_cron_job(self):
        contract_lines_ids = self.env['amc.contract.line'].search([]).filtered(lambda o: \
            not o.lead_id and (o.date == fields.Date.today()) and (o.contract_id.contract_state not in ['cancel', 'draft']))
        for contract_lines_id in contract_lines_ids:
            amount = str(contract_lines_id.amount)
            lead_name = "AMC-{0}-{1}-{2}".format(contract_lines_id.product_id.name, amount, contract_lines_id.contract_id.company_id.name)
            lead_id = self.env['crm.lead'].create({
            'name': lead_name,
            'partner_id': contract_lines_id.contract_id.partner_id.id,
            'email_from': contract_lines_id.contract_id.partner_id.email,
            'user_id' : contract_lines_id.contract_id.sales_agent_id.id,
            'area_id' : contract_lines_id.contract_id.area_id.id,
            'unit_number' : contract_lines_id.contract_id.unit_no,
            'building_name' : contract_lines_id.contract_id.building_name,
            'scope' : contract_lines_id.scope,
            'planned_revenue': contract_lines_id.amount})
            contract_lines_id.lead_id = lead_id.id

    @api.depends('contract_line_ids.amount')
    def _get_total_amount(self):
        total=[]
        for each in self:
            for value in each.contract_line_ids:
                total.append(value.amount)
                self.total_amount = sum(total)


class AmcContractLine(models.Model):
    _name = 'amc.contract.line'


    product_id = fields.Many2one('product.template', string='Product', track_visibility='onchange', 
        domain=[('type', '=', 'service')])
    amount = fields.Float(string='Amount', track_visibility='onchange')
    date = fields.Date(string='Date', track_visibility='onchange')
    scope = fields.Text(string='Scope', track_visibility='onchange')
    contract_id = fields.Many2one('amc.contract')
    lead_id = fields.Many2one('crm.lead', string='CRM', track_visibility='onchange')
    planning_id = fields.Many2one('planning.slot', string='Planning', track_visibility='onchange', 
        related='lead_id.planning_id', store=True)
    # invoice_id = fields.Many2one('account.move', string='Invoice', track_visibility='onchange')
    # payment_id = fields.Many2one('account.payment', string='Payment', track_visibility='onchange')
   
class CallbackContractLine(models.Model):
    _name = 'callback.contract.line'


    product_id = fields.Many2one('product.template', string='Product', track_visibility='onchange', 
        domain=[('type', '=', 'service')])
    amount = fields.Float(string='Amount', track_visibility='onchange')
    date = fields.Date(string='Date', track_visibility='onchange')
    scope = fields.Text(string='Scope', track_visibility='onchange')
    contract_id = fields.Many2one('amc.contract', default=lambda self: self.id)
    lead_id = fields.Many2one('crm.lead', string='CRM', track_visibility='onchange')
    planning_id = fields.Many2one('planning.slot', string='Planning', track_visibility='onchange', related='lead_id.planning_id', store=True)
    hours = fields.Integer(string='Duration in hours')
    sales_team = fields.Many2one('crm.team', string='Sales Team')
    start_date = fields.Date(string='Start Date', track_visibility='onchange')
    end_date = fields.Date(string='End Date', track_visibility='onchange')
    # invoice_id = fields.Many2one('account.move', string='Invoice', track_visibility='onchange')
    # payment_id = fields.Many2one('account.payment', string='Payment', track_visibility='onchange')

    def action_create_crm(self):
        if not self.lead_id:
            amount = str(self.amount)
            lead_name = "AMC-{0}-{1}-{2}".format(self.product_id.name, amount, self.contract_id.company_id.name)
            lead_id = self.env['crm.lead'].create({
            'name': lead_name,
            'partner_id': self.contract_id.partner_id.id,
            'email_from': self.contract_id.partner_id.email,
            'user_id' : self.contract_id.sales_agent_id.id,
            'area_id' : self.contract_id.area_id.id,
            'unit_number' : self.contract_id.unit_no,
            'building_name' : self.contract_id.building_name,
            'scope' : self.scope,
            'planned_revenue': self.amount})
            self.lead_id = lead_id.id

