# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class DriverCommission(models.Model):
    _name = "driver.commission"
    _rec_name = 'commission_amount'

    commission_type = fields.Selection([('fixed', 'Fixed'),
                                        ('percentage', 'Percentage')], required=True, default='fixed')
    commission_amount = fields.Float(default=0.0)
    employee_id = fields.Many2one('hr.employee', string='Driver', required=True)
