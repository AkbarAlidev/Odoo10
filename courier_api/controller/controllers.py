# -*- coding: utf-8 -*-
import base64
import json
import logging
from datetime import datetime

from .utils import *
from odoo.http import request

from odoo import http, fields

_logger = logging.getLogger(__name__)


class CourierCourier(http.Controller):
    @http.route('/api/courier_dashboard/', auth='user', type='json')
    def courier_dashboard(self, **kw):
        _logger.info("Courier Dashboard")
        _logger.info(kw)
        dashboard_data = {}

        courier = request.env['courier.courier']
        cost_of_the_day = 0
        today = fields.Date.today()

        domain = [('pickup_driver_id.user_id', '=', request.env.user.id)]
        domain = []

        completed_trips = courier.search_count(domain)
        total_trips = courier.search_count(domain)
        pending_trips = courier.search_count(domain)
        cancelled_trips = courier.search_count(domain)

        domain += [('date', '=', today)]

        today_total_trips = courier.search_count(domain)
        today_completed_trips = courier.search_count(domain)
        today_pending_trips = courier.search_count(domain)
        today_cancelled_trips = courier.search_count(domain)

        final_price = courier.search([]).mapped('final_price')
        if final_price:
            cost_of_the_day = sum(final_price)

        dashboard_data['total_trips'] = total_trips
        dashboard_data['completed_trips'] = completed_trips
        dashboard_data['pending_trips'] = pending_trips
        dashboard_data['cancelled_trips'] = cancelled_trips

        dashboard_data['today_total_trips'] = today_total_trips
        dashboard_data['today_completed_trips'] = today_completed_trips
        dashboard_data['today_pending_trips'] = today_pending_trips
        dashboard_data['today_cancelled_trips'] = today_cancelled_trips

        dashboard_data['cost_of_the_day'] = cost_of_the_day

        _logger.info("Response : %s" % dashboard_data)

        return dashboard_data

    @http.route('/api/courier_ids/', auth='user', type='json')
    def courier_ids(self, **kw):
        _logger.info("Courier Ids")

        courier = request.env['courier.courier']

        search_ids = courier.search([]).ids

        _logger.info("Response : %s" % search_ids)
        # return json.dumps(search_ids)
        return search_ids

    @http.route('/api/session/logout', type='http', auth="none")
    def api_logout(self, **kw):
        user = request.env['res.users'].with_user(1).search(
            [('id', '=', int(kw.get('user_id')))])
        # clear user session
        user._clear_session()
        request.session.logout(keep_db=True)
        return "logout done"

    @http.route('/api/scan_bill_API', type='json', auth="user")
    def api_read_scan_bill_API(self, **kw):
        courier = request.env['courier.courier']
        search_ids = courier.search([("name", "=", (kw.get('name')))])
        if search_ids:
            rec = []
            type = "Delivery"
            if search_ids.courier_method == "pickup_and_delivery":
                type = "Pickup"
            to_location = ""
            i = search_ids
            if i.receiver_id:
                to_location = ""
                if i.receiver_id.street:
                    to_location = i.receiver_id.street + ","
                if i.receiver_id.street2:
                    to_location = to_location + i.receiver_id.street2 + ","
                if i.receiver_id.city:
                    to_location = to_location + i.receiver_id.city + ","
                if i.receiver_id.state_id:
                    to_location = to_location + i.receiver_id.state_id.name + ","
                if i.receiver_id.area_id:
                    to_location = to_location + i.receiver_id.area_id.name + ","
                if i.receiver_id.area_id:
                    to_location = to_location + i.receiver_id.area_id.name + ","
                if i.receiver_id.zip:
                    to_location = to_location + i.receiver_id.zip + ","
                if i.receiver_id.country_id:
                    to_location = to_location + i.receiver_id.country_id.name + ","
            rec.append({
                'courier_id': search_ids.id,
                'sender_name': search_ids.sender_id.name if search_ids.sender_id else "",
                'receiver_name': search_ids.receiver_id.name if search_ids.receiver_id else "",
                'status': search_ids.state,
                "Booking No": search_ids.name,
                "Booking Date": search_ids.date,
                "Sender Name": search_ids.sender_id.name if search_ids.sender_id else "",
                "Mobile Number": search_ids.sender_phone if search_ids.sender_phone else search_ids.sender_id.phone,
                "Mobile Number (2)": search_ids.sender_mobile if search_ids.sender_phone else search_ids.sender_id.mobile,
                "Location": to_location,
                "Awb": search_ids.name,
                "Quandity": search_ids.no_of_pieces,
                "cod": "Yes" if search_ids.cod else "No",
                "type": type

            })
            return rec
        else:
            return {"msg": "no record found with name" + (kw.get('name'))}

    @http.route('/api/booking_fromapp', type='json', auth="user")
    def booking_fromapp(self, **kw):
        print(" * * *  *rr  * ** ** *  * *")
        print(kw)
        pick_location_id = False
        vals = []
        vv = []
        courier = request.env['courier.courier']
        #         search_read = courier.search_read([])
        if kw:
            if kw.get("sender_details"):
                sender_details = kw.get("sender_details")
            sender_rec = request.env["res.partner"].search(
                ['|', ("name", "=", sender_details.get("sender_name")),
                 (
                     "phone", "=", sender_details.get("sender_ph"))], limit=1)

            if not sender_rec:
                s_val = {"name": sender_details.get("sender_name"),
                         "city": sender_details.get("sender_city"),
                         "area_id": sender_details.get("sender_area"),
                         "zone_id": sender_details.get("sender_zone") if sender_details.get("sender_zone") else False,
                         "street": sender_details.get("sender_street"),
                         "street2": sender_details.get("sender_street2"),
                         "phone": sender_details.get("sender_ph"),
                         "state_id": sender_details.get("sender_state"),
                         "country_id": sender_details.get("sender_country")
                         }
                sender_rec = request.env["res.partner"].create(s_val)

            if kw.get("receiver_location"):
                receiver_details = kw.get("receiver_location")
                receiver_rec = request.env["res.partner"].search(
                    [("name", "=", receiver_details.get("receiver_name")),
                     ("phone", "=", receiver_details.get("receiver_ph"))], limit=1)

                if not receiver_rec:
                    r_val = {"name": receiver_details.get("receiver_name"),
                             "city": receiver_details.get("receiver_city"),
                             "area_id": receiver_details.get("receiver_area"),
                             "zone_id": receiver_details.get("receiver_zone"),
                             "street": receiver_details.get("receiver_street"),
                             "street2": receiver_details.get("receiver_street2"),
                             "phone": receiver_details.get("receiver_ph"),
                             "state_id": receiver_details.get("receiver_state"),
                             "country_id": receiver_details.get("receiver_country")
                             }
                    if r_val:
                        receiver_rec = request.env["res.partner"].create(r_val)

            if kw.get("pickup_location"):
                pickup_location_details = kw.get("pickup_location")

                pick_location_id = request.env["courier.carrier.location"].search(
                    [("city", "=", pickup_location_details.get("pickup_city")),
                     ("partner_id", "=", sender_rec.id),
                     ("area_id", "=", pickup_location_details.get("pickup_area")),
                     ("street", "=", pickup_location_details.get("pickup_street")),
                     ("street2", "=", pickup_location_details.get("pickup_street2")),
                     ("street2", "=", pickup_location_details.get("pickup_street2")),
                     ])
                if not pick_location_id:
                    vals = {
                        "city": pickup_location_details.get("pickup_city"),
                        "area_id": pickup_location_details.get("pickup_area"),
                        "street": pickup_location_details.get("pickup_street"),
                        "street2": pickup_location_details.get("pickup_street2"),
                        "street2": pickup_location_details.get("pickup_street2"),
                        "street2": pickup_location_details.get("pickup_street2"),
                        "state_id": pickup_location_details.get("pickup_state"),
                        "country_id": pickup_location_details.get("pickup_country"),
                        "zone_id": pickup_location_details.get("pickup_zone"),
                        "partner_id": sender_rec.id
                    }
                    pick_location_id = request.env["courier.carrier.location"].create(vals)

            if kw.get("package_details"):
                courier_details = kw.get("package_details")
                weight = float(courier_details.get("weight"))
                uom_categ = courier_details.get("uom_categ")
                date = courier_details.get("date")
                price = float(courier_details.get("price"))
                name = courier_details.get("name")
                courier_type_id = courier_details.get("courier_type_id")
                pickup_date_time = courier_details.get("courier_type_id")
                product_description = courier_details.get("package_description")
                service_type = courier_details.get("service_type")
                booking_date = courier_details.get("booking_date")
                date_of_pickup = courier_details.get('pickup_date') or ''
                time_of_pickup = courier_details.get('pickup_time') or ''
                pickup = False
                if date_of_pickup and time_of_pickup:
                    pickup = str(date_of_pickup) + str(" " + time_of_pickup)

            courier_zone_id = receiver_rec.zone_id.id
            if receiver_rec.zone_id:
                courier_zone_id = receiver_rec.zone_id.id
            elif receiver_rec.area_id.zone_id:
                courier_zone_id = receiver_rec.area_id.zone_id.id
            if pick_location_id and not pickup:
                courier_zone_id = pick_location_id.zone_id.id
            vals = {
                "sender_id": sender_rec.id,
                "receiver_id": receiver_rec.id,
                "sender_phone": sender_rec.phone,
                "sender_location_id": pick_location_id.id if pick_location_id else False,
                "receiver_phone": receiver_rec.phone,
                "weight": weight,
                "uom_categ": uom_categ,
                "date": booking_date,
                "price": price,
                "name": name,
                "service_type": service_type,
                "pickup_date": pickup_date_time,
                "courier_type_id": courier_type_id,
                "product_description": product_description,
                "pickup_date_time": pickup,
                "courier_zone_id": courier_zone_id
            }
            print('f', vals)
            if request.env.user:
                w_id = request.env["stock.warehouse"].search([("company_id", "=", request.env.user.company_id.id)],
                                                             limit=1)
                vals["company_id"] = request.env.user.company_id.id
                vals["main_warehouse_id"] = w_id.id

        try:
            courier = request.env['courier.courier'].create(vals)
            courier.sudo().load_address()
            return {"msg": "success", "record_id": courier.id}
        except Exception as e:
            return {"msg": e, "record_id": False}

    @http.route('/api/courier_booking_from_app/', auth='user', type='json')
    def dfg(self, **kw):
        print(" * * *  *rr  * ** ** *  * *")
        print(kw)
        courier = request.env['courier.courier']
        #         search_read = courier.search_read([])
        if kw:
            if kw.get("sender_details"):
                sender_details = kw.get("sender_details")
            sender_rec = request.env["res.partner"].search(
                ['|', ("name", "=", sender_details.get("sender_name")),
                 (
                     "phone", "=", sender_details.get("sender_ph"))])

        if not sender_rec:
            s_val = {"name": sender_details.get("sender_name"),
                     "city": sender_details.get("sender_city"),
                     "area_id": sender_details.get("sender_area"),
                     "zone_id": sender_details.get("sender_zone") if sender_details.get("sender_zone") else False,
                     "street": sender_details.get("sender_street"),
                     "street2": sender_details.get("sender_street2"),
                     "phone": sender_details.get("sender_ph"),
                     "state_id": sender_details.get("sender_state"),
                     "country_id": sender_details.get("sender_country")
                     }
            sender_rec = request.env["res.partner"].create(s_val)

        if kw.get("receiver_location"):
            receiver_details = kw.get("receiver_location")
            receiver_rec = request.env["res.partner"].search(
                [("name", "=", receiver_details.get("receiver_name")),
                 ("phone", "=", receiver_details.get("receiver_ph"))])

            if not receiver_rec:
                r_val = {"name": receiver_details.get("receiver_name"),
                         "city": receiver_details.get("receiver_city"),
                         "area_id": receiver_details.get("receiver_area"),
                         "zone_id": receiver_details.get("receiver_zone"),
                         "street": receiver_details.get("receiver_street"),
                         "street2": receiver_details.get("receiver_street2"),
                         "phone": receiver_details.get("receiver_ph"),
                         "state_id": receiver_details.get("receiver_state"),
                         "country_id": receiver_details.get("receiver_country")
                         }
                receiver_rec = request.env["res.partner"].create(r_val)

        if kw.get("pickup_location"):
            pickup_location_details = kw.get("pickup_location")
        #         pick_location_id = request.env[""].search(
        #             [("city", "=", pickup_location_details.get("pickup_city"))])

        if kw.get("package_details"):
            courier_details = kw.get("package_details")
        weight = float(courier_details.get("weight"))
        uom_categ = courier_details.get("uom_categ")
        date = courier_details.get("date")
        price = float(courier_details.get("price"))
        name = courier_details.get("name")
        courier_type_id = courier_details.get("courier_type_id")
        pickup_date_time = courier_details.get("courier_type_id")
        product_description = courier_details.get("package_description")
        service_type = courier_details.get("service_type")

        vals = {
            "sender_id": sender_rec.id,
            "receiver_id": receiver_rec.id,
            "sender_phone": sender_rec.phone,
            "receiver_phone": receiver_rec.phone,
            "weight": weight,
            "uom_categ": uom_categ,
            "date": date,
            "price": price,
            "name": name,
            "service_type": service_type,
            "pickup_date": pickup_date_time,
            "courier_type_id": courier_type_id,
            "product_description": product_description
        }
        courier = request.env['courier.courier'].create(vals)
        courier_id = request.env['courier.courier'].search_read([("id", "=", courier.id)])
        return courier_id

    def get_details(self, type, user_id):
        courier = request.env['courier.courier']
        rec = []
        if type == "pickup":
            records = courier.search([("pickup_driver_id", "=", int(user_id)),
                                      ("assign_to", "=", int(user_id))])
        else:
            records = courier.search([("delivery_driver_id", "=", int(user_id)),
                                      ("assign_to", "=", int(user_id))])

        if records:
            for i in records:
                type = "delivery"
                from_location = ""
                if i.sender_id:
                    type = "pickup_and_delivery"
                    if i.sender_location_id:
                        from_location = i.sender_location_id.street
                        ","
                        if i.sender_location_id.street2:
                            from_location = from_location + i.sender_location_id.street2 + ","
                        if i.sender_location_id.city:
                            from_location = from_location + i.sender_location_id.city + ","
                        if i.sender_location_id.state_id:
                            from_location = from_location + i.sender_location_id.state_id.name + ","
                        if i.sender_location_id.area_id:
                            from_location = from_location + i.sender_location_id.area_id.name + ","
                        if i.sender_location_id.area_id:
                            from_location = from_location + i.sender_location_id.area_id.name + ","
                        if i.sender_location_id.zip:
                            from_location = from_location + i.sender_location_id.zip + ","
                        if i.sender_location_id.country_id:
                            from_location = from_location + i.sender_location_id.country_id.name + ","
                    else:
                        from_location = i.sender_id.street + ","
                        if i.sender_id.street2:
                            from_location = from_location + i.sender_id.street2 + ","
                        if i.sender_id.city:
                            from_location = from_location + i.sender_id.city + ","
                        if i.sender_id.state_id:
                            from_location = from_location + i.sender_id.state_id.name + ","
                        if i.sender_id.area_id:
                            from_location = from_location + i.sender_id.area_id.name + ","
                        if i.sender_id.area_id:
                            from_location = from_location + i.sender_id.area_id.name + ","
                        if i.sender_id.zip:
                            from_location = from_location + i.sender_id.zip + ","
                        if i.sender_id.country_id:
                            from_location = from_location + i.sender_id.country_id.name + ","

                if i.receiver_id:
                    to_location = ""
                    if i.receiver_id.street:
                        to_location = i.receiver_id.street + ","
                    if i.receiver_id.street2:
                        to_location = to_location + i.receiver_id.street2 + ","
                    if i.receiver_id.city:
                        to_location = to_location + i.receiver_id.city + ","
                    if i.receiver_id.state_id:
                        to_location = to_location + i.receiver_id.state_id.name + ","
                    if i.receiver_id.area_id:
                        to_location = to_location + i.receiver_id.area_id.name + ","
                    if i.receiver_id.area_id:
                        to_location = to_location + i.receiver_id.area_id.name + ","
                    if i.receiver_id.zip:
                        to_location = to_location + i.receiver_id.zip + ","
                    if i.receiver_id.country_id:
                        to_location = to_location + i.receiver_id.country_id.name + ","

                rec.append({"booking_number": i.name,
                            'courier_id': i.id,
                            'customer_name': i.sender_id.name,
                            'from_location': from_location,
                            'delivery_location': to_location,
                            'status': i.state,
                            'type': type
                            })
        return rec

    @http.route('/api/courier_histroy/', auth='user', type='json')
    def courier_histroy(self, **kw):
        _logger.info("Courier Ids")
        values = {}
        values["pickup_records"] = self.get_details("pickup", kw.get('user_id'))
        values["delivery_records"] = self.get_details("delivery", kw.get('user_id'))

        return values

    @http.route('/api/update_delivery/', csrf=False, auth='user', type='http')
    def update_delivery(self, **kw):
        _logger.info("Updated Ids")
        if kw:
            courier = request.env['courier.courier']
            search_ids = courier.search([("id", "=", int(kw.get('courier_id')))])
            if search_ids:
                search_ids.sudo().write({"deliver_image_ids": base64.encodestring(kw.get('delivery_image').read()),
                                         "receiver_signature_ids": base64.encodestring(kw.get('sign').read()),
                                         "courier_delivery_date": kw.get('courier_delivery_date')})

                _logger.info("Response : %s" % search_ids)
                return "Record updated"
            else:
                return "No found record"

    @http.route('/api/courier_list/', auth='user', type='json')
    def courier_list(self, **kw):
        _logger.info("Courier List")

        courier = request.env['courier.courier']
        search_read = courier.search_read([])

        _logger.info("Response : %s" % search_read)

        # return json.dumps(search_read)
        return search_read

    @http.route('/api/courier_status/', auth='user', type='json')
    def courier_status(self, **kw):
        _logger.info("Courier Status")

        courier = request.env['courier.courier']

        fields = ['number', 'track_ref', 'final_price', 'price', 'state', 'latitude', 'longitude']
        fields = []
        courier_id = kw.get('courier_id')
        courier_read = courier.search_read([('id', '=', courier_id)], fields=fields)

        _logger.info("Response : %s" % courier_read)

        # return json.dumps(courier_read)
        return courier_read

    @http.route('/api/courier_update/', auth='user', type='json')
    def courier_update(self, **kw):
        _logger.info("Courier Search")
        _logger.info(kw)

        courier = request.env['courier.courier']
        courier_id = kw.get('courier_id')
        domain = [('id', '=', courier_id)]

        courier_id = courier.search(domain)

        if 'courier_status' in kw and kw.get('courier_status'):
            state = kw.get('courier_status')
        elif 'state' in kw and kw.get('state'):
            state = kw.get('state')

        if state:
            courier_id.write({'state': state})
            status = "updated"
        else:
            status = "Not Update"

        values = {
            'courier_id': courier_id.id,
            'status': status,
        }

        _logger.info("Response : %s" % values)
        return values

    @http.route('/api/get_pickup_list', auth='user', type='json')
    def get_pickup_list(self, **kw):
        _logger.info("Get Picking List")
        _logger.info(kw)
        login_user_id = request.env.user.id
        emp_id = request.env['hr.employee'].search([("user_id", "=", login_user_id)])
        fields = ['number', 'track_ref', 'final_price', 'price', 'state', 'latitude', 'longitude']
        fields = []
        # courier_read = request.env['courier.courier'].search_read([("assign_to", "=", int(emp_id.id))], fields=fields)
        courier_read = request.env['courier.courier'].search_read([("state", "=", "ready_to_pickup")], fields=fields)
        return courier_read

    @http.route('/api/update_pickingdetails/', auth='user', type='json')
    def update_pickingdetails(self, **kw):
        _logger.info("Update Picking")
        _logger.info(kw)
        if kw:
            courier_id = kw.get("courier_id")
            courier = request.env['courier.courier'].search([("id", "=", int(courier_id))])
            if courier:
                date_of_pickup = kw.get('pickup_datetime') or ''
                # time_of_pickup = kw.get('pickup_time') or ''
                pickup = str(date_of_pickup)
                courier.sudo().write({"pickup_date_time": pickup})
                return "Updated"
            else:
                return "Record not found"

    @http.route('/api/get_default_data/', auth='user', type='json')
    def courier_default_value(self, **kw):
        """ Method to read the API """
        values = {}
        service_type = []
        booking_level = []
        courier_method = []
        courier_type = request.env['courier.type']
        service_type.append({"type": "Same Day Delivery Service(Bullet Service)"})
        service_type.append({"type": "Next Day Delivery Service"})
        service_type.append({"type": "Return Service(RTS)"})
        service_type.append({"type": "COD E-commerce Shipments"})
        service_type.append({"type": "International OutBond Express"})

        values["service_type"] = service_type
        booking_level.append({"type": "DOMESTIC DELIVERY"})
        booking_level.append({"type": "INTERNATIONAL DELIVERY"})
        values["booking_level"] = booking_level
        courier_method.append({"type": "Pickup & Delivery"})
        courier_method.append({"type": "Delivery"})
        values["courier_method"] = courier_method

        res_partner = request.env['res.partner']
        res_country = request.env['res.country']
        res_state = request.env['res.country.state']
        location_list = request.env['courier.carrier.location']
        location_list = request.env['courier.carrier.location']
        uom_categ =[]
        uom_categ.append({"type":"atomic mass unit (amu)"})
        uom_categ.append({"type":"carat (metric)"})
        uom_categ.append({"type":"cental"})
        uom_categ.append({"type":"centigram"})
        uom_categ.append({"type":"dekagram"})
        uom_categ.append({"type":"dram (dr)"})
        uom_categ.append({"type":"grain (gr)"})
        uom_categ.append({"type": "gram (g)"})
        uom_categ.append({"type":"hundredweight (UK)"})
        uom_categ.append({"type":"kilogram (kg)"})
        uom_categ.append({"type":"microgram (µg)"})
        uom_categ.append({"type": "milligram (mg)"})
        uom_categ.append({"type":"newton (Earth)"})
        uom_categ.append({"type":"ounce (oz)"})
        uom_categ.append({"type":"pennyweight (dwt)"})
        uom_categ.append({"type":"pound (lb)"})
        uom_categ.append({"type":"quarter"})
        uom_categ.append({"type":"stone"})
        uom_categ.append({"type":"ton (UK, long)"})
        uom_categ.append({"type":"ton (US, short)"})
        uom_categ.append({"type":"tonne (t)"})
        uom_categ.append({"type":"troy ounce"})
        values['uom_categ'] = uom_categ
        courier_types = []
        for i in courier_type.sudo().search([]):
            courier_types.append({"id": i.id,
                                  "name": i.name})
        values['courier_types'] = courier_types
        sender_details = []
        for i in res_partner.sudo().search([]):
            sender_details.append({"id": i.id,
                                   "name": i.name,
                                   "city": i.city,
                                   "zip": i.zip,
                                   "street": i.street,
                                   "street2": i.street2,
                                   "state_id": {"id": i.state_id.id, "name": i.state_id.name},
                                   "area_id": {"id": i.area_id.id if i.area_id else "",
                                               "name": i.area_id.name if i.area_id else ""},
                                   "country_id": {"id": i.country_id.id if i.country_id else "",
                                                  "name": i.country_id.name if i.country_id else ""}

                                   })

        values['sender_ids'] = sender_details
        country_list = []
        for i in res_state.sudo().search([]):
            country_list.append({"id": i.id,
                                 "name": i.name,
                                 })
        values['country_ids'] = country_list

        state_ids_list = []
        for i in res_state.sudo().search([]):
            state_ids_list.append({"id": i.id,
                                   "name": i.name,
                                   })
        values['state_ids'] = state_ids_list

        location_list = []
        for i in request.env['courier.carrier.location'].sudo().search([]):
            location_list.append({"id": i.id,
                                  "name": i.name,
                                  "city": i.city,
                                  "partner_id": i.partner_id.id,
                                  "street": i.street,
                                  "street2": i.street2,
                                  "zip": i.zip,
                                  "area": {"id": i.area_id.id if i.area_id else "",
                                           "name": i.area_id.name if i.area_id else ""},
                                  "country": {"id": i.country_id.id if i.country_id else "",
                                              "name": i.country_id.name if i.country_id else ""},
                                  "state_id": {"id": i.state_id.id if i.state_id else "",
                                               "name": i.state_id.name if i.state_id else ""}
                                  })
        values['location_list'] = location_list
        area_list = []
        for i in request.env['area.area'].sudo().search([]):
            area_list.append({"id": i.id,
                              "name": i.name,
                              "zone_id": {"id": i.zone_id.id if i.zone_id else "",
                                          "name": i.zone_id.name if i.zone_id else "",
                                          "price":i.zone_id.price if i.zone_id else "",
                                          }
                              })
        values['area_ids'] = area_list

        payment_method =[]
        payment_method.append({"type": "Cash on Delivery"})
        payment_method.append({"type": "Credit Card"})
        values['payment_method'] = payment_method

        # service_type = []
        # service_type.append({"same_day_delivery_service": "Same Day Delivery Service(Bullet Service)",
        #                      "return_service": "Next Day Delivery Service",
        #                      "return_service": "Return Service(RTS)",
        #                      "cod_ecommerce_shipments": "COD E-commerce Shipments",
        #                      "internal_outbond_express": "International OutBond Express", })
        # values["service_type"] = service_type
        # courier_method = []
        # courier_method.append({"pickup_and_delivery": "Pickup & Delivery",
        #                        "delivery": "Delivery"})
        # values["courier_method"] = courier_method

        return values

    @http.route('/api/courier_search/', auth='user', type='json')
    def courier_search(self, **kw):
        _logger.info("Courier Search")
        _logger.info(kw)

        courier = request.env['courier.courier']
        domain = []

        if 'from_date' in kw and kw.get('from_date') and 'to_date' in kw and kw.get('to_date'):
            from_date = kw.get('from_date')
            to_date = kw.get('to_date')
            domain += [('date', '>=', from_date), ('date', '<=', to_date)]

        if 'state' in kw and kw.get('state'):
            state = kw.get('state')
            domain += [('state', '=', state)]

        if 'courier_id' in kw and kw.get('courier_id'):
            courier_id = kw.get('courier_id')
            domain += [('id', '=', courier_id)]

        _logger.info(domain)

        courier_result = courier.search_read(domain, order='date desc')
        courier_count = courier.search_count(domain)

        values = {
            'search_result': courier_result,
            'count': courier_count,
        }

        _logger.info("Response : %s" % values)
        return values
