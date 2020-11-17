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
#Team 1====================================
        objteam1 = self.env['planning.slot'].search([('role_id.name','=', 'Team1'), ('start_datetime','>=', filterstartdate), ('end_datetime','<', filterenddate)], order='start_datetime,end_datetime')
        col = 1
        count = 3

        for recteam1 in objteam1:
            startminutes_val=(recteam1.start_datetime)
            startminutes_val = (startminutes_val.minute + ((startminutes_val.hour + 4) * 60) - 480)
            startrow = int(startminutes_val/30)

            endminutes_val = (recteam1.end_datetime)
            endminutes_val = (endminutes_val.minute + ((endminutes_val.hour + 4) * 60) - 480)

            endrow = int(endminutes_val / 30)
            #raise UserError(endrow)
            if  recteam1.crm_id:
                strprint =''
                if recteam1.partner_id:
                    strprint+=recteam1.partner_id.name
                    strprint+='\n'
                if recteam1.phone:
                    strprint+=recteam1.phone
                    strprint+='\n'
                if recteam1.unit_number:
                    strprint+=recteam1.unit_number
                    strprint+='\n'
                if recteam1.building_name:
                    strprint+=recteam1.building_name
                    strprint+='\n'
                if recteam1.area_id:
                    strprint+=recteam1.area_id.name
                    strprint+='\n'
                if recteam1.scope:
                    strprint+=recteam1.scope
                    strprint+='\n'
                if recteam1.revenue:
                    strprint +='AED - '
                    strprint+=str('{0:.2f}'.format(recteam1.revenue))
                    strprint+='\n'
                #count += 1
                worksheet.merge_range('B%s:B%s' % (count+startrow, count+endrow-1), strprint, wbf['content_border_bg'])

# Team 2====================================

        objteam2 = self.env['planning.slot'].search(
            [('role_id.name', '=', 'Team2'), ('start_datetime', '>=', filterstartdate),
             ('end_datetime', '<', filterenddate)], order='start_datetime,end_datetime')
        col = 1
        count = 3

        for recteam2 in objteam2:
            startminutes_val = (recteam2.start_datetime)
            startminutes_val = (startminutes_val.minute + ((startminutes_val.hour + 4) * 60) - 480)
            startrow = int(startminutes_val / 30)

            endminutes_val = (recteam2.end_datetime)
            endminutes_val = (endminutes_val.minute + ((endminutes_val.hour + 4) * 60) - 480)

            endrow = int(endminutes_val / 30)
            # raise UserError(endrow)
            if recteam2.crm_id:
                strprint = ''
                if recteam2.partner_id:
                    strprint += recteam2.partner_id.name
                    strprint += '\n'
                if recteam2.phone:
                    strprint += recteam2.phone
                    strprint += '\n'
                if recteam2.unit_number:
                    strprint += recteam2.unit_number
                    strprint += '\n'
                if recteam2.building_name:
                    strprint += recteam2.building_name
                    strprint += '\n'
                if recteam2.area_id:
                    strprint += recteam2.area_id.name
                    strprint += '\n'
                if recteam2.scope:
                    strprint += recteam2.scope
                    strprint += '\n'
                if recteam2.revenue:
                    strprint += 'AED - '
                    strprint += str('{0:.2f}'.format(recteam2.revenue))
                    strprint += '\n'
                # count += 1
                worksheet.merge_range('C%s:C%s' % (count + startrow, count + endrow - 1), strprint,
                                      wbf['content_border_bg'])

