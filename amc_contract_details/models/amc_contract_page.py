# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
import time



class AmcContract(models.Model):
    _name = 'amc.contract'
    _inherit = ['mail.thread.cc','mail.activity.mixin']


    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), track_visibility='onchange')
    contract_name = fields.Char()
    partner_id = fields.Many2one('res.partner', string='Partner', track_visibility='onchange')
    sales_agent_id = fields.Many2one('res.users', string='Sales Agent', default=lambda self: self.env.user, track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company Name', default=lambda self: self.env.company.id, track_visibility='onchange')
    start_date = fields.Datetime(string='Start Date', track_visibility='onchange', store=True, default=lambda self: fields.Datetime.to_string(datetime.now().replace(hour=9, minute=00, second=00)))
    end_date = fields.Datetime(string='End Date', track_visibility='onchange', store=True)
    date = fields.Datetime(string='Date', track_visibility='onchange', default=lambda self: fields.Datetime.to_string(datetime.now().replace(hour=11, minute=00, second=00)))
    total_amount = fields.Float(compute='_get_total_amount', string='Total Amount', track_visibility='onchange', store=True)
    total_material_cost = fields.Float(string='Total Callout Material Cost', store=True)
    total_callout_amount = fields.Float(string='Total Callout Amount', store=True)

    contract_state = fields.Selection([('draft', 'Draft'), ('cancel', 'Cancelled'),
                              ('confirm', 'Confirmed'),('valid', 'Validated'), ('done', 'Done'), ('expired', 'Expired')], 
                              default='draft', string="Contract Status", copy=False, track_visibility='onchange')

    contract_stage = fields.Selection([('active', 'Active'), ('to_expire', 'Above To Expire'), ('expired', 'Expired')], string="Contract Stage", compute='_get_contract_stage', store=True)

    contract_line_ids = fields.One2many('amc.contract.line', 'contract_id', string="Contract Lines", track_visibility='onchange')
    callout_line_ids = fields.One2many('callout.contract.line', 'contract_id', string="Callout Lines", compute='_get_total_material_cost', track_visibility='onchange',  store=True)
    description = fields.Text(string='Description', track_visibility='onchange')
    area_id = fields.Many2one('mis.area', string='Area', track_visibility='onchange')
    unit_no = fields.Char(string='Unit No', track_visibility='onchange')
    building_name = fields.Char(string='Building Name', track_visibility='onchange')
    total_callout = fields.Integer(string='Total Callout', store=True)
    total_paid = fields.Float(compute='_get_total_invoice_details',string='Total Paid Amount', store=True)
    total_due = fields.Float(compute='_get_total_invoice_details',string='Total Due Amount', store=True)
    subtotal_amount = fields.Float(compute='_get_total_invoice_details',string='Subtotal Amount', store=True)
    total_callout_no = fields.Integer(string='Assigned Callout')
    used_callout = fields.Integer(compute='_get_callout_count', string='Used Callout', store=True)
    balance_callout = fields.Integer(compute='_get_callout_count', string='Balance Callout', store=True)
    partner_mobile = fields.Char(string='Partner Mobile', related='partner_id.mobile', store=True)


    @api.depends('callout_line_ids')
    def _get_callout_count(self):
        for each in self:
            if each.callout_line_ids and each.total_callout_no > 0:
                each.used_callout = len(each.callout_line_ids)
                each.balance_callout = each.total_callout_no - len(each.callout_line_ids)
            else:
                each.used_callout = 0
                each.balance_callout = 0

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('amc.contract') or _('New')
            contact_tag = self.env['res.partner.category'].search([('is_amc', '=', True)])
        res = super(AmcContract, self).create(vals)
        res.partner_id['category_id'] = [contact_tag.id]
        return res


    def action_confirm(self):
        if self.contract_line_ids:
            if self.contract_state == 'draft':
                self.contract_state = 'confirm'
                for contract_lines_id in self.contract_line_ids:
                    if not contract_lines_id.lead_id:
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
                        'planned_revenue': contract_lines_id.amount,
                        'job_startdate': str(contract_lines_id.date) + ' 09:00:00',
                        'job_enddate': str(contract_lines_id.date) + ' 11:00:00',
                        'cst_nextactivity_date': contract_lines_id.date,
                        'description' : 'AMC Contract '  + str(self.name),
                        'source_id': 40})
                        contract_lines_id.lead_id = lead_id.id

                        sale_order_id = self.env['sale.order'].create({
                        'partner_id': contract_lines_id.contract_id.partner_id.id,
                        'opportunity_id': lead_id.id,
                        'date_order': fields.Datetime.now(),
                        'order_line': [(0, 0, {'product_id': contract_lines_id.product_id.id,
                                               'price_unit': contract_lines_id.amount,
                                               'product_uom': contract_lines_id.product_id.uom_id.id,
                                               })],
                        })

                        sale_order_id.action_confirm()
                        lead_id.action_set_won_rainbowman()
                        lead_id.action_transfer2planning()

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
            'res_model': 'callout.contract.line',
            'view_id': self.env.ref('amc_contract_details.callout_line_view_form').id,
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
       
    def update_contract_stage_job(self):
        contract_ids = self.env['amc.contract'].search([]).filtered(lambda o: \
            (o.contract_stage not in ['expired']))
        for contract_id in contract_ids:
            if contract_id.end_date:
                today = datetime.today()
                remaining_days = contract_id.end_date - today
                if remaining_days.days > 30:
                    contract_id.contract_stage = 'active'
                elif remaining_days.days < 0:
                    contract_id.contract_stage = 'expired'
                else:
                    contract_id.contract_stage = 'to_expire'

    # def create_lead_cron_job(self):
    #     contract_lines_ids = self.env['amc.contract.line'].search([]).filtered(lambda o: \
    #         not o.lead_id and (o.date == fields.Date.today()) and (o.contract_id.contract_state not in ['cancel', 'draft']))
    #     for contract_lines_id in contract_lines_ids:
    #         for rec in self.env['amc.contract'].search([('id','=',contract_lines_id.contract_id.id)]):
    #             amount = str(contract_lines_id.amount)
    #             lead_name = "AMC-{0}-{1}-{2}".format(contract_lines_id.product_id.name, amount, contract_lines_id.contract_id.company_id.name)
    #             lead_id = self.env['crm.lead'].create({
    #             'name': lead_name,
    #             'partner_id': contract_lines_id.contract_id.partner_id.id,
    #             'email_from': contract_lines_id.contract_id.partner_id.email,
    #             'user_id' : contract_lines_id.contract_id.sales_agent_id.id,
    #             'area_id' : contract_lines_id.contract_id.area_id.id,
    #             'unit_number' : contract_lines_id.contract_id.unit_no,
    #             'building_name' : contract_lines_id.contract_id.building_name,
    #             'scope' : contract_lines_id.scope,
    #             'planned_revenue': contract_lines_id.amount,
    #             'job_startdate': rec.start_date,
    #             'job_enddate': rec.end_date,
    #             'cst_nextactivity_date': contract_lines_id.date,
    #             'source_id': 2})
    #             contract_lines_id.lead_id = lead_id.id

    #             sale_order_id = self.env['sale.order'].create({
    #             'partner_id': contract_lines_id.contract_id.partner_id.id,
    #             'opportunity_id': lead_id.id,
    #             'date_order': fields.Datetime.now(),
    #             'order_line': [(0, 0, {'product_id': contract_lines_id.product_id.id, 
    #                                    'price_unit': contract_lines_id.amount, 
    #                                    'product_uom': contract_lines_id.product_id.uom_id.id,})],
    #             })
    #             sale_order_id.action_confirm()
    #             lead_id.action_set_won_rainbowman()
    #             lead_id.action_transfer2planning()


    @api.depends('contract_line_ids.amount')
    def _get_total_amount(self):
        total=[]
        if not self.contract_line_ids:
                    self.total_amount = 0.00
        else: 
            for each in self:
                for value in each.contract_line_ids:
                    total.append(value.amount)
                    self.total_amount = sum(total)

    @api.depends('contract_line_ids.planning_id','contract_line_ids', 'contract_line_ids.lead_id.invoice_id.amount_total','contract_line_ids.lead_id.invoice_id.amount_residual')
    def _get_total_invoice_details(self):
        total_paid=[]
        total_due=[]
        subtotal=[]
        if not self.contract_line_ids.lead_id.invoice_id:
                    self.total_paid = 0.00
                    self.total_due = 0.00
                    self.subtotal_amount = 0.00
        else: 
            for each in self:
                for value in each.contract_line_ids:
                    total_paid.append(value.lead_id.invoice_id.amount_total - value.lead_id.invoice_id.amount_residual)
                    self.total_paid = sum(total_paid)
                    total_due.append(value.lead_id.invoice_id.amount_residual)
                    self.total_due = sum(total_due)
                    subtotal.append(value.planning_id.revenue)
                    self.subtotal_amount = sum(subtotal)

    @api.depends('callout_line_ids')
    def _get_total_material_cost(self):
        total=[]
        total_callamt=[]
        if not self.callout_line_ids:
                    self.total_material_cost = 0.00
                    self.total_callout_amount=0.00
        else:
            self.total_callout = len(self.callout_line_ids)
            for each in self:
                for value in each.callout_line_ids:
                    total.append(value.material_cost)
                    total_callamt.append(value.amount)
                    self.total_material_cost = sum(total)
                    self.total_callout_amount =  sum(total_callamt)

    @api.depends('end_date')
    def _get_contract_stage(self):
        if self.end_date:
            today = datetime.today()
            remaining_days = self.end_date - today
            if remaining_days.days > 30:
                self.contract_stage = 'active'
            elif remaining_days.days < 0:
                self.contract_stage = 'expired'
            else:
                self.contract_stage = 'to_expire'

        


