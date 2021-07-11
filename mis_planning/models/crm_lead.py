# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.tools.misc import formatLang
from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
class MisCrmStage(models.Model):
    _inherit = 'crm.stage'
    is_planning = fields.Boolean('Is Planning')
    is_closed = fields.Boolean('Is Closed')
    is_approval_reqired = fields.Boolean('Is Approval Required', default=False)

class MisCRMLead(models.Model):
    _inherit = 'crm.lead'
    _order ='write_date, priority desc, id desc'

    planning_id=fields.Many2one('planning.slot', string='Planning ID', readonly=True, store=True)
    unit_number = fields.Char(string='Unit No')
    area_id = fields.Many2one('mis.area', string='Area')
    is_won = fields.Boolean('Is Won', related='stage_id.is_won')
    is_closed = fields.Boolean('Is Closed', related='stage_id.is_closed')
    is_planning = fields.Boolean('Is Planning', related='stage_id.is_planning')
    building_name = fields.Char(string='Building Name')
    job_team_id = fields.Many2one('planning.role', string='Job Team')
    job_startdate = fields.Datetime(string='Job Start Date')
    job_enddate = fields.Datetime(string='Job End Date')
    is_approve_status = fields.Integer('Approval Status', default=0)
    is_transfer = fields.Boolean('Is Transfer', default=False)
    is_system = fields.Boolean('Is System', default=True)
    won_date = fields.Datetime('Won Date')



    job_totalhours = fields.Float(string='Job Total Hours', default=0, compute='_compute_job_totalhours', store=True)

    scope = fields.Text(string='Scope')

    def action_transfer2planning(self):
        self.is_transfer=True
        self._checkforoverlap()
        for rec in self:
            create_vals={
                'name': rec.name,
                'crm_id': rec.id ,
                'role_id': rec.job_team_id.id,
                'start_datetime': rec.job_startdate,
                'end_datetime': rec.job_enddate,
           }

        objplanning = self.env['planning.slot'].create(create_vals)
        self.planning_id=objplanning.id
        objstate = self.env['crm.stage'].search([('is_planning', '=', True)])
        for rec in objstate:
            self.stage_id=rec.id

    def _checkforoverlap(self):
        #raise UserError(self.job_startdate)
        objoverlapstart = self.env['planning.slot'].search(
            [('role_id', '=', self.job_team_id.id), ('start_datetime', '>=', self.job_startdate),
             ('end_datetime', '<=', self.job_startdate)])
        if objoverlapstart:
            raise UserError('Schedule Overlapped for the selected team')
        objoverlapend = self.env['planning.slot'].search(
            [('role_id', '=', self.job_team_id.id), ('start_datetime', '>=', self.job_enddate),
             ('end_datetime', '<=', self.job_enddate)])
        if objoverlapend:
            raise UserError('Schedule Overlapped for the selected team')

        #raise UserError('Transferred to Planning')
    # @api.onchange('job_startdate')
    # def _change_start_date(self):
    #     for rec in self:
    #         if rec.job_startdate:
    #             if not rec.job_enddate:
    #                 dt_temp=rec.job_startdate
    #                 rec.job_enddate=dt_temp.timedelta(hours=1)
    @api.onchange('job_startdate')
    def _onchange_startdate(self):
        for rec in self:
            stdate =rec.job_startdate
            stdate=stdate + timedelta(hours = 1)
            rec.job_enddate=stdate


    @api.depends('job_startdate', 'job_enddate')
    def _compute_job_totalhours(self):

        for wktime in self:

            if wktime.job_startdate and wktime.job_enddate:
                total_hr=(wktime.job_enddate - wktime.job_startdate).total_seconds()/ 3600
                wktime.job_totalhours= total_hr

    def popup_planning(self):
        self.ensure_one()

        return {
            'name': _('Schedule'),
            'type': 'ir.actions.act_window',
            'view_mode': 'gantt',
            'res_model': 'planning.slot',
            'target': 'new',
            'context': {
                'search_default_group_by_role': True
            }
        }

    def button_approve(self):

        self.ensure_one()

        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('mis_planning', 'email_template_crm_approved')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'crm.lead',
            'active_model': 'crm.lead',
            'active_id': self.ids[0],
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
        })

        if {'default_template_id', 'default_model', 'default_res_id'} <= ctx.keys():
            template = self.env['mail.template'].browse(ctx['default_template_id'])

        ctx['model_description'] = _('Approved')
        self.is_approve_status = 3

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


    def write(self, vals):

        #current_stage_id =self.stage_id.id

        if self.stage_id.is_closed:
             raise UserError('Access denied!, Closed stage cannot be changed')
        if 'stage_id' in vals:
            nstage_id = self.env['crm.stage'].browse(vals['stage_id'])
            if nstage_id.is_won:
                if not self.partner_id.mobile and not self.partner_id.phone:
                    raise UserError('Please Enter customer Phone or Mobile Number')
                objsale = self.env['sale.order'].search(
                    [('state', '=', 'sale'), ('opportunity_id', '=', self.id)])
                if len(objsale)==0:
                    raise UserError('Cannot find confirmed sales order')
                vals.update({'won_date': fields.Datetime.now()})

            if self.stage_id.sequence < nstage_id.sequence  and nstage_id.is_planning:
                if self.is_transfer != True:
                    raise UserError('Cannot drag and drop, please use transfer to planning button')

            elif self.stage_id.is_planning and nstage_id.is_closed and self.is_system:
                raise UserError('Cannot drag and drop, transferred planning to closed')


            if self.is_approve_status != 3:
                # if self.stage_id.id > nstage_id.id:
                if self.stage_id.sequence > nstage_id.sequence and  self.stage_id.is_approval_reqired==True  and self.env.uid not in (2,6):
                    raise UserError('Access denied!, Please contact administrator to change the stage')
                # elif self.stage_id.id > 4 and nstage_id.id < 5 and self.env.uid != 2:
                #     raise UserError('Access denied!, Please contact administrator to change the stage')
            if self.stage_id.id != nstage_id.id:
                vals.update({'is_approve_status': 0})

            # if self.stage_id.id == 4 and nstage_id.id == 5:
            #     if self.is_transfer!=True:
            #         raise UserError('Cannot drag and drop, please use transfer to planning button')
            #
            # if self.is_approve_status != 3:
            #     #if self.stage_id.id > nstage_id.id:
            #     if self.stage_id.id > 3 and  nstage_id.id < 4 and self.env.uid != 2:
            #         raise UserError('Access denied!, Please contact administrator to change the stage')
            #     elif self.stage_id.id > 4 and  nstage_id.id < 5 and self.env.uid != 2:
            #         raise UserError('Access denied!, Please contact administrator to change the stage')
            # if self.stage_id.id!= nstage_id.id:
            #     vals.update({'is_approve_status': 0})

        if vals.get('website'):
            vals['website'] = self.env['res.partner']._clean_website(vals['website'])
        # stage change: update date_last_stage_update

        if 'stage_id' in vals:
            vals['date_last_stage_update'] = fields.Datetime.now()
            stage_id = self.env['crm.stage'].browse(vals['stage_id'])
            if stage_id.is_won:
                vals.update({'probability': 100})
        # Only write the 'date_open' if no salesperson was assigned.
        if vals.get('user_id') and 'date_open' not in vals and not self.mapped('user_id'):
            vals['date_open'] = fields.Datetime.now()
        # stage change with new stage: update probability and date_closed
        if vals.get('probability', 0) >= 100 or not vals.get('active', True):
            vals['date_closed'] = fields.Datetime.now()
        elif 'probability' in vals:
            vals['date_closed'] = False
        if vals.get('user_id') and 'date_open' not in vals:
            vals['date_open'] = fields.Datetime.now()


        write_result = super(MisCRMLead, self).write(vals)
