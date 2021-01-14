from odoo import api, fields, models,exceptions
from odoo.exceptions import UserError




class AssignDriverCourier(models.TransientModel):
    _name = "courier.inscan.wizard"
    _description = "inscan wizard"

    product_list = fields.One2many("product.barcode.list.wizard", "courier_warehouse_id")
    warehouse = fields.Many2one('stock.warehouse', string="Warehouse", help='Warehouse.')

    @api.multi
    def inscan_courier_button(self):
        for r in self:
            for i in r.product_list:
                courier = self.env["courier.courier"].search([("number", "=", i.barcode)], limit=1)
                if courier:
                    courier_state = courier.state
                    print(courier_state)
                    if courier_state == "invoiced":
                        self.env["courier.courier"].search([("number", "=", i.barcode)], limit=1).state = 'inscan'
                        self.env["courier.courier"].search([("number", "=", i.barcode)],
                                                           limit=1).target_warehouse_id = self.warehouse
                        print(self.env["courier.courier"].search([("number", "=", i.barcode)], limit=1).state)
                    else:
                        raise exceptions.Warning('In order to Inscan a courier you must create invoice first')
                else:
                    raise exceptions.Warning('This courier does not exist')
                return True




class ProductBarcodeList(models.TransientModel):
    _name = "product.barcode.list.wizard"

    barcode = fields.Char()
    courier_warehouse_id = fields.Many2one("courier.inscan.wizard")

