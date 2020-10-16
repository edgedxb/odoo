# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.tools.misc import formatLang
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
import logging
import pytz
import uuid
from math import ceil

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval
from odoo.tools import format_time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class MisPlanningStatus(models.Model):
    _name = 'mis.planning.status'
    _description = 'Planning Status'

    name = fields.Char(string='Status')
    is_invoice= fields.Boolean(string='Is Invoice?')

    _sql_constraints = [
        ('unique_planningstatus',
         'unique(name)', 'Planning Status should be unique within a category!')]

class MisPlanning(models.Model):
    _inherit = 'planning.slot'

    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True,
                                       relation="res.currency")

    crm_id = fields.Many2one('crm.lead', string='CRM')
    partner_id = fields.Many2one('res.partner', related='crm_id.partner_id', string='Customer')
    email = fields.Char(related='crm_id.email_from', string='Email')
    phone = fields.Char(related='crm_id.partner_address_phone', string='Phone')
    revenue = fields.Monetary(related='crm_id.planned_revenue', currency_field='company_currency', string='Revenue')
    area_id = fields.Many2one('mis.area', related='crm_id.area_id', string='Area')
    unit_number = fields.Char(related='crm_id.unit_number', string='Unit No')
    building_name = fields.Char(related='crm_id.building_name', string='Building Name')
    scope = fields.Text(related='crm_id.scope', string='Scope')
    job_status_id = fields.Many2one('mis.planning.status')
    journal_id = fields.Many2one('account.journal', domain=[('type', 'in', ('bank','cash'))], string="Payment")
    paid_amount = fields.Float(string='Amount', default=0.0)
    is_invoice = fields.Boolean(string='Is Invoice?', related='job_status_id.is_invoice')

    def name_get(self):
        group_by = self.env.context.get('group_by', [])
        field_list = [fname for fname in self._name_get_fields() if fname not in group_by][:2]  # limit to 2 labels
        result = []
        for slot in self:
            # label part, depending on context `groupby`
            name = ' - '.join([self._fields[fname].convert_to_display_name(slot[fname], slot) for fname in field_list if slot[fname]])

            if slot.crm_id.name:
                name =str(name) + ' - ' + str(slot.crm_id.name)
            if slot.building_name:
                name = str(name) + ' - ' + str(slot.building_name)
            if slot.unit_number:
                name = str(name) + ' - ' + str(slot.unit_number)
            if slot.building_name:
                name = str(name) + ' - ' + str(slot.building_name)
            if slot.revenue:
                name = str(name) + ' - AED ' + str(slot.revenue)
            # date / time part
            destination_tz = pytz.timezone(self.env.user.tz or 'UTC')
            start_datetime = pytz.utc.localize(slot.start_datetime).astimezone(destination_tz).replace(tzinfo=None)
            end_datetime = pytz.utc.localize(slot.end_datetime).astimezone(destination_tz).replace(tzinfo=None)
            if slot.end_datetime - slot.start_datetime <= timedelta(hours=24):  # shift on a single day
                name = '%s - %s %s' % (
                    format_time(self.env, start_datetime.time(), time_format='short'),
                    format_time(self.env, end_datetime.time(), time_format='short'),
                    name
                )
            else:
                name = '%s - %s %s' % (
                    start_datetime.date(),
                    end_datetime.date(),
                    name
                )
            # add unicode bubble to tell there is a note
            if slot.name:
                name = u'%s \U0001F4AC' % name
            result.append([slot.id, name])
        return result

    @api.model
    def create(self, vals):
        if not vals.get('company_id') and vals.get('employee_id'):
            vals['company_id'] = self.env['hr.employee'].browse(vals.get('employee_id')).company_id.id
        if not vals.get('company_id'):
            vals['company_id'] = self.env.company.id
        return super(MisPlanning, self).create(vals)

    def write(self, values):

        # detach planning entry from recurrency
        if any(fname in values.keys() for fname in self._get_fields_breaking_recurrency()) and not values.get('recurrency_id'):
            values.update({'recurrency_id': False})
        # warning on published shifts
        if 'publication_warning' not in values and (set(values.keys()) & set(self._get_fields_breaking_publication())):
            values['publication_warning'] = True
        result = super(MisPlanning, self).write(values)

        # recurrence
