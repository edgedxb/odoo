# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
class MonthlyRevenueWizard(models.TransientModel):
    _name = 'monthly.revenue.wizard'

    year = fields.Char(string='Enter year', required=True)

    def action_create_report(self):
        try:
            if self.year.isnumeric()==False:
                raise ValidationError("Please enter year in 4 digit format!")
            elif len(self.year)!=4:
                raise ValidationError("Please enter year in 4 digit format!")
        except KeyError:
            raise ValidationError("Please enter year in 4 digit format!")

        context = dict(self._context)
        if context is None:
            context = {}
        data = self.read()[0] or {}

        datas = {
            'ids': self._ids,
            'data': data,
            'model': 'monthly.revenue.wizard'
        }
        return self.env.ref(
            'amc_contract_details.monthly_revenue_xls_report'
        ).report_action(self, data=datas)