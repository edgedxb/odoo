# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    is_amc = fields.Boolean('Is AMC', default=False)
    