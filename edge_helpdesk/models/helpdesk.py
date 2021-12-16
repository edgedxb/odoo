from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare
from werkzeug.urls import url_encode
class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    currency_id = fields.Many2one("res.currency", related='sale_order_id.currency_id', string="Currency")

    amount_total = fields.Monetary(string='Total', related="sale_order_id.amount_total")
    user_id = fields.Many2one('res.users', string='Salesperson', related="sale_order_id.user_id")
