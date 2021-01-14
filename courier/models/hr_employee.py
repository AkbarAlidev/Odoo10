# -*- coding: utf-8 -*-

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    is_driver = fields.Boolean(string='Is a Driver', domain=[("is_driver","=",True)],default=False, help="Enable this if this Employee is a driver.")
    driver_commission_ids = fields.One2many('driver.commission', 'employee_id', string='Commission')
    routing_id = fields.Many2one('courier.routing.path', 'Assigned Routing')
    zone_ids = fields.Many2many("zone.zone")
    passport_expire = fields.Date('Passport Expire Date')
    courier_list = fields.One2many("courier.courier","assign_to",string="Couriers")
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('widower', 'Widowed'),
        ('divorced', 'Divorced')
    ], string='Marital Status', groups='hr.group_hr_user')
