# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import models
import xlsxwriter
import pandas as pd
from odoo.exceptions import UserError, ValidationError
import calendar

class Monthly_Revenue_Report_Template(models.AbstractModel):
    _name = 'report.amc_contract_details.monthly_revenue_report_template'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, model):
        print('maddsikfjofj', model, data, self)
        stryear=data['data']['year']
        query=("""
        select *,(mtotal_amount/totalmonth) as monthlyrev from  
(select *,COALESCE(total_amount,0.00) as mtotal_amount,EXTRACT(month from start_date) as startmonth,start_date,(EXTRACT(year FROM age(end_date ,start_date))*12
 + EXTRACT(month FROM age(end_date,start_date))+1) as totalmonth from amc_contract 
  where EXTRACT(year from start_date)=%s or  EXTRACT(year from end_date)=%s
            and contract_state not in ('draft','cancelled') and contract_stage not in  ('expired')) f1
    
            """) % (stryear, stryear)
        self._cr.execute(query)
        dat = self._cr.dictfetchall()

        worksheet = workbook.add_worksheet('Monthly Revenue')
        format1 = workbook.add_format({'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'vcenter', 'bold': True})
        format11 = workbook.add_format({'font_size': 12, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True, 'bold': True})
        format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'right': True, 'left': True,'bottom': True, 'top': True, 'bold': True})
        format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 12})
        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True})
        date_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'num_format': 'dd/mm/yyyy'})
        num_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'num_format': '###,##0.00','align': 'right'})
        int_size_8 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'num_format': '###,##0', 'align': 'right'})
        formatblack = workbook.add_format({'align': 'center', 'right': True, 'left': True,'bottom': True, 'top': True, 'bold': True})
        datetime_format = workbook.add_format({'num_format': 'mm/dd/yy'})        
        underline = workbook.add_format({'font_size': 12, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True, 'bold': True,'underline':True})

        worksheet.merge_range('A2:S2', 'Monthly Revenue Report', underline)
        worksheet.set_column(0, 0, 35)
        worksheet.set_column(1, 1, 25)
        worksheet.set_column(2, 2, 25)
        worksheet.set_column(3, 3, 20)
        worksheet.set_column(4, 4, 15)
        worksheet.set_column(5, 5, 15)
        worksheet.set_column(6, 6, 15)
        # worksheet.set_column(5, 4, 15)
        worksheet.write('A3', 'CUSTOMER NAME', formatblack)
        worksheet.write('B3', 'AGENT NAME', formatblack)
        worksheet.write('C3', 'CONTRACT', formatblack)
        worksheet.write('D3', 'CONTRACT VALUE', formatblack)
        worksheet.write('E3', 'START DATE', formatblack)
        worksheet.write('F3', 'END DATE', formatblack)
        worksheet.write('G3', 'TOTAL MONTHS', formatblack)

        row = 2
        col = 7
        for x in range(1, 13):
            worksheet.write_string(row, col, calendar.month_abbr[x] +' ' + stryear, formatblack)
            worksheet.set_column(col, col, 15)
            col += 1

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
            worksheet.write(row, col, objamc.total_amount, num_size_8)
            col += 1
            worksheet.write(row, col, objamc.start_date, date_size_8)
            col += 1
            worksheet.write(row, col, objamc.end_date, date_size_8)
            col += 1
            worksheet.write(row, col, rec['totalmonth'], int_size_8)
            col += 1
            printitems=0
            totprint =int(rec['totalmonth'])
            for lint in range(12):
                if int(rec['startmonth'])<=lint+1:
                    if printitems<totprint:
                        worksheet.write(row, col, rec['monthlyrev'], num_size_8)
                        printitems+=1
                    else:
                        worksheet.write(row, col, "", num_size_8)
                else:
                    worksheet.write(row, col, "", num_size_8)
                col+=1
            row += 1
        col_val = col
        col = 7
        worksheet.merge_range('A'+str(row+1)+':G'+str(row+1), 'Total', formatblack)

        for x in range(1, 13):
            worksheet.write(row, col, '=sum('+ chr(65+col)+'4:'+chr(65+col)+str(row)+')', num_size_8)
            col +=1
        col += 1
        row += 1
        
        


        