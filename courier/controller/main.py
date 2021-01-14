# -*- coding: utf-8 -*-
import base64
import binascii
import csv

import odoo.http as http
from odoo.http import request
from odoo.tools import misc, DEFAULT_SERVER_DATE_FORMAT, tempfile, os
import datetime
import pathlib
import werkzeug
import xlrd

from odoo import models, fields, tools, api
from odoo.exceptions import ValidationError, UserError


class CourierWebsite(http.Controller):

    @http.route('/page/transaction', type='http', auth='user', website=True)
    def Transaction_page(self, **kw):
        values = []
        user = request.env['res.users'].sudo().search([('id','=',request.env.user.id)])
        print("user;;",request.env.user.id)
        print("user;;",user)
        rec = request.env["courier.courier"].sudo().search([("sender_id","=",user.partner_id.id)])
        # rec = request.env["courier.courier"].sudo().search([])
        for r in rec:
            values.append({"name": str(r.name),
                           "courier_no": str(r.number) if r.number else "",
                           "sender": str(r.sender_id.name) if r.sender_id else "",
                           "receiver": str(r.receiver_id.name) if r.receiver_id else "",
                           # "courier_method": str(r.courier_method) if r.courier_method else"",
                           "courier_method": str(dict(r._fields['courier_method'].selection).get(
                               r.courier_method)) if r.courier_method else "",
                           "booking_date": str(r.date),
                           "service_type": str(
                               dict(r._fields['service_type'].selection).get(r.service_type)) if r.service_type else "",
                           "courier_type": str(r.courier_type_id.name) if r.courier_type_id else "",
                           "delivery_location": str(r.delivery_location_ids.street) if r.delivery_location_ids else "",
                           "street": str(r.delivery_location_ids.street2) if r.delivery_location_ids else "",
                           "city": str(r.delivery_location_ids.city) if r.delivery_location_ids else "",
                           "state": str(r.delivery_location_ids.state_id.name) if r.delivery_location_ids else "",
                           "zip": str(r.delivery_location_ids.zip) if r.delivery_location_ids else "",
                           "country": str(r.delivery_location_ids.country_id.name) if r.delivery_location_ids else "",
                           "status": str(dict(r._fields['state'].selection).get(r.state)) if r.state else "",
                           })
        print("vv", values)
        return http.request.render('courier.transaction', {"rec_list": values})

    @http.route('/page/booking_page', type='http', auth='user', website=True)
    def booking_courier(self, **kw):
        values = {}

        courier_type = request.env['courier.type']
        res_partner = request.env['res.partner']
        res_country = request.env['res.country']
        res_state = request.env['res.country.state']
        location_list = request.env['courier.carrier.location']
        values['courier_types'] = courier_type.search([])
        values['sender_ids'] = res_partner.search([])
        values['receiver_ids'] = res_partner.search([])
        values['country_ids'] = res_country.search([])
        values['state_ids'] = res_state.search([])
        values['location_list'] = location_list.search([])
        values['area_ids'] = request.env['area.area'].search([])
        values['zone_ids'] = request.env['zone.zone'].search([])

        return http.request.render('courier.booking_courier', values)

    # @http.route('/page/booking', type='http', auth='user', website=True)
    # def booking_level(self, **kw):
    #     values = {}
    #     values['booking_level'] = request.env['booking_level']
    #
    #     return http.request.render('courier.booking_courier', values)

    def timeconvert(self, str1):
        if str1[-2:] == "AM" and str1[:2] == "12":
            return "00" + str1[2:-2]
        elif str1[-2:] == "AM":
            return str1[:-2]
        elif str1[-2:] == "PM" and str1[:2] == "12":
            return str1[:-2]
        else:
            return str(int(str1[:2]) + 12) + str1[2:8]

    @http.route('/page/booking/import', type='http', auth='user', website=True)
    def upload_bulk_import(self, **kw):
        values = []

        return http.request.render('courier.booking_bulk_import', values)

    @http.route('/page/booking_page/create', type='http', auth='user', website=True)
    def create_booking_courier(self, **kw):
        values = {}
        courier = request.env['courier.courier']
        if kw:
            values['name'] = kw.get('name') or ''
            values['courier_type_id'] = kw.get('courier_type_id') or ''
            values['sender_id'] = kw.get('sender_id') or ''
            values['street'] = kw.get('street') or ''
            values['street2'] = kw.get('street2') or ''
            values['city'] = kw.get('sender_city') or ''
            values['state_id'] = kw.get('sender_state_id') or ''
            values['zip'] = kw.get('sender_zip') or ''
            values['area_id'] = kw.get('sender_area_id') or ''
            values['country_id'] = kw.get('sender_country_id') or ''
            values['receiver_id'] = kw.get('receiver_id') or ''
            values['cod'] = True if kw.get('cod') == 'yes' else False or ''
            values['service_type'] = kw.get('service_type') or ''
            values['courier_method'] = kw.get('courier_method') or ''
            values['date'] = kw.get('date') or ''
            if kw.get('booking_level'):
                print(kw.get('booking_level'))
                values['booking_level'] = kw.get('booking_level')

            values['uom_categ'] = kw.get('uom_categ') or ''
            values['no_of_pieces'] = kw.get('no_of_pieces') or ''
            values['no_of_pieces'] = kw.get('no_of_pieces') or ''
            # values['dimension'] = kw.get('dimension') or ''
            # values['weight'] = kw.get('weight') or ''
            # values['length'] = kw.get('length') or ''
            # values['width'] = kw.get('width') or ''
            # values['height'] = kw.get('height') or ''
            # values['dimensional_weight'] = kw.get('dimensional_weight') or ''
            # values['chargeable_weight'] = kw.get('chargeable_weight') or ''
            values['coast'] = kw.get('cost') or 1
            values['declared_value'] = kw.get('declared_value') or 0
            rate_id = request.env['res.currency'].search([("name", "=", 'USD')], limit=1).rate
            values['declared_value_inUSD'] = rate_id * float(kw.get('declared_value') or 0)

            values['demo_id'] = [(0, 0, {
                'length': kw.get('length') or '',
                'width': kw.get('width') or '',
                'height': kw.get('height') or '',
                'weight': kw.get('weight') or '',
                'chargeable_weight': kw.get('chargeable_weight'),
                'dimensional_weight': kw.get('dimensional_weight') or '',
                'product_description': kw.get('product_description') or '',
                'product_packaging_id': kw.get('product_packaging_id') or '',
                'no_of_boxes': kw.get('no_box') or '',
                'total_weight_id': kw.get('total_weight') or ''

            }), (0, 0, {
                'length': kw.get('length1') or '',
                'width': kw.get('width1') or '',
                'height': kw.get('height1') or '',
                'weight': kw.get('weight1') or '',
                'chargeable_weight': kw.get('chargeable_weight1') or '',
                'dimensional_weight': kw.get('dimensional_weight1') or '',
                'product_description': kw.get('product_description1') or '',
                'product_packaging_id': kw.get('product_packaging_id1') or '',
                'no_of_boxes': kw.get('no_box1') or '',
                'total_weight_id': kw.get('total_weight1') or ''
            }), (0, 0, {
                'length': kw.get('length2') or '',
                'width': kw.get('width2') or '',
                'height': kw.get('height2') or '',
                'weight': kw.get('weight2') or '',
                'chargeable_weight': kw.get('chargeable_weight2'),
                'dimensional_weight': kw.get('dimensional_weight2') or '',
                'product_description': kw.get('product_description2') or '',
                'product_packaging_id': kw.get('product_packaging_id2') or '',
                'no_of_boxes': kw.get('no_box2') or '',
                'total_weight_id': kw.get('total_weight2') or ''
            }), (0, 0, {
                'length': kw.get('length3') or '',
                'width': kw.get('width3') or '',
                'height': kw.get('height3') or '',
                'weight': kw.get('weight3') or '',
                'chargeable_weight': kw.get('chargeable_weight3'),
                'dimensional_weight': kw.get('dimensional_weight3') or '',
                'product_description': kw.get('product_description3') or '',
                'product_packaging_id3': kw.get('product_packaging_id3') or '',
                'no_of_boxes': kw.get('no_box3') or '',
                'total_weight_id': kw.get('total_weight3') or ''
            }), (0, 0, {
                'length': kw.get('length4') or '',
                'width': kw.get('width4') or '',
                'height': kw.get('height4') or '',
                'weight': kw.get('weight4') or '',
                'chargeable_weight': kw.get('chargeable_weight4'),
                'dimensional_weight': kw.get('dimensional_weight4') or '',
                'product_description': kw.get('product_description4') or '',
                'product_packaging_id': kw.get('product_packaging_id4') or '',
                'no_of_boxes': kw.get('no_box4') or '',
                'total_weight_id': kw.get('total_weight4') or ''
            })]
            values['delivered_by'] = kw.get('delivered_by') or ''
            if kw.get('delivered_by') == 'by_bike':
                price = request.env["area.area"].search([("id", "=", int(kw.get("receiver_area_id")))]).by_bike
                values['price'] = price
                values['delivered_by'] = 'by_bike'
                total_weight = float(kw.get('total_weight') or 0) + float(
                    kw.get('total_weight1') or 0) + float(
                    kw.get('total_weight2') or 0) + float(kw.get('chargeable_weight3') or 0) + float(
                    kw.get('total_weight3') or 0)
                values['total_price'] = (total_weight * float(kw.get('cost') or 1)) + price
                values['total_weight'] = total_weight
            elif kw.get('delivered_by') == 'by_car':
                values['delivered_by'] = 'by_car'
                price = request.env["area.area"].search([("id", "=", int(kw.get("receiver_area_id")))]).by_car
                values['price'] = price
                total_weight = float(kw.get('total_weight') or 0) + float(
                    kw.get('total_weight1') or 0) + float(
                    kw.get('total_weight2') or 0) + float(kw.get('chargeable_weight3') or 0) + float(
                    kw.get('total_weight3') or 0)
                values['total_price'] = (total_weight * float(kw.get('cost') or 1)) + price
                values['total_weight'] = total_weight



            if kw.get("sender_area_id"):
                area_id_rec = request.env["area.area"].search([("id", "=", int(kw.get("sender_area_id")))])
                values["zone_id"] = area_id_rec.zone_id.id

            values['delivery_location_ids'] = kw.get('delivery_location_ids') if kw.get(
                'delivery_location_ids') != '0' else False
            values['sender_location_id'] = kw.get('pickup_location_id') or ''
            if kw.get("receiver_id"):
                receiver_rec = request.env["courier.courier"].search([("id", "=", int(kw.get("receiver_id")))])
                rarea_id_rec = request.env["area.area"].search([("id", "=", int(kw.get("receiver_area_id")))])
                receiver_rec.write({
                    "street": kw.get('receiver_street') or '',
                    "street2": kw.get('receiver_street2') or '',
                    "city": kw.get('receiver_city') or '',
                    "state_id": kw.get('receiver_state_id') or '',
                    "zip": kw.get('receiver_zip') or '',
                    "area_id": kw.get('receiver_area_id') or '',
                    "country_id": kw.get('receiver_country_id') or '',
                    "zone_id": rarea_id_rec.zone_id.id if rarea_id_rec else ''
                })
                if kw.get('weight'):
                    w = float(kw.get('weight'))
                    p = receiver_rec.zone_id.price if receiver_rec.zone_id else 0
                    type = (kw.get('service_type'))
                    # values["price"]=request.env["courier.courier"].sudo().cal_price(w,type,p)
                if kw.get("courier_method") == "delivery":
                    values["courier_zone_id"] = receiver_rec.zone_id.id
                else:
                    if kw.get("pickup_location_id"):
                        sender_location_id = request.env["courier.carrier.location"].search(
                            [("id", "=", int(kw.get("pickup_location_id")))])
                        values["courier_zone_id"] = sender_location_id.zone_id.id
            date_of_pickup = kw.get('pickup_date') or ''
            time_of_pickup = kw.get('pickup_time') or ''
            if date_of_pickup and time_of_pickup:
                pickup = str(date_of_pickup) + str(" " + time_of_pickup + ":00")
                values['pickup_date_time'] = pickup
            # vv = datetime.datetime.strptime(pickup, DEFAULT_SERVER_DATE_FORMAT+" %H:%M:%S")
            # print(vv)
            # values['product_description'] = kw.get('product_description') or ''
            print(values)
            courier_id = courier.create(values)
            courier_id.write({"name": courier_id.sender_id.name})
            values['courier_id'] = courier_id

        return http.request.render('courier.booking_courier_success', values)

    def csv_validator(self, xml_name):
        name, extension = os.path.splitext(xml_name)
        return True if extension == '.csv' else False

    @http.route(['/bulkimport'], type='http', auth='user', csrf=False, website=True)
    def import_buttoncsv(self, **post):
        if post:
            msg = ""
            Attachments = request.env['ir.attachment']
            name = post.get('attachment').filename
            file = post.get('attachment')
            attachment_id = Attachments.create({
                'name': name,
                'type': 'binary',
                'datas': base64.b64encode(file.read()),
                'res_model': 'couirer.couirer',
            })
            result = {}
            if attachment_id:
                if not self.csv_validator(name):
                    raise UserError(("kindly upload  .csv"))
                file_path = tempfile.gettempdir() + '/file.csv'
                file_data = attachment_id.datas.decode('base64')
                data = file_data
                f = open(file_path, 'wb')
                f.write(file_data)
                # f.write(data.decode('base64'))
                f.close()
                archive = csv.DictReader(open(file_path))
                archive_lines = []
                try:
                    for line in archive:
                        archive_lines.append(line)

                    for row in archive_lines:
                        print("line", row)
                        customer_name = row.get("Customer", "")
                        customer_phone = row.get("Tel1", "")
                        customer_mobile = row.get("Tel2", "")
                        customer_address = row.get("Address", "")
                        customer_city = row.get("City", "")
                        customer_area = row.get("Area", "")
                        customer_zone = row.get("Zone", "")
                        customer_zip = row.get("Zip", "")
                        customer_state = row.get("State", "")
                        customer_country = row.get("Country", "")
                        courier_method = row.get("Courier Method", "")
                        courier_type = row.get("Courier Type", "")
                        service_type_value = row.get("Service Type", "")
                        service_type = ""
                        if service_type_value:
                            if service_type_value == "Same Day Delivery Service(Bullet Service)":
                                service_type = "same_day_delivery_service"
                            if service_type_value == "Next Day Delivery Service":
                                service_type = "next_day_delivery_service"
                            if service_type_value == "COD E-commerce Shipments":
                                service_type = "cod_ecommerce_shipments"
                            if service_type_value == "Return Service(RTS)":
                                service_type = "return_service"
                            if service_type_value == "International OutBond Express":
                                service_type = "internal_outbond_express"
                        # courier_date_val = datetime(*xlrd.xldate_as_tuple(str(row[11].value), 0))
                        # print("-",datetime.strptime(str(row[11].value).encode('utf-8'), "%Y-%m-%d"))
                        courier_date_val = "2020-03-21"
                        recever_name = row.get("Recipient", "")
                        recever_phone = row.get("Recipient Phone", "")
                        recever_phone = row.get("Recipient Mobile", "")
                        amount = row.get("Price", "")
                        weight = row.get("Weight", "")
                        paid = row.get("", "")
                        no_of_pieces = row.get("Quantity", "")
                        cod = row.get("COD", "")

                        if courier_method == "Pickup & Delivery":
                            courier_method = "pickup_and_delivery"
                        else:
                            courier_method = "delivery"

                        existing_country = request.env['res.country'].search([("name", "ilike", customer_country)],
                                                                             limit=1)
                        if existing_country:
                            customer_country_id = existing_country.id
                        else:
                            rec_country_id = request.env['res.country.state'].create({"name": customer_state})
                            customer_country_id = rec_country_id.id
                        existing_state = request.env['res.country.state'].search([("name", "ilike", customer_state)],
                                                                                 limit=1)
                        if existing_state:
                            customer_state_id = existing_state.id
                        else:
                            rec_state_id = request.env['res.country.state'].create(
                                {"name": customer_state, "code": customer_state, "country_id": customer_country_id})
                            customer_state_id = rec_state_id.id
                        existing_courier_type = request.env["courier.type"].search([("name", "ilike", courier_type)],
                                                                                   limit=1)
                        if existing_courier_type:
                            courier_type_id = existing_courier_type.id
                        else:
                            rec_courier_type = request.env['courier.type'].create(
                                {"name": courier_type, "code": courier_type})
                            courier_type_id = rec_courier_type.id
                        customer_area_rec = False
                        if customer_area:
                            customer_area_rec = request.env['area.area'].search([("name", "=", customer_area)])
                            if not customer_area_rec:
                                customer_zone_rec = request.env['zone.zone'].search([("name", "=", customer_zone)])
                                if not customer_zone_rec:
                                    customer_zone_rec = request.env['zone.zone'].create({"name": customer_zone})
                                customer_area_rec = request.env['area.area'].create(
                                    {"name": customer_area, "zone_id": customer_zone_rec.id})
                        print (customer_area_rec)
                        if customer_name:
                            exisitng_customer = request.env['res.partner'].search(
                                [("name", "ilike", customer_name), ("phone", "=", customer_phone)])
                            if not exisitng_customer:
                                exisitng_customer = request.env['res.partner'].create(
                                    {"name": customer_name, "phone": customer_phone,
                                     "mobile": customer_mobile,
                                     'street': str(customer_address).split('.')[0],
                                     'zip': str(customer_zip).split('.')[0],
                                     'city': str(customer_city).split('.')[0],
                                     'state_id': customer_state_id,
                                     'country_id': customer_country_id,

                                     })
                            sender_id = exisitng_customer
                        if recever_name:
                            exisitng_customer = request.env['res.partner'].search(
                                [("name", "ilike", recever_name), ("phone", "=", recever_phone)])
                            if not exisitng_customer:
                                exisitng_customer = request.env['res.partner'].create(
                                    {"name": recever_name, "phone": recever_phone})
                            receiver_id = exisitng_customer
                            company_id = request.env["res.company"].search([("name", "ilike", "ON TIME COURIER")])
                            vals = {'sender_id': sender_id.id,
                                    'receiver_id': receiver_id.id,
                                    'weight': str(weight).split('.')[0],
                                    'price': str(amount).split('.')[0],
                                    'street': str(customer_address).split('.')[0],
                                    'paid': paid,
                                    "area_id": customer_area_rec.id,
                                    "zone_id": customer_area_rec.zone_id.id,
                                    "company_id": company_id.id,
                                    'cod': True if cod == "1" else False,
                                    'street2': "",
                                    "no_of_pieces": no_of_pieces,
                                    'name': sender_id.name,
                                    'zip': str(customer_zip).split('.')[0],
                                    'city': str(customer_city).split('.')[0],
                                    'state_id': customer_state_id,
                                    'country_id': customer_country_id,
                                    'courier_method': courier_method,
                                    'courier_type_id': courier_type_id,
                                    'service_type': str(service_type).split('.')[0],
                                    # 'date': datetime.strptime(str(courier_date_val),
                                    #                           tools.DEFAULT_SERVER_DATE_FORMAT)

                                    # 'date': datetime.strptime(courier_date_val, "%d/%M/%Y"),
                                    }
                            print(vals)
                            courier = request.env['courier.courier'].sudo().create(vals)
                            print (courier)
                            msg = "done"

                except Exception as E:
                    msg = E
                    return http.request.render('courier.booking_bulk_save', {"result": msg})
        return http.request.render('courier.booking_bulk_save', {"result": msg})

    @http.route(['/bulkimporst'], type='http', auth='user', website=True)
    def bulkimport(self, redirect=None, **post):
        if post:
            partner = request.env.user.partner_id
            Attachments = request.env['ir.attachment']
            name = post.get('attachment').filename
            file = post.get('attachment')
            attachment_id = Attachments.create({
                'name': name,
                'type': 'binary',
                'datas': base64.b64encode(file.read()),
                'res_model': partner._name,
                'res_id': partner.id
            })
            result = {}
            if attachment_id:
                try:
                    # fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
                    # fp.write(binascii.a2b_base64(base64.b64encode(file.read())))
                    # fp.seek(0)
                    file_data = attachment_id.datas.decode('base64')
                    workbook = xlrd.open_workbook(file_contents=file_data)
                    # workbook = xlrd.open_workbook(name)
                    sheet = workbook.sheet_by_index(0)
                    #                 no = 0
                    sheet.cell_value(0, 0)
                    msg = "Success"
                    for i in range(sheet.nrows):
                        if not i <= 0:
                            row = sheet.row_slice(i)
                            customer_name = row[0].value
                            customer_phone = row[1].value
                            customer_mobile = row[2].value
                            customer_address = row[3].value
                            customer_city = row[4].value
                            customer_zip = row[5].value
                            customer_state = row[6].value
                            customer_country = row[7].value
                            courier_method = row[8].value
                            courier_type = row[9].value
                            service_type = row[10].value
                            # courier_date_val = datetime(*xlrd.xldate_as_tuple(str(row[11].value), 0))
                            # print("-",datetime.strptime(str(row[11].value).encode('utf-8'), "%Y-%m-%d"))
                            courier_date_val = "2020-03-21"
                            recever_name = row[12].value
                            recever_phone = row[13].value
                            amount = row[14].value
                            weight = row[15].value
                            paid = row[16].value
                            cod = row[17].value

                            if courier_method == "Pickup & Delivery":
                                courier_method = "pickup_and_delivery"
                            else:
                                courier_method = "delivery"

                            existing_country = request.env['res.country'].sudo().search(
                                [("name", "ilike", customer_country)],
                                limit=1)
                            if existing_country:
                                customer_country_id = existing_country.id
                            else:
                                rec_country_id = request.env['res.country.state'].sudo().create(
                                    {"name": customer_state})
                                customer_country_id = rec_country_id.id
                            existing_state = request.env['res.country.state'].sudo().search(
                                [("name", "ilike", customer_state)],
                                limit=1)
                            if existing_state:
                                customer_state_id = existing_state.id
                            else:
                                rec_state_id = request.env['res.country.state'].sudo().create(
                                    {"name": customer_state, "code": customer_state, "country_id": customer_country_id})
                                customer_state_id = rec_state_id.id
                            existing_courier_type = request.env["courier.type"].sudo().search(
                                [("name", "ilike", courier_type)])
                            if existing_courier_type:
                                courier_type_id = existing_courier_type.id
                            else:
                                rec_courier_type = request.env['courier.type'].sudo().create(
                                    {"name": courier_type, "code": courier_type})
                                courier_type_id = rec_courier_type.id
                            if customer_name:
                                exisitng_customer = request.env['res.partner'].sudo().search(
                                    [("name", "ilike", customer_name), ("phone", "=", customer_phone)])
                                if not exisitng_customer:
                                    exisitng_customer = request.env['res.partner'].sudo().create(
                                        {"name": customer_name, "phone": customer_phone,
                                         "mobile": customer_mobile,
                                         'street': str(customer_address).split('.')[0],
                                         'zip': str(customer_zip).split('.')[0],
                                         'city': str(customer_city).split('.')[0],
                                         'state_id': customer_state_id,
                                         'country_id': customer_country_id,

                                         })
                                sender_id = exisitng_customer
                            if recever_name:
                                exisitng_customer = request.env['res.partner'].sudo().search(
                                    [("name", "ilike", recever_name), ("phone", "=", recever_phone)])
                                if not exisitng_customer:
                                    exisitng_customer = request.env['res.partner'].sudo().create(
                                        {"name": recever_name, "phone": recever_phone})
                                receiver_id = exisitng_customer
                                company_id = request.env["res.company"].sudo().search(
                                    [("name", "ilike", "ON TIME COURIER")])
                                vals = {'sender_id': sender_id.id,
                                        'receiver_id': receiver_id.id,
                                        'weight': str(weight).split('.')[0],
                                        'price': str(amount).split('.')[0],
                                        'street': str(customer_address).split('.')[0],
                                        'paid': paid,
                                        "company_id": company_id.id,
                                        'cod': cod,
                                        'street2': "",
                                        'name': sender_id.name,
                                        'zip': str(customer_zip).split('.')[0],
                                        'city': str(customer_city).split('.')[0],
                                        'state_id': customer_state_id,
                                        'country_id': customer_country_id,
                                        'courier_method': courier_method,
                                        'courier_type_id': courier_type_id,
                                        'service_type': str(service_type).split('.')[0],
                                        }
                                print(vals)
                                courier = request.env['courier.courier'].sudo().create(vals)
                                print(courier)
                except Exception as E:
                    msg = E
                    raise ValidationError(E)
        return http.request.render('courier.booking_bulk_save', msg)

    @http.route(['/page/booking_page/print'], type='http', auth="user", website=True)
    def print_challan(self, **kw):
        courier_id = kw.get('courier_id')
        name = "AirWay Bill_%s.pdf" % courier_id

        pdf = request.env['report'].sudo().get_pdf([int(courier_id)], 'courier.courier_challan')
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf)),
                          ('Content-Disposition', 'attachment; filename=%s;' % name)]
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route(['/create/partner'], type='json', auth="public", methods=['GET', 'POST'],
                website=True)
    def createpartner(self, **post):
        values = {}
        res_country = request.env['res.country']
        res_partner = request.env['res.partner']
        res_state = request.env['res.country.state']
        values['country_ids'] = res_country.search([])
        values['state_ids'] = res_state.search([])
        values['area_ids'] = request.env['area.area'].search([])
        if len(post) > 0:
            print(post)
            rec = res_partner.create(post)
            return rec.id
        return request.env['ir.ui.view'].render_template("courier.portal_detail_view", values)

    @http.route(['/create/location'], type='json', auth="public", methods=['GET', 'POST'],
                website=True)
    def create_location(self, **post):
        datas = {}
        print(post)
        values = {}
        res_country = request.env['res.country']
        res_location = request.env['courier.carrier.location']
        res_state = request.env['res.country.state']
        values['country_ids'] = res_country.search([])
        values['state_ids'] = res_state.search([])
        values['area_ids'] = request.env['area.area'].search([])
        if len(post) > 0:
            rec = res_location.create(post)
            return rec.id

        return request.env['ir.ui.view'].render_template("courier.address_detail_view", values)

    @http.route(['/create/add_area_view'], type='json', auth="public", methods=['GET', 'POST'],
                website=True)
    def add_area_view(self, **post):
        datas = {}
        print(post)
        values = {}
        res_state = request.env['res.country.state']
        values['zone_ids'] = request.env['zone.zone'].search([])
        if len(post) > 0:
            rec = request.env['area.area'].create(post)
            return rec.id

        return request.env['ir.ui.view'].render_template("courier.add_area_view", values)