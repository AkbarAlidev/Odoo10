from odoo import api, fields, models,exceptions
from odoo.exceptions import UserError




class AssignDriverCourier(models.TransientModel):
    _name = "courier.outscan.wizard"
    _description = "Out scan wizard"

    assign_to = fields.Many2one('hr.employee', string="Driver", help='Drivers.')
    product_list = fields.One2many("product.barcode.list.wizard", "courier_warehouse_id")

    @api.multi
    def outscan_courier_button(self):
        for r in self:
            for i in r.product_list:
                courier = self.env["courier.courier"].search([("number", "=", i.barcode)], limit=1)
                if courier:
                    courier_state = courier.state
                    print(courier_state)
                    if courier_state == "inscan":
                        self.env["courier.courier"].search([("number", "=", i.barcode)], limit=1).state = 'outscan'
                        self.env["courier.courier"].search([("number", "=", i.barcode)], limit=1).delivery_driver_id = self.assign_to
                        print(self.env["courier.courier"].search([("number", "=", i.barcode)], limit=1).state)
                    else:
                        raise exceptions.Warning('In order to Outscan a courier you must Inscan it first first')
                else:
                    raise exceptions.Warning('This courier does not exist')
                return True




class ProductBarcodeList(models.TransientModel):
    _name = "product.barcode.list.wizard"

    barcode = fields.Char()
    courier_warehouse_id = fields.Many2one("courier.inscan.wizard")