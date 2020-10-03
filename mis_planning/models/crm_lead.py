# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.tools.misc import formatLang
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
class MisCRMLead(models.Model):
    _inherit = 'crm.lead'

    planning_id=fields.Many2one('planning.slot', string='Planning ID')

    def action_transfer2planning(self):
        for rec in self:
            create_vals={
                'name': rec.name,
                'crm_id': rec.id ,
           }
        objplanning = self.env['planning.slot'].create(create_vals)
        self.planning_id=objplanning.id
        #raise UserError('Transferred to Planning')

