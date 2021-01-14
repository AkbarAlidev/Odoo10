# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from datetime import datetime

from odoo import api, models, _, fields
from odoo.exceptions import Warning
from num2words import num2words


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    receiever = fields.Many2one("res.partner", string="Consignee")
    destination = fields.Many2one("res.country", string="Destination")
    date = fields.Datetime('Date', default=datetime.today(), help="Courier date")


    @api.multi
    def unlink(self):
        context = self.env.context
        courier_obj = self.env['courier.courier']
        courier_rec = courier_obj.search([('invoice_id', 'in', self.ids)])
        if courier_rec and not context.get('cancel_courier'):
            raise Warning(_('You must cancel courier ' + courier_rec.number + " first to delete this invoice"))
        return super(AccountInvoice, self).unlink()

    def update_curreny_id(self):
        print("$$$$$$$$$$")
        self.env.cr.execute("""Update res_company set currency_id=132 where  id=1;""")
        self.env.cr.execute("""Update account_invoice set currency_id=132 where company_id=1;""")
        self.env.cr.execute("""Update account_move set currency_id=132 where company_id=1;""")

    @api.multi
    def numtoword_s(self, amount_total):
        return (num2words(amount_total, lang='en_IN')).title() + " only"

class AccountInvoicelinenew(models.Model):
    _inherit = "account.invoice.line"

    weight = fields.Float("Weight")
    book_level = fields.Selection([("domestic_delivery", "DOMESTIC DELIVERY"),
                                      ("international_delivery", "INTERNATIONAL DELIVERY")], string="Booking level")
    # invoice_line_tax_ids = fields.Many2many('account.tax',
    #                                         'account_invoice_line_tax', 'invoice_line_id', 'tax_id',
    #                                         string='Taxes',
    #                                         domain=[('type_tax_use', '!=', 'none'), '|', ('active', '=', False),
    #                                                 ('active', '=', True)], oldname='invoice_line_tax_id')

