# -*- coding: utf-8 -*-

import calendar
import datetime
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from odoo import models, api
from odoo.http import request
from math import pi


class DashBoard(models.Model):
    _inherit = 'account.move'

    # function to getting expenses

    # function to getting income of this year
    @api.model
    def getworkingdays(self, chkdate):
        todays_date = chkdate
        year = todays_date.year
        month = todays_date.month
        # start_date = date(year, month, 1)
        # end_date = date(year, month + 1, 1)
        print (todays_date.weekday())
        count = 0
        dt = date(year, month, 1)
        while dt.year == year and dt.month == month:
            if dt.weekday() != 4:
                count += 1
            dt += timedelta(days=1)
        return count

    @api.model
    def getworkingdaysasofnow(self, chkdate):
        todays_date = chkdate
        year = todays_date.year
        month = todays_date.month
        dayin = todays_date.day
        # start_date = date(year, month, 1)
        # end_date = date(year, month + 1, 1)
        # print (todays_date.weekday())
        count = 0
        dt = date(year, month, 1)
        while dt.year == year and dt.month == month and dt.day<=dayin:
            if dt.weekday() != 4:
                count += 1
            dt += timedelta(days=1)
        return count

    @api.model
    def getdailytarget(self, chkdate):
        noofdays=self.getworkingdays(chkdate)
        if noofdays>0:
            return 455000/(noofdays)
        else:
            0



    @api.model
    def get_income_this_year(self, *post):

        company_ids = self.get_current_multi_company_value()

        month_list = []
        for i in range(11, -1, -1):
            l_month = datetime.now() - relativedelta(months=i)
            text = format(l_month, '%B')
            month_list.append(text)

        states_arg = ""
        if post != ('posted',):
            states_arg = """ parent_state in ('posted', 'draft')"""
        else:
            states_arg = """ parent_state = 'posted'"""

        self._cr.execute(('''select sum(debit)-sum(credit) as income ,to_char(account_move_line.date, 'Month')  as month ,
                             internal_group from account_move_line ,account_account where 
                             account_move_line.account_id=account_account.id AND internal_group = 'income' 
                             AND to_char(DATE(NOW()), 'YY') = to_char(account_move_line.date, 'YY')
                             AND account_move_line.company_id in (''' + str(company_ids) + ''')
                             AND parent_state = 'posted' 
                             group by internal_group,month                  
                        '''))
        record = self._cr.dictfetchall()

        self._cr.execute(('''select sum(debit)-sum(credit) as expense ,to_char(account_move_line.date, 'Month')  as month ,
                            internal_group from account_move_line ,account_account where 
                            account_move_line.account_id=account_account.id AND internal_group = 'expense' 
                            AND to_char(DATE(NOW()), 'YY') = to_char(account_move_line.date, 'YY')
                            AND account_move_line.company_id in (''' + str(company_ids) + ''')
                            AND parent_state = 'posted'
                            group by internal_group,month                  
                        '''))

        result = self._cr.dictfetchall()
        records = []
        for month in month_list:
            last_month_inc = list(filter(lambda m: m['month'].strip() == month, record))
            last_month_exp = list(filter(lambda m: m['month'].strip() == month, result))
            if not last_month_inc and not last_month_exp:
                records.append({
                    'month': month,
                    'income': 0.0,
                    'expense': 0.0,
                    'profit': 0.0,
                })
            elif (not last_month_inc) and last_month_exp:
                last_month_exp[0].update({
                    'income': 0.0,
                    'expense': -1 * last_month_exp[0]['expense'] if last_month_exp[0]['expense'] < 1 else
                    last_month_exp[0]['expense']
                })
                last_month_exp[0].update({
                    'profit': last_month_exp[0]['income'] - last_month_exp[0]['expense']
                })
                records.append(last_month_exp[0])
            elif (not last_month_exp) and last_month_inc:
                last_month_inc[0].update({
                    'expense': 0.0,
                    'income': -1 * last_month_inc[0]['income'] if last_month_inc[0]['income'] < 1 else
                    last_month_inc[0]['income']
                })
                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income'] - last_month_inc[0]['expense']
                })
                records.append(last_month_inc[0])
            else:
                last_month_inc[0].update({
                    'income': -1 * last_month_inc[0]['income'] if last_month_inc[0]['income'] < 1 else
                    last_month_inc[0]['income'],
                    'expense': -1 * last_month_exp[0]['expense'] if last_month_exp[0]['expense'] < 1 else
                    last_month_exp[0]['expense']
                })
                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income'] - last_month_inc[0]['expense']
                })
                records.append(last_month_inc[0])
        income = []
        expense = []
        month = []
        profit = []
        for rec in records:
            income.append(rec['income'])
            expense.append(rec['expense'])
            month.append(rec['month'])
            profit.append(rec['profit'])
        return {
            'income': income,
            'expense': expense,
            'month': month,
            'profit': profit,
        }

    # function to getting income of last year

    @api.model
    def get_income_last_year(self, *post):

        company_ids = self.get_current_multi_company_value()

        month_list = []
        for i in range(11, -1, -1):
            l_month = datetime.now() - relativedelta(months=i)
            text = format(l_month, '%B')
            month_list.append(text)

        states_arg = ""
        if post != ('posted',):
            states_arg = """ parent_state in ('posted', 'draft')"""
        else:
            states_arg = """ parent_state = 'posted'"""

        self._cr.execute(('''select sum(debit)-sum(credit) as income ,to_char(account_move_line.date, 'Month')  as month ,
                            internal_group from account_move_line ,account_account
                            where account_move_line.account_id=account_account.id AND internal_group = 'income' 
                            AND Extract(year FROM account_move_line.date) = Extract(year FROM DATE(NOW())) -1 
                            AND account_move_line.company_id in (''' + str(company_ids) + ''')
                            AND parent_state = 'posted'
                            group by internal_group,month                  
                        '''))
        record = self._cr.dictfetchall()

        self._cr.execute(('''select sum(debit)-sum(credit) as expense ,to_char(account_move_line.date, 'Month')  as month ,
                            internal_group from account_move_line , account_account where 
                            account_move_line.account_id=account_account.id AND internal_group = 'expense' 
                            AND Extract(year FROM account_move_line.date) = Extract(year FROM DATE(NOW())) -1 
                            AND account_move_line.company_id in (''' + str(company_ids) + ''')
                            AND parent_state = 'posted'
                            group by internal_group,month                  
                         '''))

        result = self._cr.dictfetchall()
        records = []
        for month in month_list:
            last_month_inc = list(filter(lambda m: m['month'].strip() == month, record))
            last_month_exp = list(filter(lambda m: m['month'].strip() == month, result))
            if not last_month_inc and not last_month_exp:
                records.append({
                    'month': month,
                    'income': 0.0,
                    'expense': 0.0,
                    'profit': 0.0,
                })
            elif (not last_month_inc) and last_month_exp:
                last_month_exp[0].update({
                    'income': 0.0,
                    'expense': -1 * last_month_exp[0]['expense'] if last_month_exp[0]['expense'] < 1 else
                    last_month_exp[0]['expense']
                })
                last_month_exp[0].update({
                    'profit': last_month_exp[0]['income'] - last_month_exp[0]['expense']
                })
                records.append(last_month_exp[0])
            elif (not last_month_exp) and last_month_inc:
                last_month_inc[0].update({
                    'expense': 0.0,
                    'income': -1 * last_month_inc[0]['income'] if last_month_inc[0]['income'] < 1 else
                    last_month_inc[0]['income']
                })
                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income'] - last_month_inc[0]['expense']
                })
                records.append(last_month_inc[0])
            else:
                last_month_inc[0].update({
                    'income': -1 * last_month_inc[0]['income'] if last_month_inc[0]['income'] < 1 else
                    last_month_inc[0]['income'],
                    'expense': -1 * last_month_exp[0]['expense'] if last_month_exp[0]['expense'] < 1 else
                    last_month_exp[0]['expense']
                })
                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income'] - last_month_inc[0]['expense']
                })
                records.append(last_month_inc[0])
        income = []
        expense = []
        month = []
        profit = []
        for rec in records:
            income.append(rec['income'])
            expense.append(rec['expense'])
            month.append(rec['month'])
            profit.append(rec['profit'])
        return {
            'income': income,
            'expense': expense,
            'month': month,
            'profit': profit,
        }

    # function to getting income of last month

    @api.model
    def get_income_last_month(self, *post):

        company_ids = self.get_current_multi_company_value()
        day_list = []
        now = datetime.now()
        day = \
            calendar.monthrange(now.year - 1 if now.month == 1 else now.year,
                                now.month - 1 if not now.month == 1 else 12)[
                1]

        for x in range(1, day + 1):
            day_list.append(x)

        one_month_ago = (datetime.now() - relativedelta(months=1)).month

        states_arg = ""
        if post != ('posted',):
            states_arg = """ parent_state in ('posted', 'draft')"""
        else:
            states_arg = """ parent_state = 'posted'"""

        self._cr.execute(('''select sum(debit)-sum(credit) as income ,cast(to_char(account_move_line.date, 'DD')as int)
                            as date , internal_group from account_move_line , account_account where   
                            Extract(month FROM account_move_line.date) = ''' + str(one_month_ago) + ''' 
                            AND parent_state = 'posted'
                            AND account_move_line.company_id in (''' + str(company_ids) + ''') 
                            AND account_move_line.account_id=account_account.id AND internal_group='income'   
                            group by internal_group,date                 
                             '''))

        record = self._cr.dictfetchall()

        self._cr.execute(('''select sum(debit)-sum(credit) as expense ,cast(to_char(account_move_line.date, 'DD')as int)
                            as date ,internal_group from account_move_line ,account_account where  
                            Extract(month FROM account_move_line.date) = ''' + str(one_month_ago) + ''' 
                            AND parent_state = 'posted'
                            AND account_move_line.company_id in (''' + str(company_ids) + ''') 
                            AND account_move_line.account_id=account_account.id AND internal_group='expense'
                            group by internal_group,date                 
                                 '''))
        result = self._cr.dictfetchall()
        records = []
        for date in day_list:
            last_month_inc = list(filter(lambda m: m['date'] == date, record))
            last_month_exp = list(filter(lambda m: m['date'] == date, result))
            if not last_month_inc and not last_month_exp:
                records.append({
                    'date': date,
                    'income': 0.0,
                    'expense': 0.0,
                    'profit': 0.0
                })
            elif (not last_month_inc) and last_month_exp:
                last_month_exp[0].update({
                    'income': 0.0,
                    'expense': -1 * last_month_exp[0]['expense'] if last_month_exp[0]['expense'] < 1 else
                    last_month_exp[0]['expense']
                })
                last_month_exp[0].update({
                    'profit': last_month_exp[0]['income'] - last_month_exp[0]['expense']
                })
                records.append(last_month_exp[0])
            elif (not last_month_exp) and last_month_inc:
                last_month_inc[0].update({
                    'expense': 0.0,
                    'income': -1 * last_month_inc[0]['income'] if last_month_inc[0]['income'] < 1 else
                    last_month_inc[0]['income']
                })
                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income'] - last_month_inc[0]['expense']
                })
                records.append(last_month_inc[0])
            else:
                last_month_inc[0].update({
                    'income': -1 * last_month_inc[0]['income'] if last_month_inc[0]['income'] < 1 else
                    last_month_inc[0]['income'],
                    'expense': -1 * last_month_exp[0]['expense'] if last_month_exp[0]['expense'] < 1 else
                    last_month_exp[0]['expense']
                })
                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income'] - last_month_inc[0]['expense']
                })
                records.append(last_month_inc[0])
        income = []
        expense = []
        date = []
        profit = []
        for rec in records:
            income.append(rec['income'])
            expense.append(rec['expense'])
            date.append(rec['date'])
            profit.append(rec['profit'])
        return {
            'income': income,
            'expense': expense,
            'date': date,
            'profit': profit

        }

    # function to getting income of this month

    @api.model
    def get_income_this_month(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ parent_state in ('posted', 'draft')"""
        else:
            states_arg = """ parent_state = 'posted'"""

        day_list = []
        now = datetime.now()
        day = calendar.monthrange(now.year, now.month)[1]
        for x in range(1, day + 1):
            day_list.append(x)

        self._cr.execute(('''select sum(debit)-sum(credit) as income ,cast(to_char(account_move_line.date, 'DD')as int)
                            as date , internal_group from account_move_line , account_account
                            where   Extract(month FROM account_move_line.date) = Extract(month FROM DATE(NOW()))  
                            AND Extract(YEAR FROM account_move_line.date) = Extract(YEAR FROM DATE(NOW()))  
                            AND parent_state = 'posted'
                            AND account_move_line.company_id in (''' + str(company_ids) + ''') 
                            AND account_move_line.account_id=account_account.id AND internal_group='income'
                            group by internal_group,date                 
                        '''))

        record = self._cr.dictfetchall()

        self._cr.execute(('''select sum(debit)-sum(credit) as expense ,cast(to_char(account_move_line.date, 'DD')as int)
                            as date , internal_group from account_move_line , account_account where  
                            Extract(month FROM account_move_line.date) = Extract(month FROM DATE(NOW()))  
                            AND Extract(YEAR FROM account_move_line.date) = Extract(YEAR FROM DATE(NOW()))  
                            AND parent_state = 'posted'
                            AND account_move_line.company_id in (''' + str(company_ids) + ''') 
                            AND account_move_line.account_id=account_account.id AND internal_group='expense'
                            group by internal_group,date                 
                         ''') )
        result = self._cr.dictfetchall()
        records = []
        for date in day_list:
            last_month_inc = list(filter(lambda m: m['date'] == date, record))
            last_month_exp = list(filter(lambda m: m['date'] == date, result))
            if not last_month_inc and not last_month_exp:
                records.append({
                    'date': date,
                    'income': 0.0,
                    'expense': 0.0,
                    'profit': 0.0
                })
            elif (not last_month_inc) and last_month_exp:
                last_month_exp[0].update({
                    'income': 0.0,
                    'expense': -1 * last_month_exp[0]['expense'] if last_month_exp[0]['expense'] < 1 else
                    last_month_exp[0]['expense']
                })
                last_month_exp[0].update({
                    'profit': last_month_exp[0]['income'] - last_month_exp[0]['expense']
                })
                records.append(last_month_exp[0])
            elif (not last_month_exp) and last_month_inc:
                last_month_inc[0].update({
                    'expense': 0.0,
                    'income': -1 * last_month_inc[0]['income'] if last_month_inc[0]['income'] < 1 else
                    last_month_inc[0]['income']
                })
                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income'] - last_month_inc[0]['expense']
                })
                records.append(last_month_inc[0])
            else:
                last_month_inc[0].update({
                    'income': -1 * last_month_inc[0]['income'] if last_month_inc[0]['income'] < 1 else
                    last_month_inc[0]['income'],
                    'expense': -1 * last_month_exp[0]['expense'] if last_month_exp[0]['expense'] < 1 else
                    last_month_exp[0]['expense']
                })
                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income'] - last_month_inc[0]['expense']
                })
                records.append(last_month_inc[0])
        income = []
        expense = []
        date = []
        profit = []
        for rec in records:
            income.append(rec['income'])
            expense.append(rec['expense'])
            date.append(rec['date'])
            profit.append(rec['profit'])
        return {
            'income': income,
            'expense': expense,
            'date': date,
            'profit': profit

        }

    # function to getting late bills

    @api.model
    def get_latebills(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ state in ('posted', 'draft')"""
        else:
            states_arg = """ state = 'posted'"""

        self._cr.execute(('''  select res_partner.name as partner, res_partner.commercial_partner_id as res  ,
                            account_move.commercial_partner_id as parent, sum(account_move.amount_total) as amount
                            from account_move,res_partner where 
                            account_move.partner_id=res_partner.id AND account_move.type = 'in_invoice' AND
                            invoice_payment_state = 'not_paid' AND 
                              account_move.company_id in (''' + str(company_ids) + ''') AND
                            state = 'posted'
                            AND  account_move.commercial_partner_id=res_partner.commercial_partner_id 
                            group by parent,partner,res
                            order by amount desc '''))

        record = self._cr.dictfetchall()

        bill_partner = [item['partner'] for item in record]

        bill_amount = [item['amount'] for item in record]

        amounts = sum(bill_amount[9:])
        name = bill_partner[9:]
        results = []
        pre_partner = []

        bill_amount = bill_amount[:9]
        bill_amount.append(amounts)
        bill_partner = bill_partner[:9]
        bill_partner.append("Others")
        records = {
            'bill_partner': bill_partner,
            'bill_amount': bill_amount,
            'result': results,

        }
        return records

        # return record

    # function to getting over dues

    @api.model
    def get_overdues(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ state in ('posted', 'draft')"""
        else:
            states_arg = """ state = 'posted'"""

        self._cr.execute((''' select res_partner.name as partner, res_partner.commercial_partner_id as res  ,
                             account_move.commercial_partner_id as parent, sum(account_move.amount_total) as amount
                            from account_move, account_move_line ,res_partner where 
                            account_move.partner_id=res_partner.id AND account_move.type = 'out_invoice' AND
                            invoice_payment_state = 'not_paid' AND 
                            state = 'posted'
                            AND   account_move.company_id in (''' + str(company_ids) + ''') AND
			                 account_move_line.account_internal_type = 'payable' AND
                             account_move.commercial_partner_id=res_partner.commercial_partner_id 
                            group by parent,partner,res
                            order by amount desc
                            '''))

        record = self._cr.dictfetchall()
        due_partner = [item['partner'] for item in record]
        due_amount = [item['amount'] for item in record]

        amounts = sum(due_amount[9:])
        name = due_partner[9:]
        result = []
        pre_partner = []

        due_amount = due_amount[:9]
        due_amount.append(amounts)
        due_partner = due_partner[:9]
        due_partner.append("Others")
        records = {
            'due_partner': due_partner,
            'due_amount': due_amount,
            'result': result,

        }
        return records

    @api.model
    def get_overdues_this_month_and_year(self, *post):

        states_arg = ""
        if post[0] != 'posted':
            states_arg = """ state in ('posted', 'draft')"""
        else:
            states_arg = """ state = 'posted'"""

        company_ids = self.get_current_multi_company_value()
        if post[1] == 'this_month':
            self._cr.execute((''' 
                               select to_char(account_move.date, 'Month') as month, res_partner.name as due_partner, account_move.partner_id as parent,
                               sum(account_move.amount_total) as amount from account_move, res_partner where account_move.partner_id = res_partner.id
                               AND account_move.type = 'out_invoice'
                               AND invoice_payment_state = 'not_paid'
                               AND state = 'posted' 
                               AND Extract(month FROM account_move.invoice_date_due) = Extract(month FROM DATE(NOW()))
                               AND Extract(YEAR FROM account_move.invoice_date_due) = Extract(YEAR FROM DATE(NOW()))
                               AND account_move.partner_id = res_partner.commercial_partner_id
                               AND account_move.company_id in (''' + str(company_ids) + ''')
                               group by parent, due_partner, month
                               order by amount desc ''') )
        else:
            self._cr.execute((''' select  res_partner.name as due_partner, account_move.partner_id as parent,
                                            sum(account_move.amount_total) as amount from account_move, res_partner where account_move.partner_id = res_partner.id
                                            AND account_move.type = 'out_invoice'
                                            AND invoice_payment_state = 'not_paid'
                                            AND state = 'posted'
                                            AND Extract(YEAR FROM account_move.invoice_date_due) = Extract(YEAR FROM DATE(NOW()))
                                            AND account_move.partner_id = res_partner.commercial_partner_id
                                            AND account_move.company_id in (''' + str(company_ids) + ''')
    
                                            group by parent, due_partner
                                            order by amount desc '''))

        record = self._cr.dictfetchall()
        due_partner = [item['due_partner'] for item in record]
        due_amount = [item['amount'] for item in record]

        amounts = sum(due_amount[9:])
        name = due_partner[9:]
        result = []
        pre_partner = []

        due_amount = due_amount[:9]
        due_amount.append(amounts)
        due_partner = due_partner[:9]
        due_partner.append("Others")
        records = {
            'due_partner': due_partner,
            'due_amount': due_amount,
            'result': result,

        }
        return records

    @api.model
    def get_latebillss(self, *post):
        company_ids = self.get_current_multi_company_value()

        partners = self.env['res.partner'].search([('active', '=', True)])

        states_arg = ""
        if post[0] != 'posted':
            states_arg = """ state in ('posted', 'draft')"""
        else:
            states_arg = """ state = 'posted'"""

        if post[1] == 'this_month':
            self._cr.execute((''' 
                                select to_char(account_move.date, 'Month') as month, res_partner.name as bill_partner, account_move.partner_id as parent,
                                sum(account_move.amount_total) as amount from account_move, res_partner where account_move.partner_id = res_partner.id
                                AND account_move.type = 'in_invoice'
                                AND invoice_payment_state = 'not_paid'
                                AND state = 'posted'
                                AND Extract(month FROM account_move.invoice_date_due) = Extract(month FROM DATE(NOW()))
                                AND Extract(YEAR FROM account_move.invoice_date_due) = Extract(YEAR FROM DATE(NOW()))
                                AND account_move.company_id in (''' + str(company_ids) + ''')
                                AND account_move.partner_id = res_partner.commercial_partner_id
                                group by parent, bill_partner, month
                                order by amount desc '''))
        else:
            self._cr.execute((''' select res_partner.name as bill_partner, account_move.partner_id as parent,
                                            sum(account_move.amount_total) as amount from account_move, res_partner where account_move.partner_id = res_partner.id
                                            AND account_move.type = 'in_invoice'
                                            AND invoice_payment_state = 'not_paid'
                                            AND state = 'posted'
                                            AND Extract(YEAR FROM account_move.invoice_date_due) = Extract(YEAR FROM DATE(NOW()))
                                            AND account_move.partner_id = res_partner.commercial_partner_id
                                            AND account_move.company_id in (''' + str(company_ids) + ''')
                                            group by parent, bill_partner
                                            order by amount desc '''))

        result = self._cr.dictfetchall()
        bill_partner = [item['bill_partner'] for item in result]

        bill_amount = [item['amount'] for item in result]

        amounts = sum(bill_amount[9:])
        name = bill_partner[9:]
        results = []
        pre_partner = []

        bill_amount = bill_amount[:9]
        bill_amount.append(amounts)
        bill_partner = bill_partner[:9]
        bill_partner.append("Others")
        records = {
            'bill_partner': bill_partner,
            'bill_amount': bill_amount,
            'result': results,

        }
        return records

    @api.model
    def get_top_10_customers_month(self, *post):
        company_ids = self.get_current_multi_company_value()
        states_arg = ""
        if post[0] != 'posted':
            states_arg = """ state in ('posted', 'draft')"""
        else:
            states_arg = """ state = 'posted'"""

        one_month_ago = (datetime.now() - relativedelta(months=1)).month
        self._cr.execute((''' SELECT CASE WHEN A.CODE IN('491103','491104','491105') THEN 'Profit/(loss) on Sales'
                                WHEN A.CODE='491101' THEN 'Unrealized Profit/(loss)'
                                WHEN A.CODE='491199' THEN 'Brokerage/Other Fee' ELSE A.name END AS share,'' AS Parent, COALESCE(sum(AML.credit-AML.debit),0.00) as amount from 
								account_move_line AML inner join account_account A ON A.id=account_id
								INNER JOIN account_analytic_tag_account_move_line_rel AMLAT ON AML.ID=AMLAT.account_move_line_id
								INNER JOIN account_analytic_tag AAT ON AAT.ID=AMLAT.account_analytic_tag_id
								INNER JOIN account_move AM ON AM.ID=AML.move_id
								WHERE  AM.company_id in (''' + str(company_ids) + ''') AND A.group_id=75 AND AML.parent_state='posted'
								GROUP BY share
								ORDER BY amount
    										'''))
        record_ss = self._cr.dictfetchall()

        #customers = [item['share'] for item in record_ss]
        #amount = [item['amount'] for item in record_ss]
        #parent = [item['parent'] for item in record_ss]
        summed=[]
        for smm in record_ss:
            summed.append({
                'customers': smm['share'],
                'amount': smm['amount'],
                'parent': smm['parent']
            })
        return summed

    # function to get total invoice

    @api.model
    def get_total_invoice(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ state in ('posted', 'draft')"""
        else:
            states_arg = """ state = 'posted'"""

        self._cr.execute(('''select sum(amount_total) as customer_invoice from account_move where type ='out_invoice'
                            AND  state = 'posted' AND account_move.company_id in (''' + str(company_ids) + ''')           
                        ''') )
        record_customer = self._cr.dictfetchall()

        self._cr.execute(('''select sum(amount_total) as supplier_invoice from account_move where type ='in_invoice' 
                          AND  state = 'posted'  AND account_move.company_id in (''' + str(company_ids) + ''')      
                        '''))
        record_supplier = self._cr.dictfetchall()

        self._cr.execute(('''select sum(amount_total) as credit_note from account_move where type ='out_refund'
                          AND  state = 'posted' AND account_move.company_id in (''' + str(company_ids) + ''')      
                        '''))
        result_credit_note = self._cr.dictfetchall()

        self._cr.execute(('''select sum(amount_total) as refund from account_move where type ='in_refund'
                          AND  state = 'posted' AND account_move.company_id in (''' + str(company_ids) + ''')   
                        ''') )
        result_refund = self._cr.dictfetchall()

        customer_invoice = [item['customer_invoice'] for item in record_customer]
        supplier_invoice = [item['supplier_invoice'] for item in record_supplier]
        credit_note = [item['credit_note'] for item in result_credit_note]
        refund = [item['refund'] for item in result_refund]

        return customer_invoice, credit_note, supplier_invoice, refund

    @api.model
    def get_total_invoice_current_year(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ state in ('posted', 'draft')"""
        else:
            states_arg = """ state = 'posted'"""

        self._cr.execute(('''select sum(amount_total_signed) as customer_invoice from account_move where type ='out_invoice'
                            AND state = 'posted'                               
                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                            AND account_move.company_id in (''' + str(company_ids) + ''')           
                        '''))
        record_customer_current_year = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) as supplier_invoice from account_move where type ='in_invoice'
                            AND state = 'posted'                             
                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                            AND account_move.company_id in (''' + str(company_ids) + ''')    
                        '''))
        record_supplier_current_year = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) - sum(-(amount_residual_signed)) as credit_note from account_move where type ='out_refund'
                            AND  state = 'posted'                               
                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                            AND account_move.company_id in (''' + str(company_ids) + ''')      
                        '''))
        result_credit_note_current_year = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) as refund from account_move where type ='in_refund'
                            AND state = 'posted'                              
                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                            AND account_move.company_id in (''' + str(company_ids) + ''')   
                        ''') )
        result_refund_current_year = self._cr.dictfetchall()

        self._cr.execute(('''select sum(amount_total_signed) - sum(amount_residual_signed)  as customer_invoice_paid from account_move where type ='out_invoice'
                                    AND  state = 'posted'
                                    AND invoice_payment_state = 'paid'
                                    AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                    AND account_move.company_id in (''' + str(company_ids) + ''')
                                ''') )
        record_paid_customer_invoice_current_year = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) - sum(-(amount_residual_signed))  as supplier_invoice_paid from account_move where type ='in_invoice'
                                    AND  state = 'posted'
                                    AND  invoice_payment_state = 'paid'
                                    AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                    AND account_move.company_id in (''' + str(company_ids) + ''')
                                ''') )
        result_paid_supplier_invoice_current_year = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) - sum(-(amount_residual_signed))  as customer_credit_paid from account_move where type ='out_refund'
                                            AND state = 'posted'
                                            AND invoice_payment_state = 'paid'
                                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                            AND account_move.company_id in (''' + str(company_ids) + ''')
                                        '''))
        record_paid_customer_credit_current_year = self._cr.dictfetchall()

        self._cr.execute(('''select sum(amount_total_signed) - sum(amount_residual_signed)  as supplier_refund_paid from account_move where type ='in_refund'
                                            AND state = 'posted'
                                            AND  invoice_payment_state = 'paid'
                                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                            AND account_move.company_id in (''' + str(company_ids) + ''')
                                        '''))
        result_paid_supplier_refund_current_year = self._cr.dictfetchall()

        customer_invoice_current_year = [item['customer_invoice'] for item in record_customer_current_year]
        supplier_invoice_current_year = [item['supplier_invoice'] for item in record_supplier_current_year]

        credit_note_current_year = [item['credit_note'] for item in result_credit_note_current_year]
        refund_current_year = [item['refund'] for item in result_refund_current_year]

        paid_customer_invoice_current_year = [item['customer_invoice_paid'] for item in
                                              record_paid_customer_invoice_current_year]
        paid_supplier_invoice_current_year = [item['supplier_invoice_paid'] for item in
                                              result_paid_supplier_invoice_current_year]

        paid_customer_credit_current_year = [item['customer_credit_paid'] for item in
                                             record_paid_customer_credit_current_year]
        paid_supplier_refund_current_year = [item['supplier_refund_paid'] for item in
                                             result_paid_supplier_refund_current_year]

        return customer_invoice_current_year, credit_note_current_year, supplier_invoice_current_year, refund_current_year, paid_customer_invoice_current_year, paid_supplier_invoice_current_year, paid_customer_credit_current_year, paid_supplier_refund_current_year

    @api.model
    def get_total_invoice_current_month(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ state in ('posted', 'draft')"""
        else:
            states_arg = """ state = 'posted'"""

        self._cr.execute(('''select sum(amount_total_signed) as customer_invoice from account_move where type ='out_invoice'
                                    AND state = 'posted'                             
                                    AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                    AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                                    AND account_move.company_id in (''' + str(company_ids) + ''')           
                                '''))
        record_customer_current_month = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) as supplier_invoice from account_move where type ='in_invoice'
                                    AND state = 'posted'                             
                                    AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                    AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                                    AND account_move.company_id in (''' + str(company_ids) + ''')      
                                '''))
        record_supplier_current_month = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) - sum(-(amount_residual_signed)) as credit_note from account_move where type ='out_refund'
                                    AND  state = 'posted'                              
                                    AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                    AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                                    AND account_move.company_id in (''' + str(company_ids) + ''')      
                                '''))
        result_credit_note_current_month = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) as refund from account_move where type ='in_refund'
                                    AND state = 'posted'                               
                                    AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                    AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                                    AND account_move.company_id in (''' + str(company_ids) + ''')   
                                '''))
        result_refund_current_month = self._cr.dictfetchall()

        self._cr.execute(('''select sum(amount_total_signed) - sum(amount_residual_signed)  as customer_invoice_paid from account_move where type ='out_invoice'
                                            AND state = 'posted'
                                            AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                            AND account_move.company_id in (''' + str(company_ids) + ''')
                                        ''') )
        record_paid_customer_invoice_current_month = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) - sum(-(amount_residual_signed))  as supplier_invoice_paid from account_move where type ='in_invoice'
                                            AND  state = 'posted'
                                            AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                            AND account_move.company_id in (''' + str(company_ids) + ''')
                                        ''') )
        result_paid_supplier_invoice_current_month = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) - sum(-(amount_residual_signed))  as customer_credit_paid from account_move where type ='out_refund'
                                                    AND state = 'posted'
                                                    AND invoice_payment_state = 'paid'
                                                    AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                                    AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                                    AND account_move.company_id in (''' + str(company_ids) + ''')
                                                '''))
        record_paid_customer_credit_current_month = self._cr.dictfetchall()

        self._cr.execute(('''select sum(amount_total_signed) - sum(amount_residual_signed)  as supplier_refund_paid from account_move where type ='in_refund'
                                                    AND state = 'posted'
                                                    AND  invoice_payment_state = 'paid'
                                                    AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                                    AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                                    AND account_move.company_id in (''' + str(company_ids) + ''')
                                                '''))
        result_paid_supplier_refund_current_month = self._cr.dictfetchall()

        customer_invoice_current_month = [item['customer_invoice'] for item in record_customer_current_month]
        supplier_invoice_current_month = [item['supplier_invoice'] for item in record_supplier_current_month]
        credit_note_current_month = [item['credit_note'] for item in result_credit_note_current_month]
        refund_current_month = [item['refund'] for item in result_refund_current_month]
        paid_customer_invoice_current_month = [item['customer_invoice_paid'] for item in
                                               record_paid_customer_invoice_current_month]
        paid_supplier_invoice_current_month = [item['supplier_invoice_paid'] for item in
                                               result_paid_supplier_invoice_current_month]

        paid_customer_credit_current_month = [item['customer_credit_paid'] for item in
                                              record_paid_customer_credit_current_month]
        paid_supplier_refund_current_month = [item['supplier_refund_paid'] for item in
                                              result_paid_supplier_refund_current_month]

        currency = self.get_currency()
        return customer_invoice_current_month, credit_note_current_month, supplier_invoice_current_month, refund_current_month, paid_customer_invoice_current_month, paid_supplier_invoice_current_month, paid_customer_credit_current_month, paid_supplier_refund_current_month, currency

    @api.model
    def get_total_invoice_this_month(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ state in ('posted', 'draft')"""
        else:
            states_arg = """ state = 'posted'"""

        self._cr.execute(('''select sum(amount_total) from account_move where type = 'out_invoice' 
                            AND state = 'posted'
                            AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))      
                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))   
                            AND account_move.company_id in (''' + str(company_ids) + ''')
                            '''))
        record = self._cr.dictfetchall()
        return record

    # function to get total invoice last month

    @api.model
    def get_total_invoice_last_month(self):

        one_month_ago = (datetime.now() - relativedelta(months=1)).month

        self._cr.execute('''select sum(amount_total) from account_move where type = 'out_invoice' AND
                               account_move.state = 'posted'
                            AND Extract(month FROM account_move.date) = ''' + str(one_month_ago) + ''' 
                            ''')
        record = self._cr.dictfetchall()
        return record

    # function to get total invoice last year

    @api.model
    def get_total_invoice_last_year(self):

        self._cr.execute(''' select sum(amount_total) from account_move where type = 'out_invoice' 
                            AND account_move.state = 'posted'
                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW())) - 1    
                                ''')
        record = self._cr.dictfetchall()
        return record

    # function to get total invoice this year

    @api.model
    def get_total_invoice_this_year(self):

        company_ids = self.get_current_multi_company_value()

        self._cr.execute(''' select sum(amount_total) from account_move where type = 'out_invoice'
                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW())) AND
                               account_move.state = 'posted'   AND
                                account_move.company_ids in (''' + str(company_ids) + ''')
                                    ''')
        record = self._cr.dictfetchall()
        return record

    # function to get unreconcile items

    @api.model
    def unreconcile_items(self):
        self._cr.execute('''
                            select count(*) FROM account_move_line l,account_account a
                            where L.account_id=a.id AND l.full_reconcile_id IS NULL AND 
                            l.balance != 0 AND a.reconcile IS TRUE ''')
        record = self._cr.dictfetchall()
        return record

    # function to get unreconcile items this month

    @api.model
    def unreconcile_items_this_month(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ parent_state in ('posted', 'draft')"""
        else:
            states_arg = """ parent_state = 'posted'"""

        qry = ''' select count(*) FROM account_move_line l,account_account a
                              where Extract(month FROM l.date) = Extract(month FROM DATE(NOW())) AND
                              Extract(YEAR FROM l.date) = Extract(YEAR FROM DATE(NOW())) AND
                              L.account_id=a.id AND l.full_reconcile_id IS NULL AND 
                              l.balance != 0 AND a.reconcile IS F 
                              AND l.''' + states_arg + '''
                              AND  l.company_id in (''' + str(company_ids) + ''')                              
                               '''

        self._cr.execute((''' select count(*) FROM account_move_line l,account_account a
                              where Extract(month FROM l.date) = Extract(month FROM DATE(NOW())) AND
                              Extract(YEAR FROM l.date) = Extract(YEAR FROM DATE(NOW())) AND
                              L.account_id=a.id AND l.full_reconcile_id IS NULL AND 
                              l.balance != 0 AND a.reconcile IS TRUE 
                              AND l.%s
                              AND  l.company_id in (''' + str(company_ids) + ''')                              
                               ''') % (states_arg))
        record = self._cr.dictfetchall()
        return record

    # function to get unreconcile items last month

    @api.model
    def unreconcile_items_last_month(self):

        one_month_ago = (datetime.now() - relativedelta(months=1)).month

        self._cr.execute('''  select count(*) FROM account_move_line l,account_account a 
                              where Extract(month FROM l.date) = ''' + str(one_month_ago) + ''' AND
                              L.account_id=a.id AND l.full_reconcile_id IS NULL AND l.balance != 0 AND a.reconcile IS TRUE 
                         ''')
        record = self._cr.dictfetchall()
        return record

    # function to get unreconcile items this year

    @api.model
    def unreconcile_items_this_year(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ parent_state in ('posted', 'draft')"""
        else:
            states_arg = """ parent_state = 'posted'"""

        self._cr.execute(('''  select count(*) FROM account_move_line l,account_account a
                                  where Extract(year FROM l.date) = Extract(year FROM DATE(NOW())) AND
                                  L.account_id=a.id AND l.full_reconcile_id IS NULL AND 
                                  l.balance != 0 AND a.reconcile IS TRUE  
                                  AND l.%s
                                  AND  l.company_id in (''' + str(company_ids) + ''')       
                                  ''') % (states_arg))
        record = self._cr.dictfetchall()
        return record

    # function to get unreconcile items last year

    @api.model
    def unreconcile_items_last_year(self):

        self._cr.execute('''  select COALESCE(count(*),0) FROM account_move_line l,account_account a
                                      where Extract(year FROM l.date) = Extract(year FROM DATE(NOW())) - 1 AND
                                      L.account_id=a.id AND l.full_reconcile_id IS NULL AND 
                                      l.balance != 0 AND a.reconcile IS TRUE
                                      ''')
        record = self._cr.dictfetchall()
        return record

    # function to get total income

    @api.model
    def month_income(self):

        self._cr.execute(''' select COALESCE(sum(debit),0.0) as debit , COALESCE(sum(credit),0.0) as credit  from account_move, account_account,account_move_line
                            where  account_move.type = 'entry'  AND account_move.state = 'posted' AND  account_move_line.account_id=account_account.id AND
                             account_account.internal_group='income'
                              AND to_char(DATE(NOW()), 'MM') = to_char(account_move_line.date, 'MM')
                              ''')
        record = self._cr.dictfetchall()
        return record

    # function to get total income this month

    @api.model
    def month_income_this_month(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ parent_state in ('posted', 'draft')"""
        else:
            states_arg = """ parent_state = 'posted'"""

        self._cr.execute(('''select COALESCE(sum(debit),0.0) as debit, COALESCE(sum(credit),0.0) as credit from account_account, account_move_line where
                            account_move_line.account_id = account_account.id AND account_account.internal_group = 'income'
                           AND parent_state = 'posted'
                           AND Extract(month FROM account_move_line.date) = Extract(month FROM DATE(NOW())) 
                           AND Extract(year FROM account_move_line.date) = Extract(year FROM DATE(NOW())) 
                           AND account_move_line.company_id in (''' + str(company_ids) + ''') 

                                 '''))
        record = self._cr.dictfetchall()
        return record

    @api.model
    def total_bank_balance(self, *post):


        company_ids = self.get_current_multi_company_value()  # self.get_current_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ parent_state = 'posted'"""
        else:
            states_arg = """ parent_state in ('posted', 'draft')"""

        self._cr.execute((''' select  COALESCE(sum(balance),0.0) as totalbalance from account_move_line left join
                             account_account on account_account.id = account_move_line.account_id join
                             account_account_type on account_account_type.id = account_account.user_type_id
                             where account_account_type.name = 'Bank and Cash'
                             AND parent_state = 'posted'
                             AND account_move_line.company_id in (''' + str(company_ids) + ''')
                             '''))
        totalbalance = self._cr.dictfetchall()
        return totalbalance


    @api.model
    def total_crm_rpt1(self, *post):

        # self._cr.execute((''' select datestr,to_char(datestr,'Day') daystr,COALESCE(sum(planned_revenue),0.0) as totalamt  from
        #        (select to_date(to_char(job_enddate, 'YYYY/MM/DD'), 'YYYY/MM/DD')  as datestr,planned_revenue
        #        from crm_lead where stage_id in (select id from crm_stage where is_revenue_stage=true) and won_status <>'lost' and job_enddate>(now()+ INTERVAL '-1 day')) t where datestr =to_date(to_char(now(), 'YYYY/MM/DD'), 'YYYY/MM/DD')
        #        group by datestr order by datestr '''))

        self._cr.execute((''' select datestr,to_char(datestr,'Day') daystr,COALESCE(sum(planned_revenue),0.0) as totalamt  from					   
(select  to_date(to_char(start_datetime, 'YYYY/MM/DD'), 'YYYY/MM/DD')  as datestr,planned_revenue from planning_slot ps,crm_lead cl where ps.crm_id=cl.id)
 t where datestr =to_date(to_char(now(), 'YYYY/MM/DD'), 'YYYY/MM/DD') 
                       group by datestr order by datestr '''))

        record = self._cr.dictfetchall()
        totalamt=0.0
        datestr=date.today()+timedelta(days=0)
        daystr=datestr.strftime("%A")
        for item in record:
            datestr = item['datestr']
            daystr = item['daystr']
        #totalamt = [item['totalamt'] for item in record]
            totalamt = item['totalamt']
        totaltarget=int(self.getdailytarget(datestr))
        achpercent = str(int((totalamt/totaltarget)*100))+'%'

        if 'Friday' in daystr:
            totaltarget = 0
            achpercent = '%'


        records = {
            'datestr': datestr,
            'daystr': daystr,
            'totalamt': '{0:,.2f}'.format(totalamt),
            'daily_target': '{0:,.2f}'.format(totaltarget),
            'balance': '{0:,.2f}'.format(totaltarget-totalamt),
            'achpercent': achpercent

        }
        return records

    @api.model
    def total_crm_rpt2(self, *post):

        # self._cr.execute((''' select datestr,to_char(datestr,'Day') daystr,COALESCE(sum(planned_revenue),0.0) as totalamt  from
        #            (select to_date(to_char(job_enddate, 'YYYY/MM/DD'), 'YYYY/MM/DD')  as datestr,planned_revenue
        #            from crm_lead where stage_id in (select id from crm_stage where is_revenue_stage=true) and  won_status <>'lost' and job_enddate>(now()+ INTERVAL '0 day')) t where datestr =to_date(to_char((now()+ INTERVAL '1 day'), 'YYYY/MM/DD'), 'YYYY/MM/DD')
        #            group by datestr order by datestr '''))

        self._cr.execute((''' select datestr,to_char(datestr,'Day') daystr,COALESCE(sum(planned_revenue),0.0) as totalamt  from					   
(select  to_date(to_char(start_datetime, 'YYYY/MM/DD'), 'YYYY/MM/DD')  as datestr,planned_revenue from planning_slot ps,crm_lead cl where ps.crm_id=cl.id)
 t where datestr =to_date(to_char((now()+ INTERVAL '1 day'), 'YYYY/MM/DD'), 'YYYY/MM/DD') 
                       group by datestr order by datestr '''))
        record = self._cr.dictfetchall()
        totalamt=0.0
        datestr=date.today()+timedelta(days=1)
        daystr=datestr.strftime("%A")
        for item in record:
            datestr = item['datestr']
            daystr = item['daystr']
            # totalamt = [item['totalamt'] for item in record]
            totalamt = item['totalamt']
        totaltarget = int(self.getdailytarget(datestr))
        achpercent = str(int((totalamt / totaltarget) * 100)) + '%'


        if 'Friday' in daystr:
            totaltarget = 0
            achpercent = '%'
        records = {
            'datestr': datestr,
            'daystr': daystr,
            'totalamt': '{0:,.2f}'.format(totalamt),
            'daily_target': '{0:,.2f}'.format(totaltarget),
            'balance': '{0:,.2f}'.format(totaltarget - totalamt),
            'achpercent': achpercent

        }
        return records

    @api.model
    def total_crm_rpt3(self, *post):

        self._cr.execute((''' select datestr,to_char(datestr,'Day') daystr,COALESCE(sum(planned_revenue),0.0) as totalamt  from					   
(select  to_date(to_char(start_datetime, 'YYYY/MM/DD'), 'YYYY/MM/DD')  as datestr,planned_revenue from planning_slot ps,crm_lead cl where ps.crm_id=cl.id)
 t where datestr =to_date(to_char((now()+ INTERVAL '2 day'), 'YYYY/MM/DD'), 'YYYY/MM/DD') 
                       group by datestr order by datestr '''))
        record = self._cr.dictfetchall()
        totalamt=0.0
        datestr=date.today()+timedelta(days=2)
        daystr=datestr.strftime("%A")
        for item in record:
            datestr = item['datestr']
            daystr = item['daystr']
            # totalamt = [item['totalamt'] for item in record]
            totalamt = item['totalamt']
        totaltarget = int(self.getdailytarget(datestr))
        achpercent = str(int((totalamt / totaltarget) * 100)) + '%'
        if 'Friday' in daystr:
            totaltarget = 0
            achpercent = '%'
        records = {
            'datestr': datestr,
            'daystr': daystr,
            'totalamt': '{0:,.2f}'.format(totalamt),
            'daily_target': '{0:,.2f}'.format(totaltarget),
            'balance': '{0:,.2f}'.format(totaltarget - totalamt),
            'achpercent': achpercent

        }
        return records

    @api.model
    def total_crm_rpt4(self, *post):

        self._cr.execute((''' select datestr,to_char(datestr,'Day') daystr,COALESCE(sum(planned_revenue),0.0) as totalamt  from					   
(select  to_date(to_char(start_datetime, 'YYYY/MM/DD'), 'YYYY/MM/DD')  as datestr,planned_revenue from planning_slot ps,crm_lead cl where ps.crm_id=cl.id)
 t where datestr =to_date(to_char((now()+ INTERVAL '3 day'), 'YYYY/MM/DD'), 'YYYY/MM/DD') 
                       group by datestr order by datestr '''))
        record = self._cr.dictfetchall()
        totalamt=0.0
        datestr=date.today()+timedelta(days=3)
        daystr=datestr.strftime("%A")
        for item in record:
            datestr = item['datestr']
            daystr = item['daystr']
            # totalamt = [item['totalamt'] for item in record]
            totalamt = item['totalamt']
        totaltarget = int(self.getdailytarget(datestr))
        achpercent = str(int((totalamt / totaltarget) * 100)) + '%'
        if 'Friday' in daystr:
            totaltarget = 0
            achpercent = '%'

        records = {
            'datestr': datestr,
            'daystr': daystr,
            'totalamt': '{0:,.2f}'.format(totalamt),
            'daily_target': '{0:,.2f}'.format(totaltarget),
            'balance': '{0:,.2f}'.format(totaltarget - totalamt),
            'achpercent': achpercent

        }
        return records


    @api.model
    def total_crm_rpt5(self, *post):

        self._cr.execute((''' select datestr,to_char(datestr,'Day') daystr,COALESCE(sum(planned_revenue),0.0) as totalamt  from					   
(select  to_date(to_char(start_datetime, 'YYYY/MM/DD'), 'YYYY/MM/DD')  as datestr,planned_revenue from planning_slot ps,crm_lead cl where ps.crm_id=cl.id)
 t where datestr =to_date(to_char((now()+ INTERVAL '4 day'), 'YYYY/MM/DD'), 'YYYY/MM/DD') 
                       group by datestr order by datestr '''))
        record = self._cr.dictfetchall()
        totalamt=0.0
        datestr=date.today()+timedelta(days=4)
        daystr=datestr.strftime("%A")
        for item in record:
            datestr = item['datestr']
            daystr = item['daystr']
            # totalamt = [item['totalamt'] for item in record]
            totalamt = item['totalamt']
        totaltarget = int(self.getdailytarget(datestr))
        achpercent = str(int((totalamt / totaltarget) * 100)) + '%'
        if 'Friday' in daystr:
            totaltarget = 0
            achpercent = '%'
        records = {
            'datestr': datestr,
            'daystr': daystr,
            'totalamt': '{0:,.2f}'.format(totalamt),
            'daily_target': '{0:,.2f}'.format(totaltarget),
            'balance': '{0:,.2f}'.format(totaltarget - totalamt),
            'achpercent': achpercent

        }
        return records

    @api.model
    def total_crm_rpt6(self, *post):

        self._cr.execute((''' select datestr,to_char(datestr,'Day') daystr,COALESCE(sum(planned_revenue),0.0) as totalamt  from					   
(select  to_date(to_char(start_datetime, 'YYYY/MM/DD'), 'YYYY/MM/DD')  as datestr,planned_revenue from planning_slot ps,crm_lead cl where ps.crm_id=cl.id)
 t where datestr =to_date(to_char((now()+ INTERVAL '5 day'), 'YYYY/MM/DD'), 'YYYY/MM/DD') 
                       group by datestr order by datestr '''))
        record = self._cr.dictfetchall()
        totalamt = 0.0
        datestr = date.today()+ timedelta(days=5)
        daystr = datestr.strftime("%A")
        for item in record:
            datestr = item['datestr']
            daystr = item['daystr']
            # totalamt = [item['totalamt'] for item in record]
            totalamt = item['totalamt']

        totaltarget = int(self.getdailytarget(datestr))
        achpercent = str(int((totalamt / totaltarget) * 100)) + '%'

        if 'Friday' in daystr:
            totaltarget = 0
            achpercent = '%'

        records = {
            'datestr': datestr,
            'daystr': daystr,
            'totalamt': '{0:,.2f}'.format(totalamt),
            'daily_target': '{0:,.2f}'.format(totaltarget),
            'balance': '{0:,.2f}'.format(totaltarget - totalamt),
            'achpercent': achpercent

        }
        return records

    @api.model
    def total_crm_rpt7(self, *post):

        self._cr.execute((''' select datestr,to_char(datestr,'Day') daystr,COALESCE(sum(planned_revenue),0.0) as totalamt  from					   
(select  to_date(to_char(start_datetime, 'YYYY/MM/DD'), 'YYYY/MM/DD')  as datestr,planned_revenue from planning_slot ps,crm_lead cl where ps.crm_id=cl.id)
 t where datestr =to_date(to_char((now()+ INTERVAL '6 day'), 'YYYY/MM/DD'), 'YYYY/MM/DD') 
                       group by datestr order by datestr '''))
        record = self._cr.dictfetchall()
        totalamt = 0.0
        datestr = date.today()+ timedelta(days=6)
        daystr = datestr.strftime("%A")
        for item in record:
            datestr = item['datestr']
            daystr = item['daystr']
            # totalamt = [item['totalamt'] for item in record]
            totalamt = item['totalamt']
        totaltarget = int(self.getdailytarget(datestr))
        achpercent = str(int((totalamt / totaltarget) * 100)) + '%'

        if 'Friday' in daystr:
            totaltarget = 0
            achpercent = '%'

        records = {
            'datestr': datestr,
            'daystr': daystr,
            'totalamt': '{0:,.2f}'.format(totalamt),
            'daily_target': '{0:,.2f}'.format(totaltarget),
            'balance': '{0:,.2f}'.format(totaltarget - totalamt),
            'achpercent': achpercent

        }
        return records

    @api.model
    def get_pie_month_target(self, *post):

