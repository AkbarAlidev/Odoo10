from odoo import api, fields, models


class ExportReport(models.TransientModel):
    _name = "export.report"
    _description = "Export report print"

    mawb_no = fields.Char(string="MAWB NO.")
    flight_number = fields.Char(string="Flight Number")
    etd = fields.Datetime(string="ETD")
    eta = fields.Datetime(string="ETA")
    destination = fields.Many2one('res.country')
    date = fields.Date(string="Date")

    @api.multi
    def check_report(self):
        couriers = self.env['courier.courier'].search(
            [('date', '=', self.date),
             ('booking_level', '=', 'international_delivery'),
             ('receiver_id.country_id.name', '=', self.destination.name)])
        print(couriers)
        data = {
            'eta': self.eta,
            'etd': self.etd,
            'mawb_no': self.mawb_no,
            'date': self.date,
            'flight_number': self.flight_number,
            'destination': self.destination.name
        }
        return {'type': 'ir.actions.report.xml',
                'report_name': 'courier.courier.xlsx',
                'datas': data
                }

    def _print_report(self, data):
        data['form'].update(self.read(['date_from', 'date_to'])[0])
        return self.env['report'].get_action(self, 'courier.courier_empost')