# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.tools.misc import formatLang
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
class MisPlanning(models.Model):
    _inherit = 'planning.slot'

    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True,
                                       relation="res.currency")


    crm_id = fields.Many2one('crm.lead', string='CRM')
    partner_id = fields.Many2one('res.partner', related='crm_id.partner_id', string='Customer')
    email = fields.Char(related='crm_id.email_from', string='Email')
    phone = fields.Char(related='crm_id.partner_address_phone', string='Phone')
    revenue = fields.Monetary(related='crm_id.planned_revenue', currency_field='company_currency', string='Revenue')