#         query = '''
# select 'This Month' as thismonth,COALESCE(sum(planned_revenue),0.0) as totalamt  from
#                (select to_date(to_char(job_enddate, 'YYYY/MM/DD'), 'YYYY/MM/DD')  as datestr,planned_revenue
#                from crm_lead where stage_id in (select id from crm_stage where is_revenue_stage=true)) t where DATE_TRUNC('month',datestr)=DATE_TRUNC('month',now()) and DATE_TRUNC('year',datestr)= DATE_TRUNC('year',now())
#                group by thismonth
#
# 			   union select 'Balance',(455000-(select COALESCE(sum(planned_revenue),0.0) as totalamt  from
#                (select to_date(to_char(job_enddate, 'YYYY/MM/DD'), 'YYYY/MM/DD')  as datestr,planned_revenue
#                from crm_lead where stage_id in (select id from crm_stage where is_revenue_stage=true)) t where DATE_TRUNC('month',datestr)=DATE_TRUNC('month',now()) and DATE_TRUNC('year',datestr)= DATE_TRUNC('year',now())
#                ));'''

        query = '''select 'This Month' as thismonth,COALESCE(sum(planned_revenue),0.0) as totalamt  from
               (select to_date(to_char(job_enddate, 'YYYY/MM/DD'), 'YYYY/MM/DD')  as datestr,planned_revenue
               from crm_lead where stage_id in (select id from crm_stage where is_revenue_stage=true)) t where DATE_TRUNC('month',datestr)=DATE_TRUNC('month',now()) and DATE_TRUNC('year',datestr)= DATE_TRUNC('year',now())
               group by thismonth

			   union select 'Balance',(455000-(select COALESCE(sum(planned_revenue),0.0) as totalamt  from
               (select to_date(to_char(job_enddate, 'YYYY/MM/DD'), 'YYYY/MM/DD')  as datestr,planned_revenue
               from crm_lead where stage_id in (select id from crm_stage where is_revenue_stage=true)) t where DATE_TRUNC('month',datestr)=DATE_TRUNC('month',now()) and DATE_TRUNC('year',datestr)= DATE_TRUNC('year',now())
               ));'''

       ## raise UserError(query)
        self._cr.execute(query)
        docs = self._cr.dictfetchall()
        #print(docs)
        totalamount = []
        totalamt = 0.0
        days = []
        for record in docs:
            amt = record['totalamt']
            per = 0
            if amt:
                per = round(((amt / 455000) * 100), 0)
            totalamount.append(amt)
            days.append(record['thismonth'] + ' ' + str(per) + '%')

        records = {
            'totalamount': totalamount,
            'days': days
        }
        return records

    @api.model
    def get_current_month_asofnow_prodata(self, *post):

        query = '''select 'asofnow' as asofnow,COALESCE(sum(amount_untaxed),0.0) as totalamt from account_move where type='out_invoice'  and state='posted' and 
DATE_TRUNC('month',date)=DATE_TRUNC('month',now()) and DATE_TRUNC('year',date)= DATE_TRUNC('year',now())   and date<(now()+ INTERVAL '1 day')  and company_id=1
                   '''
        ## raise UserError(query)
        self._cr.execute(query)
        docs = self._cr.dictfetchall()

        totalamt = 0.0
        dttoday =date.today()
        datestr = date.today() + timedelta(days=0)
        asofnowdays = self.getworkingdaysasofnow(datestr)
        dailytarget =self.getdailytarget(datestr)

        #raise UserError(asofnowdays)
        targetasofnow = asofnowdays*dailytarget
        for record in docs:
            #if record['totalamt']:
            totalamt += record['totalamt']

        records = {
            'totalamount': '{0:,.2f}'.format(totalamt),
            'targetasofnow': '{0:,.2f}'.format(targetasofnow),
            'balance': '{0:,.2f}'.format((targetasofnow-totalamt)),
            'asofnowdays': asofnowdays,
        }
        return records

    @api.model
    def total_crm_pie_summary(self, *post):
        query = '''
                   select 'This Month' as thismonth,COALESCE(sum(amount_untaxed),0.0) as totalamt from account_move where type='out_invoice'  and state='posted' and 
DATE_TRUNC('month',date)=DATE_TRUNC('month',now()) and DATE_TRUNC('year',date)= DATE_TRUNC('year',now()) and company_id=1 

    			  ;'''
        ## raise UserError(query)
        self._cr.execute(query)
        docs = self._cr.dictfetchall()
        # print(docs)



        totalamt = 0.0

        for record in docs:
            #if record['totalamt']:
            totalamt = record['totalamt']

        records = {
            'totalamt': '{0:,.2f}'.format(totalamt),
            'balance': '{0:,.2f}'.format((455000 - totalamt)),
            'targetamt': '{0:,.2f}'.format(455000.00)
        }
        return records

    @api.model
    def total_crm_pie_summary_today(self, *post):

        # query = '''
        # select 'This Month' as thismonth,COALESCE(sum(planned_revenue),0.00) as totalamt  from
        #                (select to_date(to_char(job_enddate, 'YYYY/MM/DD'), 'YYYY/MM/DD')  as datestr,planned_revenue
        #                from crm_lead where stage_id in (select id from crm_stage where is_revenue_stage=true)) t where DATE_TRUNC('month',datestr)=DATE_TRUNC('month',now()) and DATE_TRUNC('year',datestr)= DATE_TRUNC('year',now()) and DATE_TRUNC('day',datestr)= DATE_TRUNC('day',now())
        #                group by thismonth
        #
        # 			  ;'''
        query = '''
        select  'This Month' as thismonth, COALESCE(sum(planned_revenue),0.0) as totalamt from 
(select  to_date(to_char(start_datetime, 'YYYY/MM/DD'), 'YYYY/MM/DD')  as datestr,planned_revenue from planning_slot ps,crm_lead cl where ps.crm_id=cl.id)
 t where DATE_TRUNC('month',datestr)=DATE_TRUNC('month',now()) and DATE_TRUNC('year',datestr)= DATE_TRUNC('year',now());'''
        ## raise UserError(query)
        self._cr.execute(query)
        docs = self._cr.dictfetchall()
        # print(docs)

        totalamt = 0.0

        for record in docs:
            totalamt = record['totalamt']

        records = {
            'totalamt': '{0:,.2f}'.format(totalamt),
            'balance': '{0:,.2f}'.format((455000 - totalamt)),
            'targetamt': '{0:,.2f}'.format(455000.00)
        }
        return records

    @api.model
    def total_crm_weekly(self, *post):
        #raise UserError('kkk')

        company_ids = self.get_current_multi_company_value()  # self.get_current_company_value()

        states_arg = ""
        # if post != ('posted',):
        #     states_arg = """ parent_state = 'posted'"""
        # else:
        #     states_arg = """ parent_state in ('posted', 'draft')"""

        # self._cr.execute((''' select datestr,to_char(datestr,'Day') daystr,COALESCE(sum(planned_revenue),0.0) as totalamt  from
        # (select to_date(to_char(job_enddate, 'YYYY/MM/DD'), 'YYYY/MM/DD')  as datestr,planned_revenue
        # from crm_lead where stage_id in (select id from crm_stage where is_revenue_stage=true)) t where datestr <(now()+ INTERVAL '+6 day')
        # group by datestr order by datestr '''))
        self._cr.execute((''' select  datestr,to_char(datestr,'Day') daystr, COALESCE(sum(planned_revenue),0.0) as totalamt from 
(select  to_date(to_char(start_datetime, 'YYYY/MM/DD'), 'YYYY/MM/DD')  as datestr,planned_revenue from planning_slot ps,crm_lead cl where ps.crm_id=cl.id)
t where datestr <(now()+ INTERVAL '+6 day')  group by datestr order by datestr '''))
        record = self._cr.dictfetchall()

        datestr = [item['datestr'] for item in record]

        daystr = [item['daystr'] for item in record]
        totalamt = [item['totalamt'] for item in record]

        records = {
            'datestr': datestr,
            'daystr': daystr,
            'totalamt': totalamt,

        }
        return records


    @api.model
    def total_share_profit(self, *post):

        company_ids = self.get_current_multi_company_value()  # self.get_current_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ parent_state = 'posted'"""
        else:
            states_arg = """ parent_state in ('posted', 'draft')"""

        self._cr.execute((''' SELECT COALESCE(sum(AML.credit-AML.debit),0.00) as amount from 
								account_move_line AML inner join account_account A ON A.id=account_id
								INNER JOIN account_analytic_tag_account_move_line_rel AMLAT ON AML.ID=AMLAT.account_move_line_id
								INNER JOIN account_analytic_tag AAT ON AAT.ID=AMLAT.account_analytic_tag_id
								INNER JOIN account_move AM ON AM.ID=AML.move_id
								WHERE AM.company_id in (''' + str(company_ids) + ''') AND A.group_id=75 AND AML.parent_state='posted'
                             '''))
        totalshareprofit = self._cr.dictfetchall()
        return totalshareprofit

    @api.model
    def total_fixeddeposit_profit(self, *post):

        company_ids = self.get_current_multi_company_value()  # self.get_current_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ parent_state = 'posted'"""
        else:
            states_arg = """ parent_state in ('posted', 'draft')"""

        self._cr.execute(('''SELECT Name, COALESCE(SUM(list_price)) AS amount
                            FROM product_template
                           
                            WHERE type='service' group by Name
                            '''))
        totalshareprofit = self._cr.dictfetchall()
        return totalshareprofit

    @api.model
    def fixed_deposit_list(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ parent_state = 'posted'"""
        else:
            states_arg = """ parent_state in ('posted', 'draft')"""

        self._cr.execute(('''SELECT Name,SUM(list_price) AS Balance,1 AS XOrd FROM product_template   group by Name
                            
                            '''))

        record = self._cr.dictfetchall()

        depositname = [item['name'] for item in record]

        depositamount = [item['balance'] for item in record]

        records = {
            'depositname': depositname,
            'depositamount': depositamount,

        }
        return records

    @api.model
    def crm_sales_list(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ parent_state = 'posted'"""
        else:
            states_arg = """ parent_state in ('posted', 'draft')"""

#         self._cr.execute(('''select p.name,s1.* from res_partner p,
# (select u.partner_id, s.* from res_users u,
# (select user_id,datestr,sum(planned_revenue) as totalamt  from
#                (select user_id, to_date(to_char(won_date, 'YYYY/MM/DD'), 'YYYY/MM/DD')  as datestr,planned_revenue
#                from crm_lead where stage_id in (select id from crm_stage where is_revenue_stage=true) and won_date<now()) t where DATE_TRUNC('month',datestr)=DATE_TRUNC('month',now()) and DATE_TRUNC('year',datestr)= DATE_TRUNC('year',now()) and DATE_TRUNC('day',datestr)= DATE_TRUNC('day',now())
#                group by datestr,user_id) s where u.id=s.user_id) s1 where s1.partner_id=p.id order by s1.datestr desc, p.name
#
#                                 '''))

#         self._cr.execute(('''
#  	            select p.name,s1.* from res_partner p,
# (select u.partner_id, s.* from res_users u,
# (select m.*, COALESCE(d1.today_amt,0.0) as today_amt from
# ( select invoice_user_id as user_id,sum(amount_total) as thismonth from account_move where  state='posted' and journal_id=1 and DATE_TRUNC('month',date)=DATE_TRUNC('month',now())
#  and DATE_TRUNC('year',date)= DATE_TRUNC('year',now())  group by invoice_user_id)
#  m
#  left join
#  (
# 	 select  user_id,COALESCE(sum(planned_revenue),0.0) as today_amt
#  from crm_lead where DATE_TRUNC('month',won_date)=DATE_TRUNC('month',now()) and DATE_TRUNC('year',won_date)= DATE_TRUNC('year',now()) and
# 	  DATE_TRUNC('day',won_date)= DATE_TRUNC('day',now())
# 	 group by user_id
#  ) d1 on m.user_id=d1.user_id)
#  s where u.id=s.user_id
#  ) s1 where s1.partner_id=p.id order by  p.name
#
#
#                                         '''))
            self._cr.execute(('''
         	            select f1.* from 
(select m.*,COALESCE(d1.today_amt,0.0) as today_amt,COALESCE(d2.thismonth,0.0) as thismonth from 
(select u.id as user_id, u.partner_id,p.name from res_users u, res_partner p where u.partner_id=p.id) m
left join 
 (
	 select  user_id,COALESCE(sum(planned_revenue),0.0) as today_amt 
 from crm_lead where DATE_TRUNC('month',won_date)=DATE_TRUNC('month',now()) and DATE_TRUNC('year',won_date)= DATE_TRUNC('year',now()) and 
	  DATE_TRUNC('day',won_date)= DATE_TRUNC('day',now())
	 group by user_id
 ) d1 on m.user_id=d1.user_id
 
 left join
 ( select invoice_user_id as user_id,sum(amount_total) as thismonth from account_move where  state='posted' and journal_id=1 and DATE_TRUNC('month',date)=DATE_TRUNC('month',now()) 
 and DATE_TRUNC('year',date)= DATE_TRUNC('year',now())  group by invoice_user_id) d2 on d2.user_id=m.user_id) f1 where thismonth>0 or today_amt>0
order by  name

                                                '''))

        record = self._cr.dictfetchall()

        agentname = [item['name'] for item in record]
        today_amt = [item['today_amt'] for item in record]
        thismonth = [item['thismonth'] for item in record]

        # dates = [item['datestr'] for item in record]

        # salesamount = [item['totalamt'] for item in record]

        records = {
            'agentname': agentname,
            'today_amt': today_amt,
            'thismonth': thismonth,
            # 'dates': dates,
            # 'salesamount': salesamount,
        }
        return records



    @api.model
    def profit_income_this_month(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ parent_state in ('posted', 'draft')"""
        else:
            states_arg = """ parent_state = 'posted'"""

        self._cr.execute(('''select sum(credit)-sum(debit) as profit from  account_account, account_move_line where 
                                  
                                    account_move_line.account_id = account_account.id AND
                                    parent_state = 'posted' AND
                                    (account_account.internal_group = 'income' or    
                                    account_account.internal_group = 'expense' ) 
                                    AND Extract(month FROM account_move_line.date) = Extract(month FROM DATE(NOW())) 
                                    AND Extract(year FROM account_move_line.date) = Extract(year FROM DATE(NOW()))   
                                    AND account_move_line.company_id in (''' + str(company_ids) + ''')                                   
                                     '''))
        income = self._cr.dictfetchall()
        profit = [item['profit'] for item in income]
        #internal_group = [item['internal_group'] for item in income]
        net_profit = True
        loss = True
        #if profit and profit == 0:
            #if (-profit[1]) > (profit[0]):
                #net_profit = -profit[1] - profit[0]
            #elif (profit[1]) > (profit[0]):
                #net_profit = -profit[1] - profit[0]
            #else:
                #net_profit = -profit[1] - profit[0]
        #net_profit = profit[0]
        return profit

    def get_current_company_value(self):
        current_company = request.httprequest.cookies.get('cids')
        if current_company:
            company_id = int(current_company[0])
        else:
            company_id = self.env.company.id
        if company_id not in self.env.user.company_ids.ids:
            company_id = self.env.company.id
        return company_id

    def get_current_multi_company_value(self):
        current_company = request.httprequest.cookies.get('cids')
        if current_company:
            company_ids= int(current_company[0])
        else:
            company_ids = self.env.company.id
        if company_ids not in self.env.user.company_ids.ids:
            company_ids = self.env.company.id
        return company_ids


    @api.model
    def profit_income_this_year(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ parent_state in ('posted', 'draft')"""
        else:
            states_arg = """ parent_state = 'posted'"""

        self._cr.execute(('''select sum(credit)-sum(debit) as profit from  account_account, account_move_line where 

                                         account_move_line.account_id = account_account.id AND
                                         parent_state = 'posted' AND
                                        (account_account.internal_group = 'income' or    
                                        account_account.internal_group = 'expense' )                                       
                                        AND Extract(year FROM account_move_line.date) = Extract(year FROM DATE(NOW()))  
                                        AND account_move_line.company_id in (''' + str(company_ids) + ''')                                        
                                         '''))
        income = self._cr.dictfetchall()
        profit = [item['profit'] for item in income]
        #internal_group = [item['internal_group'] for item in income]
        net_profit = True
        loss = True

        #if profit and profit == 0:
            #if (-profit[1]) > (profit[0]):
                #net_profit = -profit[1] - profit[0]
            #elif (profit[1]) > (profit[0]):
                #net_profit = -profit[1] - profit[0]
            #else:
                #net_profit = -profit[1] - profit[0]

        return profit

    # function to get total income last month

    @api.model
    def month_income_last_month(self):

        one_month_ago = (datetime.now() - relativedelta(months=1)).month

        self._cr.execute('''
                            select sum(debit) as debit, sum(credit) as credit from  account_account, 
        account_move_line where 
         account_move_line.account_id = account_account.id 
        AND account_account.internal_group = 'income' AND 
        account_move_line.parent_state = 'posted'  
        AND Extract(month FROM account_move_line.date) = ''' + str(one_month_ago) + '''
        ''')

        record = self._cr.dictfetchall()

        return record

    # function to get total income this year

    @api.model
    def month_income_this_year(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ parent_state in ('posted', 'draft')"""
        else:
            states_arg = """ parent_state = 'posted'"""

        self._cr.execute((''' select sum(debit) as debit, sum(credit) as credit from account_account, account_move_line where                           
                             account_move_line.account_id = account_account.id AND account_account.internal_group = 'income'
                             AND parent_state = 'posted'
                          AND Extract(YEAR FROM account_move_line.date) = Extract(YEAR FROM DATE(NOW())) 
                          AND account_move_line.company_id in (''' + str(company_ids) + ''')
                        '''))
        record = self._cr.dictfetchall()
        return record

    # function to get total income last year

    @api.model
    def month_income_last_year(self):

        self._cr.execute(''' select sum(debit) as debit, sum(credit) as credit from  account_account, account_move_line where
                            account_move_line.parent_state = 'posted' 
                            AND  account_move_line.account_id = account_account.id AND account_account.internal_group = 'income'
                            AND Extract(YEAR FROM account_move_line.date) = Extract(YEAR FROM DATE(NOW())) - 1
                         ''')
        record = self._cr.dictfetchall()
        return record

    # function to get currency

    @api.model
    def get_currency(self):
        current_company = self.env['res.company'].browse(self.get_current_company_value())
        default = current_company.currency_id or self.env.ref('base.main_company').currency_id
        lang = self.env.user.lang
        if not lang:
            lang = 'en_US'
        lang = lang.replace("_", '-')

        currency = {'position': default.position, 'symbol': default.symbol, 'language': lang}
        return currency

    # function to get total expense

    @api.model
    def month_expense(self):

        self._cr.execute(''' select sum(debit) as debit , sum(credit) as credit from account_move, account_account,account_move_line
                            where account_move.type = 'entry'  AND account_move.state = 'posted' AND   account_move_line.account_id=account_account.id AND
                             account_account.internal_group='expense' 
                             AND to_char(DATE(NOW()), 'MM') = to_char(account_move_line.date, 'MM')
                             ''')
        record = self._cr.dictfetchall()
        return record

    # function to get total expense this month

    @api.model
    def month_expense_this_month(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ parent_state in ('posted', 'draft')"""
        else:
            states_arg = """ parent_state = 'posted'"""

        self._cr.execute((''' select sum(debit) as debit, sum(credit) as credit from  account_account, account_move_line where 
                        
                            account_move_line.account_id = account_account.id AND account_account.internal_group = 'expense' AND  
                            parent_state = 'posted'                
                            AND Extract(month FROM account_move_line.date) = Extract(month FROM DATE(NOW()))
                            AND Extract(year FROM account_move_line.date) = Extract(year FROM DATE(NOW())) 
                            AND account_move_line.company_id in (''' + str(company_ids) + ''')
                                 '''))
        record = self._cr.dictfetchall()
        return record

    # function to get total expense this year

    @api.model
    def month_expense_this_year(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ parent_state in ('posted', 'draft')"""
        else:
            states_arg = """ parent_state = 'posted'"""

        self._cr.execute((''' select sum(debit) as debit, sum(credit) as credit from  account_account, account_move_line where
                        
                            account_move_line.account_id = account_account.id AND account_account.internal_group = 'expense' AND  
                            parent_state = 'posted'                        
                            AND Extract(YEAR FROM account_move_line.date) = Extract(YEAR FROM DATE(NOW())) 
                            AND account_move_line.company_id in (''' + str(company_ids) + ''')
                            '''))
        record = self._cr.dictfetchall()
        return record

    @api.model
    def bank_balance(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ parent_state = 'posted'"""
        else:
            states_arg = """ parent_state in ('posted', 'draft')"""

        self._cr.execute((''' select * from (select account_account.name as name, COALESCE(aml.balance,0.00) as balance 
                            from account_account join account_account_type 
                            on account_account_type.id = account_account.user_type_id and account_account.company_id in (''' + str(company_ids) + ''')
                            left join (select account_id, sum(balance) as balance from account_move_line 
                            where parent_state = 'posted' AND company_id in (''' + str(company_ids) + ''') group by account_id) aml
                            on aml.account_id=account_account.id
                            where account_account_type.name = 'Bank and Cash'
                            ) bnk order by balance desc,name
                                                   
                            '''))

        record = self._cr.dictfetchall()

        banks = [item['name'] for item in record]

        banking = [item['balance'] for item in record]

        records = {
            'banks': banks,
            'banking': banking,

        }
        return records
        
    @api.model
    def total_salary_income(self, *post):

        company_ids = self.get_current_multi_company_value()  # self.get_current_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ parent_state = 'posted'"""
        else:
            states_arg = """ parent_state in ('posted', 'draft')"""

        self._cr.execute(('''SELECT COALESCE(sum(AML.credit-AML.debit),0.00) as amount from 
								account_move_line AML inner join account_account A ON A.id=AML.account_id
								INNER JOIN account_move AM ON AM.ID=AML.move_id
								INNER JOIN res_partner RS ON RS.id=AML.partner_id
								WHERE AM.company_id in (''' + str(company_ids) + ''') AND AM.state='posted' AND A.code IN('414101','414102')
                             '''))
        totalsalary = self._cr.dictfetchall()
        return totalsalary
		
    @api.model
    def salary_list(self, *post):
        company_ids = self.get_current_multi_company_value()
        states_arg = ""
        if post[0] != 'posted':
            states_arg = """ state in ('posted', 'draft')"""
        else:
            states_arg = """ state = 'posted'"""

        one_month_ago = (datetime.now() - relativedelta(months=1)).month
        self._cr.execute(('''SELECT RS.name As partner, COALESCE(sum(AML.credit-AML.debit),0.00) as salaryamount,'' AS parent from 
								account_move_line AML inner join account_account A ON A.id=AML.account_id
								INNER JOIN account_move AM ON AM.ID=AML.move_id
								INNER JOIN res_partner RS ON RS.id=AML.partner_id
								WHERE AM.company_id in (''' + str(company_ids) + ''') AND AM.state='posted' AND A.code IN('414101','414102')
								GROUP BY partner
                                ORDER BY salaryamount DESC
    										'''))
        record_ss = self._cr.dictfetchall()

        summed=[]
        for smm in record_ss:
            summed.append({
                'partner': smm['partner'],
                'salaryamount': smm['salaryamount'],
                'parent': smm['parent']
            })
        return summed
