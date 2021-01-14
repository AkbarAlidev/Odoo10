from odoo import api, fields, models


class ManualNumber(models.TransientModel):
    _name = "manual.number"
    _description = "manual number"

    courier_number = fields.Char(string="Courier number")

    @api.multi
    def update_courier_number(self):
        data = {}
        act_ids = self._context.get('active_ids')
        courier_records = self.env["courier.courier"].search([('id', 'in', act_ids)], limit=1)
        courier_records.number = self.courier_number
        return True
