# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.tools.misc import formatLang
from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

class MisCRMLead(models.Model):
    _name = 'notpaid.invoices'

    def _get_notpaid_lines(self):
        objinvoice = self.env['account.move'].search([('state', '=', 'posted'),
                                                      ('move_type', 'in', ('out_invoice', 'out_refund')),
                                                      ('company_id', '=', 1),
                                                      ('amount_residual_signed', '>', 0.0)])
        return objinvoice

    def _send_notpaid_email_notification(self):
        email_template = self.env.ref('mis_reports.email_template_notpaid_invoice')

        if email_template:
            email_template.send_mail(force_send=True)

