# -*- coding: utf-8 -*-

from odoo import models, fields


class UpdatePlannedRevenue(models.TransientModel):
    _name = 'update.planned.revenue'
    _description = 'Update Planned Revenue'


    def update_planned_revenue(self):
        amc_line = self.env['amc.contract.line'].search([]).filtered(lambda o: \
            (o.lead_id))
        callout_line = self.env['callout.contract.line'].search([]).filtered(lambda o: \
            (o.lead_id))
        if amc_line:
            for each in amc_line:
                each.amount = each.lead_id.planned_revenue
        if callout_line:
            for data in callout_line:
                data.amount = data.lead_id.planned_revenue