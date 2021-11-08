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

        tmr = 8.0

        filterstartdate = self.current_date
        filterenddate = filterstartdate + timedelta(days=1)

        for tmcount in range(25):
            strtime = str(
                '{0:02.0f}:{1:02.0f}'.format(*divmod(float(tmr) * 60, 60)))
            count += 1
            worksheet.set_row(count, 30)
            worksheet.write(count, 0, strtime, wbf['content_border_bg'])
            tmr += 0.5


        objrole = self.env['planning.role'].search([], order='id')
        for rec_role in objrole:
            count = 1
            col += 1
            column_width = 40
            worksheet.set_column(col, col, column_width)
            worksheet.write(count, col, rec_role.name, wbf['content_border_bg'])


            # Team data ====================================
            objteam1 = self.env['planning.slot'].search(
                [('role_id.name', '=', rec_role.name), ('start_datetime', '>=', filterstartdate),
                 ('end_datetime', '<', filterenddate)], order='start_datetime,end_datetime')
            # col = 1
            count = 2

            for recteam1 in objteam1:
                startminutes_val = (recteam1.start_datetime)
                startminutes_val = (startminutes_val.minute + ((startminutes_val.hour + 4) * 60) - 480)
                startrow = int(startminutes_val / 30)

                endminutes_val = (recteam1.end_datetime)
                endminutes_val = (endminutes_val.minute + ((endminutes_val.hour + 4) * 60) - 480)

                endrow = int(endminutes_val / 30)

                if recteam1.crm_id:
                    strprint = ''
                    if recteam1.partner_id:
                        strprint += recteam1.partner_id.name
                        strprint += '\n'
                    if recteam1.phone:
                        strprint += recteam1.phone
                        strprint += '\n'
                    if recteam1.unit_number:
                        strprint += recteam1.unit_number
                        strprint += '\n'
                    if recteam1.building_name:
                        strprint += recteam1.building_name
                        strprint += '\n'
                    if recteam1.area_id:
                        strprint += recteam1.area_id.name
                        strprint += '\n'
                    if recteam1.scope:
                        strprint += recteam1.scope
                        strprint += '\n'
                    if recteam1.revenue:
                        strprint += 'AED - '
                        strprint += str('{0:.2f}'.format(recteam1.revenue))
                        strprint += '\n'
                    # count += 1
                    worksheet.merge_range(str(chr(65+col))+str(count + startrow)+':'+str(chr(65+col))+str(count + endrow - 1), strprint,
                                          wbf['content_border_bg'])


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