#        raise UserError(str(current_stage_id) + str(self.stage_id.id))

        if self.planning_id:
            if self.stage_id.id <4:
                self.planning_id.unlink()
            else:
                if self.planning_id.is_invoice==False:
                    self._checkforoverlap()
                    self.planning_id.update({'start_datetime': self.job_startdate,'end_datetime': self.job_enddate})


#        self.is_approve_status=0

        # Compute new automated_probability (and, eventually, probability) for each lead separately
        if self._should_update_probability(vals):
            self._update_probability()

        return write_result

    # def button_approve(self, force=False):
    #     self.write({'is_approve': True})
    #     return {}


    def action_send_email(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('mis_planning', 'email_template_crm_approval')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'crm.lead',
            'active_model': 'crm.lead',
            'active_id': self.ids[0],
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
        })

        if {'default_template_id', 'default_model', 'default_res_id'} <= ctx.keys():
            template = self.env['mail.template'].browse(ctx['default_template_id'])

        ctx['model_description'] = _('Delivery Order')
        self.is_approve_status = 1

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



class MisSalesOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):

        result = super(MisSalesOrder, self).create(vals)
        if self.opportunity_id:
            total_amount = 0.0
            objsale = self.env['sale.order'].search([('state', '!=', 'cancel'), ('opportunity_id', '=', self.opportunity_id.id)])
            for rec in objsale:
                total_amount+=rec.amount_total
            self._cr.execute(
                'update crm_lead set planned_revenue=%s,expected_revenue=%s*probability/100 where id=%s',(total_amount,total_amount,self.opportunity_id.id))
        return result

    def write(self, values):
        result = super(MisSalesOrder, self).write(values)
        if self.opportunity_id:
            total_amount = 0.0
            objsale = self.env['sale.order'].search([('state', '!=', 'cancel'), ('opportunity_id', '=', self.opportunity_id.id)])
            for rec in objsale:
                total_amount += rec.amount_total
            self._cr.execute(
                'update crm_lead set planned_revenue=%s,expected_revenue=%s*probability/100 where id=%s', (total_amount,
                total_amount, self.opportunity_id.id))