#        if any(key in ('repeat', 'repeat_type', 'repeat_until', 'repeat_interval') for key in values):
            # User is trying to change this record's recurrence so we delete future slots belonging to recurrence A
            # and we create recurrence B from now on w/ the new parameters
        for slot in self:
            if slot.job_status_id.is_invoice:
                objstate = self.env['crm.stage'].search([('is_closed', '=', True)])
                for rec in objstate:
                    slot.crm_id.stage_id = rec.id
#            raise UserError('hi')
                if slot.paid_amount < 0:
                    raise UserError('Amount cannot be negative')
                if slot.recurrency_id and values.get('repeat') is None:
                    recurrency_values = {
                        'repeat_interval': values.get('repeat_interval') or slot.recurrency_id.repeat_interval,
                        'repeat_until': values.get('repeat_until') if values.get('repeat_type') == 'until' else False,
                        'repeat_type': values.get('repeat_type'),
                        'company_id': slot.company_id.id,
                    }
                    # Kill recurrence A
                    slot.recurrency_id.repeat_type = 'until'
                    slot.recurrency_id.repeat_until = slot.start_datetime
                    slot.recurrency_id._delete_slot(slot.end_datetime)
                    # Create recurrence B
                    recurrence = slot.env['planning.recurrency'].create(recurrency_values)
                    slot.recurrency_id = recurrence
                    slot.recurrency_id._repeat_slot()
                if slot.paid_amount>0:
                    strname = ''
                    if slot.name:
                        strname = slot.name

                    objsale = self.env['sale.order'].search(
                        [('state', '=', 'sale'), ('opportunity_id', '=', slot.crm_id.id)])
                    move_line_vals = []
                    if objsale:
                        for rec in objsale:
                            for line in rec.order_line:
                                create_vals = (0, 0, {
                                    'date':  datetime.now(),
                                    'name': line.product_id.name,
                                    'ref': 'Auto Invoice - ' + strname,
                                    'tax_ids': line.tax_id.ids,
                                    'parent_state': 'draft',
                                    'quantity': line.product_uom_qty,
                                    'price_unit': line.price_unit,
                                    'product_id': line.product_id.id,
                                })
                               # totalamt += line.price_total
                                move_line_vals.append(create_vals)

                                move_vals = {'date':  datetime.now(),
                                             'partner_id': slot.partner_id.id,
                                             'invoice_origin': strname,
                                             'invoice_date':  datetime.now(),
                                             'journal_id': 1,
                                             'ref': 'Auto Invoice - ' + strname,
                                             'name': '/',

                                             'state': 'draft',
                                             'type': 'out_invoice',

                                             'invoice_line_ids': move_line_vals,
                                             }
                        objacmove = self.env['account.move'].create(move_vals)

                        #self.invoice_id = objacmove.id
                        #self.state = 'posted'

                        list_of_ids = []
                        postedinvoice = objacmove.post()
                        #postedinvoice.action_invoice_register_payment()
                        list_of_ids.append(objacmove.id)
                        if list_of_ids:
                            imd = self.env['ir.model.data']
                            action = imd.xmlid_to_object('account.action_move_out_invoice_type')
                            list_view_id = imd.xmlid_to_res_id('account.view_invoice_tree')
                            form_view_id = imd.xmlid_to_res_id('account.view_move_form')
                            result = {
                                'name': action.name,
                                'help': action.help,
                                'type': action.type,
                                'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
                                'target': action.target,
                                'context': action.context,
                                'res_model': action.res_model,
                            }
                            if list_of_ids:
                                result['domain'] = "[('id','in',%s)]" % list_of_ids
                        else:
                            raise UserError(_('Invoice not generated'))

        return result

