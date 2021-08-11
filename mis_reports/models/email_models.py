# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.tools.misc import formatLang
from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

class MisNotPaidInvoice(models.Model):
    _name = 'notpaid.invoices'

    def _get_notpaid_lines(self):
        objinvoice = self.env['account.move'].search([('state', '=', 'posted'),
                                                      ('move_type', 'in', ('out_invoice', 'out_refund')),
                                                      ('company_id', '=', 1),
                                                      ('amount_residual_signed', '>', 0.0)])

        records = []

        for lines in objinvoice:
            data_vals = {}
            data_vals['number'] = lines.number
            data_vals['invoice_date'] = lines.invoice_date
            data_vals['partner_name'] = lines.partner_id.name
            data_vals['user_name'] = lines.user_id.name
            data_vals['amount_total_signed'] = lines.amount_total_signed
            data_vals['amount_residual_signed'] = lines.amount_residual_signed


            records.append(data_vals)
        return records


    def _send_notpaid_email_notification(self):
        email_template = self.env.ref('mis_reports.email_template_notpaid_invoice')
        email_template.send_mail(self.id, force_send=True)