class AmcContractLine(models.Model):
    _name = 'amc.contract.line'


    product_id = fields.Many2one('product.product', string='Product', required=True, track_visibility='onchange',
        domain=[('type', '=', 'service')])
    amount = fields.Float(string='Amount', track_visibility='onchange', compute='_compute_amc_amount', inverse='_inverse_amc_amount', store=True)
    date = fields.Date(string='Date', track_visibility='onchange', required=True)
    scope = fields.Text(string='Scope', track_visibility='onchange')
    contract_id = fields.Many2one('amc.contract')
    lead_id = fields.Many2one('crm.lead', string='CRM', track_visibility='onchange')
    planning_id = fields.Many2one('planning.slot', string='Planning', track_visibility='onchange', 
        related='lead_id.planning_id', store=True)
    # invoice_id = fields.Many2one('account.move', string='Invoice', compute='_get_invoice_id', store=True)
    payment_id = fields.Many2one('account.payment', string='Payment', related='lead_id.payment_id', store=True)

    @api.depends('lead_id.planned_revenue')
    def _compute_amc_amount(self):
        for amc_line in self:
            if amc_line.lead_id:
                amc_line.amount = amc_line.lead_id.planned_revenue 

    def _inverse_amc_amount(self):
        for amc_line in self:
            if amc_line.lead_id:
                amc_line.amount = amc_line.lead_id.planned_revenue 
    