# Team 3====================================

        objteam3 = self.env['planning.slot'].search(
            [('role_id.name', '=', 'Team3'), ('start_datetime', '>=', filterstartdate),
             ('end_datetime', '<', filterenddate)], order='start_datetime,end_datetime')
        col = 1
        count = 3

        for recteam3 in objteam3:
            startminutes_val = (recteam3.start_datetime)
            startminutes_val = (startminutes_val.minute + ((startminutes_val.hour + 4) * 60) - 480)
            startrow = int(startminutes_val / 30)

            endminutes_val = (recteam3.end_datetime)
            endminutes_val = (endminutes_val.minute + ((endminutes_val.hour + 4) * 60) - 480)

            endrow = int(endminutes_val / 30)
            # raise UserError(endrow)
            if recteam3.crm_id:
                strprint = ''
                if recteam3.partner_id:
                    strprint += recteam3.partner_id.name
                    strprint += '\n'
                if recteam3.phone:
                    strprint += recteam3.phone
                    strprint += '\n'
                if recteam3.unit_number:
                    strprint += recteam3.unit_number
                    strprint += '\n'
                if recteam3.building_name:
                    strprint += recteam3.building_name
                    strprint += '\n'
                if recteam3.area_id:
                    strprint += recteam3.area_id.name
                    strprint += '\n'
                if recteam3.scope:
                    strprint += recteam3.scope
                    strprint += '\n'
                if recteam3.revenue:
                    strprint += 'AED - '
                    strprint += str('{0:.2f}'.format(recteam3.revenue))
                    strprint += '\n'
                # count += 1
                worksheet.merge_range('D%s:D%s' % (count + startrow, count + endrow - 1), strprint,
                                      wbf['content_border_bg'])

# Team 4====================================

        objteam4 = self.env['planning.slot'].search(
            [('role_id.name', '=', 'Team4'), ('start_datetime', '>=', filterstartdate),
             ('end_datetime', '<', filterenddate)], order='start_datetime,end_datetime')
        col = 1
        count = 3

        for recteam4 in objteam4:
            startminutes_val = (recteam4.start_datetime)
            startminutes_val = (startminutes_val.minute + ((startminutes_val.hour + 4) * 60) - 480)
            startrow = int(startminutes_val / 30)

            endminutes_val = (recteam4.end_datetime)
            endminutes_val = (endminutes_val.minute + ((endminutes_val.hour + 4) * 60) - 480)

            endrow = int(endminutes_val / 30)
            # raise UserError(endrow)
            if recteam4.crm_id:
                strprint = ''
                if recteam4.partner_id:
                    strprint += recteam4.partner_id.name
                    strprint += '\n'
                if recteam4.phone:
                    strprint += recteam4.phone
                    strprint += '\n'
                if recteam4.unit_number:
                    strprint += recteam4.unit_number
                    strprint += '\n'
                if recteam4.building_name:
                    strprint += recteam4.building_name
                    strprint += '\n'
                if recteam4.area_id:
                    strprint += recteam4.area_id.name
                    strprint += '\n'
                if recteam4.scope:
                    strprint += recteam4.scope
                    strprint += '\n'
                if recteam4.revenue:
                    strprint += 'AED - '
                    strprint += str('{0:.2f}'.format(recteam4.revenue))
                    strprint += '\n'
                # count += 1
                worksheet.merge_range('E%s:E%s' % (count + startrow, count + endrow - 1), strprint,
                                      wbf['content_border_bg'])

# Team 5====================================

        objteam5 = self.env['planning.slot'].search(
            [('role_id.name', '=', 'Team5'), ('start_datetime', '>=', filterstartdate),
             ('end_datetime', '<', filterenddate)], order='start_datetime,end_datetime')
        col = 1
        count = 3

        for recteam5 in objteam5:
            startminutes_val = (recteam5.start_datetime)
            startminutes_val = (startminutes_val.minute + ((startminutes_val.hour + 4) * 60) - 480)
            startrow = int(startminutes_val / 30)

            endminutes_val = (recteam5.end_datetime)
            endminutes_val = (endminutes_val.minute + ((endminutes_val.hour + 4) * 60) - 480)

            endrow = int(endminutes_val / 30)
            # raise UserError(endrow)
            if recteam5.crm_id:
                strprint = ''
                if recteam5.partner_id:
                    strprint += recteam5.partner_id.name
                    strprint += '\n'
                if recteam5.phone:
                    strprint += recteam5.phone
                    strprint += '\n'
                if recteam5.unit_number:
                    strprint += recteam5.unit_number
                    strprint += '\n'
                if recteam5.building_name:
                    strprint += recteam5.building_name
                    strprint += '\n'
                if recteam5.area_id:
                    strprint += recteam5.area_id.name
                    strprint += '\n'
                if recteam5.scope:
                    strprint += recteam5.scope
                    strprint += '\n'
                if recteam5.revenue:
                    strprint += 'AED - '
                    strprint += str('{0:.2f}'.format(recteam5.revenue))
                    strprint += '\n'
                # count += 1
                worksheet.merge_range('F%s:F%s' % (count + startrow, count + endrow - 1), strprint,
                                      wbf['content_border_bg'])

