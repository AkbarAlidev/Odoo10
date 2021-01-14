# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class SenderAccountStatement(models.TransientModel):
    _name = "sender.account.statement"
    _description = "Sender Account Statement"

    sender_id = fields.Many2one('res.partner', 'Sender', help='Responsible to sends courier', required=True)
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")

    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['sender_id', 'date_from', 'date_to'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['sender_id', 'date_from', 'date_to'])[0])
        return self.env['report'].get_action(self, 'courier.account_statement_report_template')

    @api.multi
    def get_record(self):
        courier_ids = self.env['courier.courier'].search(
            [('date', '<=', self.to_date),
             ('date', '>=', self.from_date),
             ('sender_id', '=', self.sender_id.id)])
        account_data = []
        for courier_id in courier_ids:
            # data_dict = {}
            account_data.append({
                'date': datetime.datetime.strptime(courier_id.date, '%Y-%m-%d').strftime('%d-%m-%Y'),
                'shipment_amount': courier_id.delivery_carrier_charges,
                'shipment_status': courier_id.state,
                'receipt_no': courier_id.number,
                'goods_price': courier_id.price,
                'total_amount': courier_id.invoice_total,
                'phone': courier_id.sender_id.phone,
                'city': courier_id.city,
                'delivered_date': courier_id.deliver_date,
                'receipt_data': datetime.datetime.strptime(courier_id.date, '%Y-%m-%d').strftime('%d-%m-%Y'),
            })
        return account_data

    @api.onchange('from_date')
    def _onchange_from_date(self):
        if self.from_date and self.to_date and self.to_date < self.from_date:
            self.to_date = self.from_date

    @api.onchange('to_date')
    def _onchange_to_date(self):
        if self.to_date and self.to_date < self.from_date:
            self.from_date = self.to_date
