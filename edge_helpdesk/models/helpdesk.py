# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    amount_total = fields.Float(string='Total', related="sale_order_id.amount_total")
    user_id = fields.Many2one('res.users', string='Salesperson', related="sale_order_id.user_id")
