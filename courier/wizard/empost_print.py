from odoo import api, fields, models


class SenderAccountStatement(models.TransientModel):
    _name = "empost.report"
    _description = "Empost report print"

    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")

    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['date_from', 'date_to'])[0])
        return self.env['report'].get_action(self, 'courier.courier_empost')

    @api.multi
    def get_record(self):
        # courier_ids_inters = self.env['courier.courier'].search(
        #     [('date', '<=', self.to_date),
        #      ('date', '>=', self.from_date),
        #      ('booking_level', '=', 'international_delivery')])
        # total_above_inter = len(self.env['courier.courier'].search(
        #     [('date', '<=', self.to_date), ('date', '>=', self.from_date), ('chargeable_weight', '>', 30),
        #      ('booking_level', '=', 'international_delivery')]))
        # total_below_inter = len(self.env['courier.courier'].search(
        #     [('date', '<=', self.to_date), ('date', '>=', self.from_date), ('chargeable_weight', '<=', 30),
        #      ('booking_level', '=', 'international_delivery')]))
        # total_amount_above_inter = 0
        # total_amount_below_inter = 0
        # for courier_id_inter in courier_ids_inters:
        #     if courier_id_inter.chargeable_weight > 30:
        #         total_amount_above_inter = total_amount_above_inter + courier_id_inter.final_price
        #     elif courier_id_inter.chargeable_weight <= 30:
        #         total_amount_below_inter = total_amount_below_inter + courier_id_inter.final_price
        #
        # courier_ids_doms = self.env['courier.courier'].search(
        #     [('date', '<=', self.to_date),
        #      ('date', '>=', self.from_date),
        #      ('booking_level', '=', 'domestic_delivery')])
        # total_above_dom = len(self.env['courier.courier'].search([('date', '<=', self.to_date),('date', '>=', self.from_date),('chargeable_weight', '>', 30),('booking_level', '=', 'domestic_delivery')]))
        # total_below_dom = len(self.env['courier.courier'].search([('date', '<=', self.to_date),('date', '>=', self.from_date),('chargeable_weight', '<=', 30),('booking_level', '=', 'domestic_delivery')]))
        # total_amount_above_dom = 0
        # total_amount_below_dom = 0
        # for courier_ids_dom in courier_ids_doms:
        #     if courier_ids_dom.chargeable_weight > 30:
        #         total_amount_above_dom = total_amount_above_dom + courier_ids_dom.final_price
        #     elif courier_ids_dom.chargeable_weight <= 30:
        #         total_amount_below_dom = total_amount_below_dom + courier_ids_dom.final_price
        # data = []
        # data.append({
        #     'from_date': self.from_date,
        #     'to_date': self.to_date,
        #     'total_above_inter': total_above_inter,
        #     'total_below_inter': total_below_inter,
        #     'total_amount_above_inter': total_amount_above_inter,
        #     'total_amount_below_inter': total_amount_below_inter,
        #     'total_above_dom': total_above_dom,
        #     'total_below_dom': total_below_dom,
        #     'total_amount_above_dom': total_amount_above_dom,
        #     'total_amount_below_dom': total_amount_below_dom,
        # })
        # return data
        inter_letter = self.env['courier.courier'].search(
            [('date', '<=', self.to_date),
             ('date', '>=', self.from_date),
             ('booking_level', '=', 'international_delivery'),
             ('courier_type_id', '=', 'Letter')])
        inter_documents = self.env['courier.courier'].search(
            [('date', '<=', self.to_date),
             ('date', '>=', self.from_date),
             ('booking_level', '=', 'international_delivery'),
             ('courier_type_id', '=', 'Documents')])
        inter_upto_30 = self.env['courier.courier'].search(
            [('date', '<=', self.to_date),
             ('date', '>=', self.from_date),
             ('booking_level', '=', 'international_delivery'),
             ('courier_type_id', 'not in',('Letter', 'Documents')),
             ('total_weight', '<=', 30)])
        inter_above_30 = self.env['courier.courier'].search(
            [('date', '<=', self.to_date),
             ('date', '>=', self.from_date),
             ('booking_level', '=', 'international_delivery'),
             ('courier_type_id', 'not in', ('Letter', 'Documents')),
             ('total_weight', '>', 30)])
        dom_letter = self.env['courier.courier'].search(
            [('date', '<=', self.to_date),
             ('date', '>=', self.from_date),
             ('booking_level', '=', 'domestic_delivery'),
             ('courier_type_id', '=', 'Letter')])
        dom_documents = self.env['courier.courier'].search(
            [('date', '<=', self.to_date),
             ('date', '>=', self.from_date),
             ('booking_level', '=', 'domestic_delivery'),
             ('courier_type_id', '=', 'Documents')])
        dom_upto_30 = self.env['courier.courier'].search(
            [('date', '<=', self.to_date),
             ('date', '>=', self.from_date),
             ('booking_level', '=', 'domestic_delivery'),
             ('courier_type_id', 'not in', ('Letter', 'Documents')),
             ('total_weight', '<=', 30)])
        dom_above_30 = self.env['courier.courier'].search(
            [('date', '<=', self.to_date),
             ('date', '>=', self.from_date),
             ('booking_level', '=', 'domestic_delivery'),
             ('courier_type_id', 'not in', ('Letter', 'Documents')),
             ('total_weight', '>', 30)])
        sub_total_qty = len(inter_letter) + len(inter_documents) + len(inter_upto_30) + len(inter_above_30) + len(dom_letter) + len(dom_documents) + len(dom_upto_30) + len(dom_above_30)
        inter_letter_price = 0
        inter_documents_price = 0
        inter_upto_30_price = 0
        inter_above_30_price = 0
        for inter_let in inter_letter:
            inter_letter_price = inter_letter_price + inter_let.final_price
        for inter_doc in inter_documents:
            inter_documents_price = inter_documents_price + inter_doc.final_price
        for inter_up in inter_upto_30:
            inter_upto_30_price = inter_upto_30_price + inter_up.final_price
        for inter_ab in inter_above_30:
            inter_above_30_price = inter_above_30_price + inter_ab.final_price

        inter_letter_price_tax = inter_letter_price / 10
        inter_documents_price_tax = inter_documents_price / 10
        inter_upto_30_price_tax = inter_upto_30_price / 10

        dom_letter_price = 0
        dom_documents_price = 0
        dom_upto_30_price = 0
        dom_above_30_price = 0
        for dom_let in dom_letter:
            dom_letter_price = dom_letter_price + dom_let.final_price
        for dom_doc in dom_documents:
            dom_documents_price = dom_documents_price + dom_doc.final_price
        for dom_up in dom_upto_30:
            dom_upto_30_price = dom_upto_30_price + dom_up.final_price
        for dom_ab in dom_above_30:
            dom_above_30_price = dom_above_30_price + dom_ab.final_price

        dom_letter_price_tax = dom_letter_price / 10
        dom_documents_price_tax = dom_documents_price / 10
        dom_upto_30_price_tax = dom_upto_30_price / 10

        company = self.env['courier.courier'].search([], limit=1)
        name = company.company_id.partner_id.name
        street = company.company_id.partner_id.street
        street2 = company.company_id.partner_id.street2
        city = company.company_id.partner_id.city
        state = company.company_id.partner_id.state_id.name
        zip = company.company_id.partner_id.zip
        country = company.company_id.partner_id.country_id.name
        phone = company.company_id.partner_id.phone

        total_tax = inter_letter_price_tax + inter_documents_price_tax + inter_upto_30_price_tax + dom_letter_price_tax + dom_documents_price_tax + dom_upto_30_price_tax
        total_price = inter_letter_price + inter_documents_price + inter_upto_30_price + inter_above_30_price + dom_letter_price + dom_documents_price + dom_upto_30_price + dom_above_30_price
        data = []
        data.append({
            'from_date': self.from_date,
            'to_date': self.to_date,
            'inter_letter_qty': len(inter_letter),
            'inter_documents_qty': len(inter_documents),
            'inter_upto_30_qty': len(inter_upto_30),
            'inter_above_30_qty': len(inter_above_30),
            'dom_letter_qty': len(dom_letter),
            'dom_documents_qty': len(dom_documents),
            'dom_upto_30_qty': len(dom_upto_30),
            'dom_above_30_qty': len(dom_above_30),
            'sub_total_qty': sub_total_qty,
            'inter_letter_price': inter_letter_price,
            'inter_documents_price': inter_documents_price,
            'inter_upto_30_price': inter_upto_30_price,
            'inter_above_30_price': inter_above_30_price,
            'dom_letter_price': dom_letter_price,
            'dom_documents_price': dom_documents_price,
            'dom_upto_30_price': dom_upto_30_price,
            'dom_above_30_price': dom_above_30_price,
            'total_price': total_price,
            'inter_letter_price_tax': inter_letter_price_tax,
            'inter_documents_price_tax': inter_documents_price_tax,
            'inter_upto_30_price_tax': inter_upto_30_price_tax,
            'dom_letter_price_tax': dom_letter_price_tax,
            'dom_documents_price_tax': dom_documents_price_tax,
            'dom_upto_30_price_tax': dom_upto_30_price_tax,
            'total_tax': total_tax,

            'name': name,
            'street': street,
            'street2': street2,
            'city': city,
            'state': state,
            'zip': zip,
            'country': country,
            'phone': phone

        })
        return data