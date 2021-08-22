# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.tools.misc import formatLang
from datetime import date, datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

class MisNotPaidInvoice(models.TransientModel):
    _name = 'notpaid.invoices'
    _description ='Not Paid invoices Notification'

    body_text = fields.Text(default='eeee')
    email_to = fields.Char()
    subject_line = fields.Char()
    sales_Agent = fields.Char()
    report_date = fields.Datetime(default=fields.Datetime.now)


    def _get_notpaid_lines(self):

        objinvoice = self.env['account.move'].search([('state', '=', 'posted'),
                                                      ('type', 'in', ('out_invoice', 'out_refund')),
                                                      ('company_id', '=', 1),
                                                      ('amount_residual_signed', '>', 0.0)],order='date')

        strbody=''
        for lines in objinvoice:

            strbody+="<tr><td style='border: 1px solid black;border-collapse: collapse;padding: 5px;text-align: center;'><b>" + str(lines.name) +"</b></td>"
            strbody += "<td style='border: 1px solid black;border-collapse: collapse;padding: 5px;'><b>" + str(
                lines.date) + "</b></td>"
            strbody += "<td style='border: 1px solid black;border-collapse: collapse;padding: 5px;'><b>" + str(
                lines.partner_id.name) + "</b></td>"
            strbody += "<td style='border: 1px solid black;border-collapse: collapse;padding: 5px;'><b>" + str(
                lines.invoice_user_id.name) + "</b></td>"
            strbody += "<td style='border: 1px solid black;border-collapse: collapse;padding: 5px;text-align: right;'><b>" + str(
                "{:.2f}".format(lines.amount_total_signed)) + "</b></td>"
            strbody += "<td style='border: 1px solid black;border-collapse: collapse;padding: 5px;text-align: right;'><b>" + str(
                "{:.2f}".format(lines.amount_residual_signed)) + "</b></td>"

            strbody += "</tr>"
        return strbody

    @api.model
    def _get_notpaid_lines_byagent(self, sales_agent_id):

        objinvoice = self.env['account.move'].search([('state', '=', 'posted'),
                                                      ('type', 'in', ('out_invoice', 'out_refund')),
                                                      ('company_id', '=', 1),
                                                      ('amount_residual_signed', '>', 0.0), ('invoice_user_id' ,'=', sales_agent_id)],order='partner_id,date')

        strbody=''
        for lines in objinvoice:

            strbody+="<tr><td style='border: 1px solid black;border-collapse: collapse;padding: 5px;text-align: center;'><b>" + str(lines.name) +"</b></td>"
            strbody += "<td style='border: 1px solid black;border-collapse: collapse;padding: 5px;'><b>" + str(
                lines.date) + "</b></td>"
            strbody += "<td style='border: 1px solid black;border-collapse: collapse;padding: 5px;'><b>" + str(
                lines.partner_id.name) + "</b></td>"
            strbody += "<td style='border: 1px solid black;border-collapse: collapse;padding: 5px;'><b>" + str(
                lines.invoice_user_id.name) + "</b></td>"
            strbody += "<td style='border: 1px solid black;border-collapse: collapse;padding: 5px;text-align: right;'><b>" + str(
                "{:.2f}".format(lines.amount_total_signed)) + "</b></td>"
            strbody += "<td style='border: 1px solid black;border-collapse: collapse;padding: 5px;text-align: right;'><b>" + str(
                "{:.2f}".format(lines.amount_residual_signed)) + "</b></td>"

            strbody += "</tr>"
        return strbody


    def _get_notpaid_summary_byagent(self):

        self._cr.execute("""
                         select invoice_user_id, sum(amount_total_signed) as totinvoice,sum(amount_residual_signed) as totbalance 
                         from account_move where state='posted' and type in ('out_invoice', 'out_refund') 
                         and company_id=1 and amount_residual_signed>0 group by invoice_user_id   
                     """)
        res_sum = self._cr.dictfetchall()


        for sr in res_sum:
            objusers = self.env['res.users'].search([('id', '=', sr['invoice_user_id'])])
            strbody=''
            strbody+="<tr><td style='border: 1px solid black;border-collapse: collapse;padding: 5px;text-align: center;'><b>" + str(objusers.name) +"</b></td>"
            strbody += "<td style='border: 1px solid black;border-collapse: collapse;padding: 5px;'><b>" + str(
                "{:.2f}".format(sr.totinvoice)) + "</b></td>"
            strbody += "<td style='border: 1px solid black;border-collapse: collapse;padding: 5px;'><b>" + str(
                "{:.2f}".format(sr.totbalance)) + "</b></td>"
            strbody += "</tr>"
        return strbody






    def _send_notpaid_email_notification(self):


        vals={'body_text': ' ',
              'email_to': 'ceo@edgedxb.com,md@edgedxb.com,info@edgedxb.com',
              'sales_Agent' : 'Dear All ',

        }
        objnotification = self.env['notpaid.invoices'].create(vals)

        objnotification.body_text=self._get_notpaid_lines()
        objnotification.report_date =objnotification.report_date+ timedelta(hours=4)
        objnotification.subject_line = "Outstanding Invoice Notifications - " + str(objnotification.report_date)

        # raise UserError(objnotification.body_text)


        email_template = self.env.ref('mis_reports.email_template_notpaid_invoice')


        email_template.send_mail(objnotification.id, force_send=True)

        email_summary_temp = self.env.ref('mis_reports.email_template_notpaid_invoice_summary')
        objnotification.body_text=self._get_notpaid_summary_byagent
        objnotification.subject_line = "Outstanding Invoice Summary by Agent  Notifications - " + str(objnotification.report_date)
        email_summary_temp.send_mail(objnotification.id, force_send=True)


        self._cr.execute("""
                    SELECT distinct
                        invoice_user_id
                    FROM
                        account_move
                    WHERE
                        type in  ('out_invoice', 'out_refund')  AND state ='posted' AND company_id= 1
                        and amount_residual_signed>0.0   
                """)
        res = self._cr.dictfetchall()

        saleagents = [r['invoice_user_id'] for r in res]

        for sagent in saleagents:
            objusers = self.env['res.users'].search([('id', '=', sagent)])
            if objusers:
                objnotification.email_to = str(objusers.email)
                objnotification.sales_Agent ="Dear " + str(objusers.name)
                objnotification.subject_line = str(objusers.name) + "'s Customers Outstanding Invoice Notifications - " + str(objnotification.report_date)

                objnotification.body_text = self._get_notpaid_lines_byagent(sagent)
                email_template.send_mail(objnotification.id, force_send=True)