# Team 6====================================

        objteam6 = self.env['planning.slot'].search(
            [('role_id.name', '=', 'Team6'), ('start_datetime', '>=', filterstartdate),
             ('end_datetime', '<', filterenddate)], order='start_datetime,end_datetime')
        col = 1
        count = 3

        for recteam6 in objteam6:
            startminutes_val = (recteam6.start_datetime)
            startminutes_val = (startminutes_val.minute + ((startminutes_val.hour + 4) * 60) - 480)
            startrow = int(startminutes_val / 30)

            endminutes_val = (recteam6.end_datetime)
            endminutes_val = (endminutes_val.minute + ((endminutes_val.hour + 4) * 60) - 480)

            endrow = int(endminutes_val / 30)
            # raise UserError(endrow)
            if recteam6.crm_id:
                strprint = ''
                if recteam6.partner_id:
                    strprint += recteam6.partner_id.name
                    strprint += '\n'
                if recteam6.phone:
                    strprint += recteam6.phone
                    strprint += '\n'
                if recteam6.unit_number:
                    strprint += recteam6.unit_number
                    strprint += '\n'
                if recteam6.building_name:
                    strprint += recteam6.building_name
                    strprint += '\n'
                if recteam6.area_id:
                    strprint += recteam6.area_id.name
                    strprint += '\n'
                if recteam6.scope:
                    strprint += recteam6.scope
                    strprint += '\n'
                if recteam6.revenue:
                    strprint += 'AED - '
                    strprint += str('{0:.2f}'.format(recteam6.revenue))
                    strprint += '\n'
                # count += 1
                worksheet.merge_range('G%s:G%s' % (count + startrow, count + endrow - 1), strprint,
                                      wbf['content_border_bg'])

# Team 7====================================

        objteam7 = self.env['planning.slot'].search(
            [('role_id.name', '=', 'Team7'), ('start_datetime', '>=', filterstartdate),
             ('end_datetime', '<', filterenddate)], order='start_datetime,end_datetime')
        col = 1
        count = 3

        for recteam7 in objteam7:
            startminutes_val = (recteam7.start_datetime)
            startminutes_val = (startminutes_val.minute + ((startminutes_val.hour + 4) * 60) - 480)
            startrow = int(startminutes_val / 30)

            endminutes_val = (recteam7.end_datetime)
            endminutes_val = (endminutes_val.minute + ((endminutes_val.hour + 4) * 60) - 480)

            endrow = int(endminutes_val / 30)
            # raise UserError(endrow)
            if recteam7.crm_id:
                strprint = ''
                if recteam7.partner_id:
                    strprint += recteam7.partner_id.name
                    strprint += '\n'
                if recteam7.phone:
                    strprint += recteam7.phone
                    strprint += '\n'
                if recteam7.unit_number:
                    strprint += recteam7.unit_number
                    strprint += '\n'
                if recteam7.building_name:
                    strprint += recteam7.building_name
                    strprint += '\n'
                if recteam7.area_id:
                    strprint += recteam7.area_id.name
                    strprint += '\n'
                if recteam7.scope:
                    strprint += recteam7.scope
                    strprint += '\n'
                if recteam7.revenue:
                    strprint += 'AED - '
                    strprint += str('{0:.2f}'.format(recteam7.revenue))
                    strprint += '\n'
                # count += 1
                worksheet.merge_range('H%s:H%s' % (count + startrow, count + endrow - 1), strprint,
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