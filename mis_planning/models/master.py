from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.tools.misc import formatLang
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
class MisArea(models.Model):
    _name = 'mis.area'
    _description ='Service Area'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Area", required=True, track_visibility='onchange')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Area already exists !"),
    ]