class CalloutContractLine(models.Model):
    _name = 'callout.contract.line'


    product_id = fields.Many2one('product.product', string='Product', track_visibility='onchange',
        domain=[('type', '=', 'service')])
    amount = fields.Float(string='Amount', track_visibility='onchange', compute='_compute_callout_amount', inverse='_inverse_callout_amount', store=True)
    date = fields.Datetime(string='Date', track_visibility='onchange', default=time.strftime('%Y-%m-%d 09:00:00'))
    scope = fields.Text(string='Scope', track_visibility='onchange')
    contract_id = fields.Many2one('amc.contract', default=lambda self: self.id)
    lead_id = fields.Many2one('crm.lead', string='CRM', track_visibility='onchange')
    planning_id = fields.Many2one('planning.slot', string='Planning', track_visibility='onchange', related='lead_id.planning_id', store=True)
    hours = fields.Integer(string='Duration in hours')
    sales_team = fields.Many2one('crm.team', string='Sales Team')
    start_date = fields.Datetime(string='Start Date', track_visibility='onchange', default=lambda self: fields.Datetime.to_string(datetime.now().replace(hour=9, minute=00, second=00)))
    end_date = fields.Datetime(string='End Date', track_visibility='onchange', default=lambda self: fields.Datetime.to_string(datetime.now().replace(hour=9, minute=00, second=00)))
    material_cost = fields.Float(string='Material Cost', track_visibility='onchange')
    # invoice_id = fields.Many2one('account.move', string='Invoice', track_visibility='onchange')
    # payment_id = fields.Many2one('account.payment', string='Payment', related='lead_id.payment_id', store=True)


    @api.depends('lead_id.planned_revenue')
    def _compute_callout_amount(self):
        for callout_line in self:
            if callout_line.lead_id:
                callout_line.amount = callout_line.lead_id.planned_revenue 

    def _inverse_callout_amount(self):
        for callout_line in self:
            if callout_line.lead_id:
                callout_line.amount = callout_line.lead_id.planned_revenue 

    def action_create_crm_planning(self):
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
            'planned_revenue': self.amount,
            'job_startdate': self.start_date,
            'job_enddate': self.end_date,
            'cst_nextactivity_date': self.date,
            'source_id': 30})
            self.lead_id = lead_id.id
            sale_order_id = self.env['sale.order'].create({
            'partner_id': self.contract_id.partner_id.id,
            'opportunity_id': lead_id.id,
            'date_order': fields.Datetime.now(),
            'order_line': [(0, 0, {'product_id': self.product_id.id, 
                                   'price_unit': self.amount, 
                                   'product_uom': self.product_id.uom_id.id,})],
            })
            sale_order_id.action_confirm()
            lead_id.action_set_won_rainbowman()
            lead_id.action_transfer2planning()
