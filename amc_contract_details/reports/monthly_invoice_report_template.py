# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import models
import xlsxwriter
import pandas as pd
from odoo.exceptions import UserError, ValidationError
import calendar

class Monthly_Invoice_Report_Template(models.AbstractModel):
    _name = 'report.amc_contract_details.monthly_invoice_report_template'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, model):
        stryear=data['data']['year']

        query=("""
        select * from amc_contract where EXTRACT(year from start_date)=%s or  EXTRACT(year from end_date)=%s
            and contract_state not in ('draft','cancelled') and contract_stage not in  ('expired')
        """) % (stryear, stryear)
        self._cr.execute(query)
        dat = self._cr.dictfetchall()

        worksheet = workbook.add_worksheet('Monthly Invoice')
        format1 = workbook.add_format({'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'vcenter', 'bold': True})
        format11 = workbook.add_format({'font_size': 12, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True, 'bold': True})
        format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'right': True, 'left': True,'bottom': True, 'top': True, 'bold': True})
        format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 12})
        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True})
        date_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'num_format': 'dd/mm/yyyy'})
        num_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'num_format': '###,##0.00','align': 'right'})
        num_size_8_red = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'num_format': '###,##0.00', 'align': 'right','font_color':'red'})
        formatblack = workbook.add_format({'align': 'center', 'right': True, 'left': True,'bottom': True, 'top': True, 'bold': True})
        datetime_format = workbook.add_format({'num_format': 'mm/dd/yy'})        
        underline = workbook.add_format({'font_size': 12, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True, 'bold': True,'underline':True})

        worksheet.merge_range('A2:J2', 'Monthly Invoice Report', underline)
        worksheet.set_column(0, 0, 35)
        worksheet.set_column(1, 1, 25)
        worksheet.set_column(2, 2, 25)
        worksheet.set_column(3, 3, 20)
        worksheet.set_column(4, 4, 15)
        worksheet.set_column(5, 5, 15)
        worksheet.set_column(6, 6, 15)
        worksheet.set_column(7, 7, 15)
        worksheet.set_column(8, 8, 15)
        worksheet.set_column(9, 9, 20)
        worksheet.set_column(10, 10, 20)
        worksheet.set_column(11, 11, 20)
        # worksheet.set_column(5, 4, 15)
        worksheet.write('A3', 'CUSTOMER NAME', formatblack)
        worksheet.write('B3', 'AGENT NAME', formatblack)
        worksheet.write('C3', 'CONTRACT', formatblack)
        worksheet.write('D3', 'CONTRACT DATE', formatblack)
        worksheet.write('E3', 'FROM DATE', formatblack)
        worksheet.write('F3', 'TO DATE', formatblack)
        worksheet.write('G3', 'CONTRACT AMOUNT', formatblack)
        worksheet.write('H3', 'INVOICED AMOUNT', formatblack)
        worksheet.write('I3', 'PAID AMOUNT', formatblack)
        worksheet.write('J3', 'DUE AMOUNT', formatblack)

        row=3

        for rec in dat:
            col = 0
            objamc = self.env['amc.contract'].search([('id','=',rec['id'])])

            worksheet.write(row, col, objamc.partner_id.name, font_size_8)
            col += 1
            worksheet.write(row, col, objamc.sales_agent_id.name, font_size_8)
            col += 1
            worksheet.write(row, col, rec['name'], font_size_8)
            col += 1
            worksheet.write(row, col, objamc.date, date_size_8)
            col += 1
            worksheet.write(row, col, objamc.start_date, date_size_8)
            col += 1
            worksheet.write(row, col, objamc.start_date, date_size_8)
            col += 1
            worksheet.write(row, col, objamc.total_amount, num_size_8)
            col += 1

            objamcline = self.env['amc.contract.line'].search([('contract_id', '=', objamc.id)])
            totalinv =0
            totalinvdue=0

            for clin in objamcline:
                if clin.lead_id:
                    if clin.lead_id.invoice_id:
                        totalinv+=clin.lead_id.invoice_id.amount_total
                        totalinvdue+=clin.lead_id.invoice_id.amount_residual

            worksheet.write(row, col, totalinv, num_size_8)
            col += 1
            worksheet.write(row, col, totalinv-totalinvdue, num_size_8)
            col += 1
            worksheet.write(row, col, totalinvdue, num_size_8)
            col += 1
            row += 1
        col = 6
        worksheet.merge_range('A' + str(row + 1) + ':F' + str(row + 1), 'Total', formatblack)
        worksheet.write(row, col, '=sum(G4:G' + str(row) + ')', num_size_8)
        col += 1
        worksheet.write(row, col, '=sum(H4:H' + str(row) + ')', num_size_8)
        col += 1
        worksheet.write(row, col, '=sum(I4:I' + str(row) + ')', num_size_8)
        col += 1
        worksheet.write(row, col, '=sum(J4:J' + str(row) + ')', num_size_8)
        col += 1
