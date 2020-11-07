# -*- coding: utf-8 -*-
from datetime import date, datetime
from odoo.exceptions import UserError
from odoo.tools import date_utils
import xlsxwriter
import base64
from odoo import fields, models, api, _
from io import BytesIO
from pytz import timezone
from datetime import timedelta
import pytz

class PlanningSummary(models.TransientModel):
    _name = 'wizard.report.planning'


    current_date = fields.Date(string='Date', required=True)


    datas = fields.Binary('File', readonly=True)
    datas_fname = fields.Char('Filename', readonly=True)    

    #
    # def _get_partner(self):
    #     if self.partner_id:
    #         return ('partner_id', '=', self.partner_id.id)
    #     else:
    #         return (1, '=', 1)
    #
    # def _get_analytic(self):
    #     if self.analytic_id:
    #         return ('analytic_id', '=', self.analytic_id.id)
    #     else:
    #         return (1, '=', 1)
    #
    # def _getdomainfilter(self):
    #     return [('date', '>=', self.from_date), ('date', '<=', self.to_date),self._get_partner(),
    #             self._get_analytic(),('company_id', '=', self.env.company.id),('state', '=', 'posted'),('type', 'in', ['in_invoice','in_refund'])
    #             ]

    def download_planning_summary(self):

        date = datetime.now()
        report_name = 'Planning_' + date.strftime("%y%m%d%H%M%S")
        date_string = self.current_date.strftime("%B-%y")
        header_date =self.current_date.strftime("%Y-%m-%d")
        filename = '%s %s' % (report_name, date_string)
        #
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        wbf = {}

        wbf['content'] = workbook.add_format()
        wbf['header'] = workbook.add_format({'bold': 1, 'align': 'center'})
        wbf['content_float'] = workbook.add_format({'align': 'right', 'num_format': '#,##0.00'})
        wbf['content_border'] = workbook.add_format()
        wbf['content_border'].set_top()
        wbf['content_border'].set_bottom()
        wbf['content_border'].set_left()
        wbf['content_border'].set_right()

        wbf['content_float_border'] = workbook.add_format({'align': 'right', 'num_format': '#,##0.00'})
        wbf['content_float_border'].set_top()
        wbf['content_float_border'].set_bottom()
        wbf['content_float_border'].set_left()
        wbf['content_float_border'].set_right()

        wbf['content_border_bg_total'] = workbook.add_format({'align': 'right', 'bold': 1, 'bg_color': '#E1E1E1'})
        wbf['content_border_bg_total'].set_top()
        wbf['content_border_bg_total'].set_bottom()
        wbf['content_border_bg_total'].set_left()
        wbf['content_border_bg_total'].set_right()

        wbf['content_border_bg'] = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': 1, 'bg_color': '#E1E1E1'})
        wbf['content_border_bg'].set_top()
        wbf['content_border_bg'].set_bottom()
        wbf['content_border_bg'].set_left()
        wbf['content_border_bg'].set_right()
        wbf['content_border_bg'].set_text_wrap()

        wbf['content_float_border_bg'] = workbook.add_format({'align': 'right', 'num_format': '#,##0.00', 'bold': 1, 'bg_color': '#E1E1E1'})
        wbf['content_float_border_bg'].set_top()
        wbf['content_float_border_bg'].set_bottom()
        wbf['content_float_border_bg'].set_left()
        wbf['content_float_border_bg'].set_right()



        worksheet = workbook.add_worksheet(report_name)

        count = 0

        # Report Heading
        worksheet.merge_range('A%s:G%s' % (1, 1), 'PLANNING SUMMARY REPORT ' + str(header_date) , wbf['header'])
        count += 1
        col = 0

        worksheet.set_row(1,40)
        column_width=25
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Time', wbf['content_border_bg'])
        col += 1
        column_width = 40
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Team 1', wbf['content_border_bg'])
        col += 1
        column_width = 40
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Team 2', wbf['content_border_bg'])
        col += 1
        column_width = 40
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Team 3', wbf['content_border_bg'])
        col += 1
        column_width = 40
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Team 4', wbf['content_border_bg'])
        col += 1
        column_width = 40
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Team 5', wbf['content_border_bg'])
        col += 1
        column_width = 40
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Team 6', wbf['content_border_bg'])

        col += 1
        column_width = 40
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Team 7', wbf['content_border_bg'])

        tmr = 8.0

        filterstartdate =self.current_date
        filterenddate =filterstartdate+timedelta(days=1)

        for tmcount in range(25):
            strtime = str(
                '{0:02.0f}:{1:02.0f}'.format(*divmod(float(tmr) * 60, 60)))
            count += 1
            worksheet.set_row(count, 30)
            worksheet.write(count, 0, strtime, wbf['content_border_bg'])
            tmr += 0.5

        objteam1 = self.env['planning.slot'].search([('role_id.name','=', 'Team1'), ('start_datetime','>=', filterstartdate), ('start_datetime','<=', filterenddate)], order='start_datetime,end_datetime')
        col = 1
        count = 2
        for recteam1 in objteam1:
            startminutes_val=(recteam1.start_datetime)
            startminutes_val = (startminutes_val.minute + ((startminutes_val.hour + 4) * 60) - 480)
            startrow = int(startminutes_val/30)

            endminutes_val = (recteam1.end_datetime)
            endminutes_val = (endminutes_val.minute + ((endminutes_val.hour + 4) * 60) - 480)
            endrow = int(endminutes_val / 30)
            if  recteam1.crm_id:
                #count += 1
                worksheet.merge_range('B%s:B%s' % (count+startrow, count+endrow), recteam1.crm_id.name + ' ' + str(recteam1.partner_id.name)+ ' AED - ' + str(recteam1.revenue), wbf['content_border_bg'])

        objteam2 = self.env['planning.slot'].search([('role_id.name','=', 'Team2'), ('start_datetime','>=', filterstartdate), ('start_datetime','<=', filterenddate)], order='start_datetime,end_datetime')
        col = 1
        count = 2
        for recteam2 in objteam2:
            startminutes_val=(recteam2.start_datetime)
            startminutes_val = (startminutes_val.minute + ((startminutes_val.hour + 4) * 60) - 480)
            startrow = int(startminutes_val/30)

            endminutes_val = (recteam2.end_datetime)
            endminutes_val = (endminutes_val.minute + ((endminutes_val.hour + 4) * 60) - 480)
            endrow = int(endminutes_val / 30)
            if  recteam2.crm_id:
                #count += 1
                worksheet.merge_range('C%s:C%s' % (count+startrow, count+endrow), recteam2.crm_id.name + ' ' + str(recteam2.partner_id.name)+ ' AED - ' + str(recteam2.revenue), wbf['content_border_bg'])



        objteam3 = self.env['planning.slot'].search([('role_id.name','=', 'Team3'), ('start_datetime','>=', filterstartdate), ('start_datetime','<=', filterenddate)], order='start_datetime,end_datetime')
        col = 1
        count = 2
        for recteam3 in objteam3:
            startminutes_val=(recteam3.start_datetime)
            startminutes_val = (startminutes_val.minute + ((startminutes_val.hour + 4) * 60) - 480)
            startrow = int(startminutes_val/30)

            endminutes_val = (recteam3.end_datetime)
            endminutes_val = (endminutes_val.minute + ((endminutes_val.hour + 4) * 60) - 480)
            endrow = int(endminutes_val / 30)
            if  recteam3.crm_id:
                #count += 1
                worksheet.merge_range('D%s:D%s' % (count+startrow, count+endrow), recteam3.crm_id.name + ' ' + str(recteam3.partner_id.name)+ ' AED - ' + str(recteam3.revenue), wbf['content_border_bg'])


        objteam4 = self.env['planning.slot'].search([('role_id.name','=', 'Team4'), ('start_datetime','>=', filterstartdate), ('start_datetime','<=', filterenddate)], order='start_datetime,end_datetime')
        col = 1
        count = 2
        for recteam4 in objteam4:
            startminutes_val=(recteam4.start_datetime)
            startminutes_val = (startminutes_val.minute + ((startminutes_val.hour + 4) * 60) - 480)
            startrow = int(startminutes_val/30)

            endminutes_val = (recteam4.end_datetime)
            endminutes_val = (endminutes_val.minute + ((endminutes_val.hour + 4) * 60) - 480)
            endrow = int(endminutes_val / 30)
            if  recteam4.crm_id:
                #count += 1
                worksheet.merge_range('B%s:B%s' % (count+startrow, count+endrow), recteam4.crm_id.name + ' ' + str(recteam4.partner_id.name)+ ' AED - ' + str(recteam4.revenue), wbf['content_border_bg'])


        objteam5 = self.env['planning.slot'].search([('role_id.name','=', 'Team5'), ('start_datetime','>=', filterstartdate), ('start_datetime','<=', filterenddate)], order='start_datetime,end_datetime')
        col = 1
        count = 2
        for recteam5 in objteam5:
            startminutes_val=(recteam5.start_datetime)
            startminutes_val = (startminutes_val.minute + ((startminutes_val.hour + 4) * 60) - 480)
            startrow = int(startminutes_val/30)

            endminutes_val = (recteam5.end_datetime)
            endminutes_val = (endminutes_val.minute + ((endminutes_val.hour + 4) * 60) - 480)
            endrow = int(endminutes_val / 30)
            if  recteam5.crm_id:
                #count += 1
                worksheet.merge_range('B%s:B%s' % (count+startrow, count+endrow), recteam5.crm_id.name + ' ' + str(recteam5.partner_id.name)+ ' AED - ' + str(recteam5.revenue), wbf['content_border_bg'])


        objteam6 = self.env['planning.slot'].search([('role_id.name','=', 'Team6'), ('start_datetime','>=', filterstartdate), ('start_datetime','<=', filterenddate)], order='start_datetime,end_datetime')
        col = 1
        count = 2
        for recteam6 in objteam6:
            startminutes_val=(recteam6.start_datetime)
            startminutes_val = (startminutes_val.minute + ((startminutes_val.hour + 4) * 60) - 480)
            startrow = int(startminutes_val/30)

            endminutes_val = (recteam6.end_datetime)
            endminutes_val = (endminutes_val.minute + ((endminutes_val.hour + 4) * 60) - 480)
            endrow = int(endminutes_val / 30)
            if  recteam6.crm_id:
                #count += 1
                worksheet.merge_range('B%s:B%s' % (count+startrow, count+endrow), recteam6.crm_id.name + ' ' + str(recteam6.partner_id.name)+ ' AED - ' + str(recteam6.revenue), wbf['content_border_bg'])




        workbook.close()
        out=base64.encodestring(fp.getvalue())
        self.write({'datas':out, 'datas_fname':filename})
        fp.close()
        filename += '%2Exlsx'

        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'web/content/?model='+self._name+'&id='+str(self.id)+'&field=datas&download=true&filename='+filename,
        }