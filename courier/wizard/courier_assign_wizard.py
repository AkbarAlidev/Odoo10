# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class AssignDriverCourier(models.TransientModel):
    _name = "courier.assign.driver.wizard"
    _description = "Assign Driver for Courier"

    assign_to = fields.Many2one('hr.employee', 'Drivers', help='Drivers.')


    @api.multi
    def update_driver_courier(self):
        data = {}
        act_ids = self._context.get('active_ids')
        courier_records = self.env["courier.courier"].search([('id', 'in', act_ids)])
        for rec in courier_records:
            if rec.state=="inscan":
                rec.update({"delivery_driver_id":self.assign_to.id,"state":"outscan","assign_to":self.assign_to.id})
            elif rec.state=="ready_to_pickup":
                rec.update({"pickup_driver_id": self.assign_to.id,"assign_to":self.assign_to.id})
                rec.action_pickup_done()
        return True

