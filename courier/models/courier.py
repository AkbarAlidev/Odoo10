# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.


import base64
import logging
import os
import datetime

_logger = logging.getLogger(__name__)
import pathlib
import werkzeug
import xlrd
from datetime import datetime

from odoo.exceptions import UserError, Warning
from odoo.tools.safe_eval import safe_eval

from odoo import api, fields, models, _


def urlplus(url, params):
    return werkzeug.Href(url)(params or None)


states = [('draft', 'Draft'),
          ('invoiced', 'Invoiced'),
          ('packing', 'Packing'),
          ('ready_to_pickup', 'Ready to Pickup'),
          ('picked', 'Ready for Packing'),
          ('pickedup', 'Picked Up'),
          ('customs_inspection', 'Customs Inspection'),
          ('dnata_facility', 'Dnata facility'),
          ('inprogress', 'In Progress'),

          ('inscan', 'In Scan'),
          ('outscan', 'Out Scan'),
          ('departed_facility_in_dubai', 'Departed facility in Dubai'),
          ('on_transit', 'On Transit'),
          ('ready_for_dispatched', 'Ready for Dispatch'),
          ('clearance_processed', 'Clearance Processed'),
          ('dispatched', 'Dispatched'),
          ('out_for_delivery', 'Out for delivery'),
          ('delivered', 'Delivered'),
          ('return', 'Return'),
          ('lost', 'Lost'),
          ('damaged', 'Damaged'),
          ('claim', 'Claim'),
          ('refunded', 'Refunded'),
          ('cancel', 'Cancel')]


# ---------------------res.partner---------------------#
class ResPartner(models.Model):
    _inherit = "res.partner"

    courier_sent_ids = fields.One2many('courier.courier', 'sender_id', 'Sender', help='The name of the Sender.')
    courier_receive_ids = fields.One2many('courier.courier', 'receiver_id', 'Receiver',
                                          help='The name of the Receiver.')
    courier_discount_percentage = fields.Float(string='Courier discount percentage (%)', default='0.0')
    customer_type = fields.Selection([('vip', 'VIP'), ('normal', 'Normal')],
                                     string="Customer type", required=True, default='normal')
    sender_location_ids = fields.One2many("courier.carrier.location", "partner_id")


# ---------------------courier.carrier.location---------------------#
class CourierCarrierLocation(models.Model):
    _name = "courier.carrier.location"
    _description = "class for managing locations"
    _rec_name = 'street'

    name = fields.Char('Name', size=64, help='The name of the courier.')
    street = fields.Char(help='The name of the street.')
    street2 = fields.Char(help='The name of the street2.')
    zip = fields.Char(change_default=True, help='The name of the zip code.')
    city = fields.Char(help='The name of the city.')
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', help='The name of the state.')
    zone_id = fields.Many2one('zone.zone', string="Zone", help='The zone where the state is located.')
    area_id = fields.Many2one('area.area', string="Area", help='The Area')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', help='The name of the country.')
    partner_id = fields.Many2one('res.partner', string='Partner')

    @api.onchange("area_id")
    def change_area_id(self):
        if self.area_id:
            print(self.area_id.zone_id)
            self.zone_id = self.area_id.zone_id.id


# ---------------------courier.carrier---------------------#
class CourierCarrier(models.Model):
    _name = "courier.carrier"
    _description = "class manages the carriers"

    name = fields.Char('Name', size=64, help='The name of the carrier.')
    from_location_id = fields.Many2one('courier.carrier.location', 'Source location',
                                       help='The name of the from location.')
    to_location_id = fields.Many2one('courier.carrier.location', 'Destination Location',
                                     help='The name of the to location.')
    distance = fields.Char("Distance", help='Distance between source and destination locations')
    medium = fields.Selection([('ByAir', 'By Air'),
                               ('BySea', 'By Sea'),
                               ('ByBus', 'By Bus'),
                               ('ByTrain', 'By Train'),
                               ('Other', 'Other')],
                              'Transport Medium', help='Medium used to shipment for courier')
    product_id = fields.Many2one('product.product', 'Product', help='The name of the product.')
    days = fields.Char('Days', help='It is display number of day')
    price = fields.Float('Price', help='It is display price')
    provider_ids = fields.Many2many('res.partner', 'res_partner_provider_rel', 'partner_id', 'provider_id',
                                    'List of Suppliers')


# ---------------------courier.routing---------------------#
class CourierRouting(models.Model):
    _name = "courier.routing"
    _description = "class manages routing of courier"

    name = fields.Char('Name', size=32, help='The name of routing.')
    from_location_id = fields.Many2one('courier.carrier.location', 'From location', help='Source location.')
    to_location_id = fields.Many2one('courier.carrier.location', 'To Location', help='Destination location.')
    days = fields.Char(string="Days", help='Approximate number of days for delivery')
    price = fields.Float(string="Price", help='It is display the price of courier.')
    distance = fields.Char(string="Distance", help='It is display the distance \
        of source location to destination location.')
    path_ids = fields.One2many('courier.routing.path', 'routing_id', 'Path id', help='It is display the routes.')


# ---------------------courier_routing_path---------------------#
class CourierRoutingPath(models.Model):
    _name = "courier.routing.path"
    _description = "class which manages paths of routing"

    name = fields.Char('Name')
    routing_id = fields.Many2one('courier.routing', 'Routing')
    carrier_id = fields.Many2one('courier.carrier', 'Carrier')
    from_location_id = fields.Many2one('courier.carrier.location', 'Source', help='The name of the Source.')
    to_location_id = fields.Many2one('courier.carrier.location', 'Destination', help='The name of the Destination.')
    days = fields.Char(string="Duration", help='It is display duration.')
    price = fields.Float(string="Price", help='It is display the price of courier.')
    distance = fields.Char(string="Distance", help='It is display the distance of from location and to location.')
    zone_id = fields.Many2one('zone.zone', "Zone", help='The name of the Zone.')
    employee_ids = fields.One2many('hr.employee', 'routing_id', string='Employees')

    #    provider_id = fields.Many2many(related='carrier_id.provider_ids', string="Provider")

    @api.onchange('carrier_id')
    def onchange_carrier_id(self):
        if self.carrier_id:
            self.from_location_id = self.carrier_id.from_location_id.id
            self.to_location_id = self.carrier_id.to_location_id.id
            self.price = self.carrier_id.price
            self.distance = self.carrier_id.distance
            self.days = self.carrier_id.days
            # self.provider_id = [x.id for x in self.carrier_id.provider_ids]


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    def get_price_from_picking(self, total, weight, volume, quantity):
        price = 0.0
        criteria_found = False
        price_dict = {'price': total, 'volume': volume,
                      'weight': weight, 'wv': volume * weight,
                      'quantity': quantity}
        for line in self.price_rule_ids:
            test = safe_eval(line.variable + line.operator + str(line.max_value), price_dict)
            if test:
                price = line.list_base_price + line.list_price * float(price_dict[line.variable_factor])
                criteria_found = True
                break
        if not criteria_found:
            raise UserError(_("Selected product in the delivery method doesn't \
                fulfill any of the delivery carrier(s) criteria."))
        return price


# ---------------------courier.terms--------------------- #
class CourierTerms(models.Model):
    _name = "courier.terms"
    _description = "Courier Terms Information"

    name = fields.Char('Term', size=64, help='The name of the term.')
    code = fields.Char('Code', size=64, help='It is display unique code')
    description = fields.Text('Description', help='It is display terms & conditions')


# ---------------------courier.type--------------------- #
class CourierType(models.Model):
    _name = "courier.type"
    _description = "Courier Types Information"

    name = fields.Char('Name', size=64, help='The name of the courier type.')
    code = fields.Char('Code', size=64, help='It is display unique code')


# ---------------------courier.courier--------------------- #
class CourierCourier(models.Model):
    _name = "courier.courier"
    _description = "General Courier Information"
    _rec_name = "number"

    @api.model
    def download_file_format(self):
        """ Donwload the template file for import"""
        doc_id = self.env['ir.attachment'].search([("datas_fname", "=", "BulkImportTemplateFile.csv")], limit=1)
        if not doc_id:
            path = os.path.dirname(os.path.realpath(__file__))
            parent_file_path = os.path.abspath(os.path.join(path, os.pardir))
            # create a directory under static folder
            xml_directory = parent_file_path + '/static/src/template/'
            xls_file_filepath = xml_directory + "import_courier.csv"
            # self.contract_template = base64.b64encode(open(xls_file_filepath, "rb").read())
            data = base64.b64encode(open(xls_file_filepath, "rb").read())
            attach_vals = {
                'name': '%s.csv' % ('BulkImportFile'),
                'datas': data,
                'datas_fname': '%s.csv' % ('BulkImportTemplateFile'),
            }
            doc_id = self.env['ir.attachment'].create(attach_vals)
        print(doc_id)
        download_url = '/web/content/' + str(doc_id.id) + '?download=true'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        # download
        file_url = "/?model=" + doc_id._name + "&id=" + str(doc_id.id) + "&filename=" + doc_id.name
        params = {}
        return str(base_url) + str(download_url),
        # return urlplus(file_url, params)

    @api.multi
    @api.depends('invoice_id.residual')
    def get_invoice_total(self):
        for rec in self:
            if rec.invoice_id:
                if rec.invoice_id.state == 'draft':
                    rec.invoice_total = rec.invoice_id.amount_total
                else:
                    rec.invoice_total = rec.invoice_id.residual

    @api.multi
    @api.depends('refund_invoice_id.residual')
    def get_refund_invoice_total(self):
        for rec in self:
            if rec.refund_invoice_id:
                if rec.refund_invoice_id.state == 'draft':
                    rec.invoice_total = rec.refund_invoice_id.amount_total
                else:
                    rec.invoice_total = rec.refund_invoice_id.residual



    number = fields.Char('Number', copy=False, help='It is display unique number')
    name = fields.Char('Name', help='Courier Name')
    receiver_id = fields.Many2one('res.partner', 'Recipient', help='Responsible to receive courier')
    sender_id = fields.Many2one('res.partner', 'Sender', help='Responsible to sends courier')
    sender_location_id = fields.Many2one('courier.carrier.location')
    assign_to = fields.Many2one('hr.employee', domain=[('is_driver', '=', True)], string='Assigned To',
                                help='The name of the assigned Employee.')
    pickup_driver_id = fields.Many2one('hr.employee', 'Assigned To', help='The name of the assigned Employee.')
    delivery_driver_id = fields.Many2one('hr.employee', 'Assigned To', help='The name of the assigned Employee.')
    routing_id = fields.Many2one('courier.routing.path', 'Routing',
                                 help="Way taken in getting from sender's to recipient's address")
    invoice_id = fields.Many2one('account.invoice', 'Invoice', copy=False, help='reference of Invoice')
    invoice_count = fields.Integer(string='# of Invoices', compute='_get_invoice_count', readonly=True)
    deliver_date = fields.Datetime('Estimated Delivery Date',
                                   help='Estimation of  when a shipment will arrive at its destination.')
    courier_delivery_date = fields.Datetime('Delivered Date',
                                            help='Actual Delivered Date')
    price = fields.Float('Delivery Rate', help="Rates(excluded from delivery charges)")
    courier_method = fields.Selection([("pickup_and_delivery", "Pickup & Delivery"), ("delivery", "Delivery")],
                                      default="delivery")
    pickup_date_time = fields.Datetime(string="Pick Up Datetime")
    service_type = fields.Selection([("door_to_door", "Door to door"),
                                     ("clearance_by_consignee", "Clearance by consignee/IKA Airport")])
    delivery_location_ids = fields.Many2one("courier.carrier.location", "partner_id")

    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', change_default=True)
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State')
    zone_id = fields.Many2one('zone.zone', string="Zone", help='The zone where the state is located.')
    area_id = fields.Many2one('area.area', string="Area", help='The Area')

    country_id = fields.Many2one('res.country', string='Country')

    latitude = fields.Float('Geo Latitude', digits=(16, 5))
    longitude = fields.Float('Geo Longitude', digits=(16, 5))

    distance = fields.Char(related='routing_id.distance', string='Distance', help='Distance')
    terms_id = fields.Many2one('courier.terms', 'Terms', help='Specific terms for a courier itself')
    history_ids = fields.One2many('courier.history', 'courier_id', '', readonly=True)
    note = fields.Text('Note', help='It is display note')
    state = fields.Selection(states,'State', default="draft", help="States of courier")
    date = fields.Datetime('Date', default=datetime.today(), help="Courier date")
    track_ref = fields.Char('Tracking Reference', help="Tracking reference for courier")

    form_tax_id = fields.Many2many("account.tax", string="TAX")
    # weight = fields.Float('Actual Weight', help="weight of courier")
    # dimensional_weight = fields.Float('Dimensional Weight', help="calculated weight", compute='_compute_all_amount', store=True)
    demo_id = fields.One2many("package.tree", "custom_id")

    @api.onchange('coast', 'total_weight','discount_price', 'price')
    def _compute_final_pricenew(self):
        self.total_price = (self.total_weight * self.coast) + self.price

    coast = fields.Float("Cost / Kg", default=1)
    uom_categ = fields.Char('UOM', help="Uom")
    uom_categ = fields.Selection([("atomic mass unit (amu)","atomic mass unit (amu)"),
                                               ("carat (metric)","carat (metric)"),
                                                ("cental","cental"),
                                                ("centigram","centigram"),
                                                ("dekagram","dekagram"),
                                                ("dram (dr)","dram (dr)"),
                                                ("grain (gr)","grain (gr)"),
                                                ("gram (g)","gram (g)"),
                                                ("hundredweight (UK)","hundredweight (UK)"),
                                                ("kilogram (kg)","kilogram (kg)"),
                                                ("microgram (µg)","microgram (µg)"),
                                                ("milligram (mg)","milligram (mg)"),
                                                ("newton (Earth)","newton (Earth)"),
                                                ("ounce (oz)","ounce (oz)"),
                                                ("pennyweight (dwt)","pennyweight (dwt)"),
                                                ("pound (lb)","pound (lb)"),
                                                ("quarter","quarter"),
                                                ("stone","stone"),
                                                ("ton (UK, long)","ton (UK, long)"),
                                               ("ton (US, short)","ton (US, short)"),
                                                ("tonne (t)","tonne (t)"),
                                                ("troy ounce","troy ounce"),])

    #    size = fields.Char('Size', help="size of courier")
    delivery_carrier_id = fields.Many2one('delivery.carrier', 'Delivery Methods', help="Display the delivery methods")
    delivery_carrier_charges = fields.Float('Delivery Carrier Charges', help="Display the delivery charges")
    sub_total = fields.Float('Sub Total', compute='_compute_price',
                             help="Display the total of price, delivery charges and freight charges.")
    discount = fields.Float('Discount(%)', compute='_compute_discount', default='0.0',
                            help="Discount percentage of this customer")
    discount_amount = fields.Float('Discount amount', compute='_compute_final_price',
                                   help="Discount amount of this customer")
    final_price = fields.Float('Net delivery rate', compute='_compute_final_price',
                               help="Final amount this customer after discount")
    main_warehouse_id = fields.Many2one("stock.warehouse", "Main Warehouse", help="Source warehouse")
    target_warehouse_id = fields.Many2one("stock.warehouse", "Target Warehouse",
                                          help="The name of the target warehouse.")
    paid = fields.Boolean(compute="check_paid", string="Paid?", store=True,
                          default=False, copy=False, help="invoice is paid or not.")
    refund_invoice_id = fields.Many2one('account.invoice', string="Invoice for which this invoice is the refund")
    refund = fields.Boolean(compute="check_refund", default=False, copy=False, help="This courier is Invoice refunded")
    cod = fields.Boolean(string="COD", help="This courier is 'Cash on Delivery'")
    courier_type_id = fields.Many2one('courier.type', 'Courier Type', help="Types of the courier")
    invoice_total = fields.Float(compute="get_invoice_total", string='Invoice Total', help="Total amount of invoice")
    refund_invoice_total = fields.Float(compute="get_refund_invoice_total", string='Refund Invoice Total',
                                        help="Total refund amount of invoice")
    company_id = fields.Many2one('res.company', 'Company', help="The name of the company",
                                 default=lambda self: self.env.user.company_id.id)
    product_packaging_id = fields.Many2one('product.packaging', 'Product Packaging', help="The name of the package")
    freight_charge = fields.Float(string="Freight Charge")
    pickup_charge = fields.Float(string="Pick up Charge")
    ministry_charge = fields.Float(string="Ministry of Foreign Affairs Approval")
    export_decharge = fields.Float(string="Export Declaration(ED)")
    civil_aviation_charge = fields.Float(string="DCAA")
    other_charge = fields.Float(string="Other Charge")
    no_of_pieces = fields.Float(string="No of Boxes", compute='_compute_all_boxes',store=True)

    @api.depends('demo_id.no_of_boxes')
    def _compute_all_boxes(self):
        """
        Compute the total Number of boxes.
        """
        for order in self:
            boxes = 0.0
            for line in order.demo_id:
                boxes += line.no_of_boxes
            order.update({
                'no_of_pieces': boxes
            })

    # @api.onchange('demo_id')
    # def count_departments(self):
    #     self.no_of_pieces = len(self.demo_id)
    #     print(self.no_of_pieces)

    length = fields.Float(string="Length in cm", default=1)
    width = fields.Float(string="Width in cm", default=1)
    height = fields.Float(string="height in cm", default=1)

    discount_price = fields.Float(string="Discount amount")

    total_weight = fields.Float('Total Chargeable Weight', help="Total chargeable weight",  compute='_compute_all_amount',store=True)


    @api.depends('demo_id.total_weight_id')
    def _compute_all_amount(self):
        """
        Compute the total amounts of the weight_id.
        """
        for order in self:
            amount = 0.0
            for line in order.demo_id:
                amount += line.total_weight_id
            order.update({
                'total_weight': amount
            })

    total_price = fields.Float(string="Total price")
    declared_value = fields.Float(string="Declared value")
    declared_value_inUSD = fields.Float(string="USD", compute='_compute_usd_amount', store=True)

    @api.depends('declared_value')
    def _compute_usd_amount(self):
            rate_id = self.env['res.currency'].search([("name", "=", 'USD')], limit=1)
            print(rate_id.rate)
            self.declared_value_inUSD = rate_id.rate * self.declared_value
            print(self.declared_value_inUSD)


    delivery_location = fields.Text(string="Delivery Location")
    courier_zone_id = fields.Many2one(comodel_name='zone.zone', string="Zone",
                                      help='The zone where the state is located.')
    sender_phone = fields.Char(string="Phone", related="sender_id.phone")
    sender_mobile = fields.Char(string="Mobile", related="sender_id.mobile")
    receiver_phone = fields.Char(string="Recevier Phone", related="receiver_id.phone")
    receiver_mobile = fields.Char(string="Recevier Mobile", related="receiver_id.mobile")
    deliver_image_ids = fields.Binary(string="Binary Image", attachment=True)
    receiver_signature_ids = fields.Binary(string="Signature", attachment=True)
    booking_level = fields.Selection([("domestic_delivery", "DOMESTIC DELIVERY"),
                                      ("international_delivery", "INTERNATIONAL DELIVERY")])
    delivered_by = fields.Selection([("by_bike", "By Bike"),
                                      ("by_car", "By Car"),
                                     ("walk_in_Customer", "Walk-in-Customer")], string="Delivered By")
    cod_amount = fields.Float(string="COD amount")

    def get_values(self):

        return 'python method'

    def cal_price(self,weight,type,price):
        price_val = 25.0
        default_kg = 5.0
        if float(self.weight) and type == 'next_day_delivery_service':
            if float(weight) <= default_kg:
                price = price
            else:
                current_val = float(self.weight) - 5
                price = price + (current_val * 2)

        # Default 34 AED Upto 5 , Each KG add 3 AED
        price_val_1 = 34.0
        if float(weight) and type == 'return_service':
            if float(weight) <= default_kg:
                price = self.price
            else:
                current_val = float(weight) - 5
                price = price + (current_val * 3)

        # Default 48 AED Upto 5 , Each KG add 4 AED
        price_val_2 = 48.0
        if float(weight) and type == 'internal_outbond_express':
            if float(weight) <= default_kg:
                price = self.price
            else:
                current_val = float(weight) - 5
                price = price + (current_val * 4)

        # Default 75 AED Upto 5 , Each KG add 5 AED
        price_val_3 = 75.0
        if float(weight) and type == 'same_day_delivery_service':
            if float(weight) <= default_kg:
                price = price
            else:
                current_val = float(weight) - 5
                price = price + (current_val * 5)
        return price



    # @api.onchange('weight')
    # def _onchange_weight(self):
    #     # Default 25 AED Upto 5 , Each KG add 2 AED
    #     price_val = 25.0
    #     default_kg = 5.0
    #     if float(self.weight) and self.service_type == 'next_day_delivery_service':
    #         if float(self.weight) <= default_kg:
    #             self.price = self.price
    #         else:
    #             current_val = float(self.weight) - 5
    #             self.price = self.price + (current_val * 2)
    #
    #     # Default 34 AED Upto 5 , Each KG add 3 AED
    #     price_val_1 = 34.0
    #     if float(self.weight) and self.service_type == 'return_service':
    #         if float(self.weight) <= default_kg:
    #             self.price = self.price
    #         else:
    #             current_val = float(self.weight) - 5
    #             self.price = self.price + (current_val * 3)
    #
    #     # Default 48 AED Upto 5 , Each KG add 4 AED
    #     price_val_2 = 48.0
    #     if float(self.weight) and self.service_type == 'internal_outbond_express':
    #         if float(self.weight) <= default_kg:
    #             self.price = self.price
    #         else:
    #             current_val = float(self.weight) - 5
    #             self.price = self.price + (current_val * 4)
    #
    #     # Default 75 AED Upto 5 , Each KG add 5 AED
    #     price_val_3 = 75.0
    #     if float(self.weight) and self.service_type == 'same_day_delivery_service':
    #         if float(self.weight) <= default_kg:
    #             self.price = self.price
    #         else:
    #             current_val = float(self.weight) - 5
    #             self.price = self.price + (current_val * 5)
    # @api.onchange('height','weight','length','width','price','no_of_pieces','discount_price')
    # def _onchange_weight(self):
    #     self.dimensional_weight = (self.length * self.width * self.height) / 5000
    #     if self.weight >= self.dimensional_weight:
    #         self.chargeable_weight = self.weight
    #         current_price = self.weight * self.price * self.no_of_pieces
    #         self.total_price = current_price
    #     else:
    #         self.chargeable_weight = self.dimensional_weight
    #         current_price = self.dimensional_weight * self.price * self.no_of_pieces
    #         self.total_price = current_price

    @api.onchange("company_id")
    def update_warehouse(self):
        if self.company_id:
            w_id = self.env["stock.warehouse"].search([("company_id", "=", self.company_id.id)], limit=1)
            self.main_warehouse_id = w_id.id

    @api.onchange("area_id")
    def change_area_id(self):
        if self.area_id:
            self.zone_id = self.area_id.zone_id.id

    @api.onchange("sender_id")
    def load_address(self):
        self.street = self.sender_id.street
        self.street2 = self.sender_id.street2
        self.zip = self.sender_id.zip
        self.zone_id = self.sender_id.zone_id.id
        self.area_id = self.sender_id.area_id.id
        self.city = self.sender_id.city
        self.state_id = self.sender_id.state_id.id if self.sender_id.state_id else False
        self.country_id = self.sender_id.country_id.id if self.sender_id.country_id else False
        return {'domain': {'sender_location_id': [('partner_id', '=', self.sender_id.id)]}}

    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].sudo().next_by_code('courier.courier') or _('New')
        vals['name'] = vals['number']
        result = super(CourierCourier, self).create(vals)
        result.action_invoicing()
        return result

    @api.onchange("sender_location_id")
    def change_sender_location_id(self):
        if self and self.courier_method:
            if self.sender_location_id:
                if not self.sender_location_id.zone_id:
                    raise Warning("There is no zone set for Picking Location")
            else:
                self.courier_zone_id = self.sender_location_id.zone_id.id

    @api.onchange('receiver_id', 'delivered_by')
    def load_receiver_id_address(self):
        if self.receiver_id:
            if not self.receiver_id.zone_id:
                raise Warning("There is no zone set for Receiver")
            else:
                if self.delivered_by == 'by_bike':
                    self.price = self.receiver_id.area_id.by_bike
                elif self.delivered_by == 'by_car':
                    self.price = self.receiver_id.area_id.by_car
            check_address = self.env['courier.carrier.location'].search(
                [("partner_id", "=", self.receiver_id.id), ("street", "=", self.receiver_id.street)], limit=1)
            rec = check_address
            if not check_address:
                vals = {"street": self.receiver_id.street,
                        "street2": self.receiver_id.street2,
                        "zip": self.receiver_id.zip,
                        "city": self.receiver_id.city,
                        "zone_id": self.receiver_id.zone_id.id,
                        "partner_id": self.receiver_id.id,
                        "area_id": self.receiver_id.area_id.id,
                        "state_id": self.sender_id.state_id.id if self.sender_id.state_id else False,
                        "country_id": self.sender_id.country_id.id if self.sender_id.country_id else False}
                rec = self.env['courier.carrier.location'].create(vals)
            self.delivery_location_ids = rec.id
            # self.price = rec.zone_id.price
            if self.sender_location_id:
                self.courier_zone_id = self.sender_location_id.zone_id.id
            else:
                self.courier_zone_id = rec.zone_id.id

            return {'domain': {'delivery_location_ids': [('id', '=', rec.id)]}}

    @api.multi
    def write(self, vals):
        for rec in self:
            if vals.get('state'):
                self.env['courier.history'].create(
                    {'courier_id': rec.id,
                     'name': rec.name or '/',
                     'distance': rec.distance or 0,
                     'price': rec.final_price or 0.0,
                     'driver_id': rec.delivery_driver_id.id or rec.pickup_driver_id.id,
                     'from_state': rec.state,
                     'to_state': vals.get('state'),
                     'history_time': datetime.now()
                     })
                template_rec = self.env.ref("courier.email_template_courier_status")
                if template_rec:
                    rec.number = rec.number
                    receiver_name = rec.receiver_id and rec.receiver_id.name or ''
                    courier = rec.number or rec.name
                    from_state = dict(self.fields_get(allfields=['state'])['state']['selection'])[rec.state]
                    to_state = dict(self.fields_get(allfields=['state'])['state']['selection'])[vals.get('state')]
                    street = ''

                    street = rec.street if rec.street else rec.street2
                    if street == "" or street == False:
                        raise Warning("Please selection location first")
                    body_html = """
                        <![CDATA[<div style="font-family: 'Lucica Grande',
                        Ubuntu, Arial, Verdana, sans-serif; font-size: 14px;
                        color: rgb(34, 34, 34); background-color: #FFF; ">
                        <p>Hello """ + receiver_name + """,</p>
                        <p>Your Courier """ + courier + """ state is changed.
                        Courier status details is as below:</p>
                        <p style="border-left: 1px solid #8e0000; margin-left: 30px;" >
                        &nbsp; From State : """ + from_state + """
                        <br/> &nbsp; To State : """ + to_state + """
                        <br/> &nbsp; Current Location : """ + street + """
                        <br/></p><br/><p>
                        *** This is an automatically generated email, please do not reply *** </p>
                    """
                    template_rec.write({
                        'body_html': body_html,
                        'email_from': str(rec.sender_id and rec.sender_id.email or ''),
                        'email_to': str(rec.receiver_id and rec.receiver_id.email or ''),
                    })
                    template_rec.send_mail(rec.id, force_send=True)
        res = super(CourierCourier, self).write(vals)
        return res

    @api.multi
    def set_to_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})
        return True

    @api.multi
    def action_pickup_done(self):
        if self.pickup_driver_id:
            for rec in self:
                rec.write({'state': 'picked'})
        else:
            raise Warning("Please Assign driver for Pickup")
        return True

    @api.multi
    def cancel_courier(self):
        for rec in self:
            if rec.invoice_id:
                rec.invoice_id.action_invoice_cancel()
                rec.invoice_id.move_name = ''
                rec.invoice_id.unlink()
            rec.write({'state': 'cancel'})
        return True

    @api.multi
    def _get_invoice_count(self):
        for rec in self:
            if rec.invoice_id:
                rec.invoice_count = 1
            else:
                rec.invoice_count = 0


    @api.multi
    @api.depends('invoice_id.state')
    def check_paid(self):
        for rec in self:
            if rec.invoice_id and rec.invoice_id.state == 'paid':
                rec.paid = True
            else:
                rec.paid = False

    @api.multi
    @api.depends('invoice_id.state')
    def check_refund(self):
        for rec in self:
            if rec.invoice_id.id:
                refund_invoice_id = self.env['account.invoice'].search([
                    ('refund_invoice_id', '=', rec.invoice_id.id)], order='id desc', limit=1)
                rec.write({'refund_invoice_id': refund_invoice_id.id})
                if refund_invoice_id and refund_invoice_id.state == 'paid':
                    rec.refund = True
                else:
                    rec.refund = False

    @api.multi
    def action_view_invoice(self):
        invoices = self.mapped('invoice_id')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_view_refund_invoice(self):
        invoices = self.mapped('refund_invoice_id')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    @api.depends('total_price', 'delivery_carrier_charges')
    def _compute_price(self):
        for cour in self:
            cour.sub_total = cour.total_price + cour.delivery_carrier_charges-cour.discount_price

    @api.multi
    @api.depends('sender_id')
    def _compute_discount(self):
        for cour in self:
            if cour.sender_id.courier_discount_percentage:
                cour.discount = cour.sender_id.courier_discount_percentage

    @api.multi
    @api.depends('sub_total', 'discount')
    def _compute_final_price(self):
        for cour in self:
            if cour.discount:
                cour.discount_amount = (cour.sub_total / 100 * cour.discount)
                cour.final_price = cour.sub_total - (cour.sub_total / 100 * cour.discount)
            else:
                cour.discount_amount = 0.0
                cour.final_price = cour.sub_total

    @api.onchange('delivery_carrier_id', 'weight', 'price')
    def onchange_delivery_carrier_id(self):
        if self.delivery_carrier_id:
            PRICE = 0.0
            if self.delivery_carrier_id.delivery_type == 'fixed':
                margin = (float(self.delivery_carrier_id.margin) / 100.0)
                PRICE = self.delivery_carrier_id.fixed_price * (1.0 + margin)
                if self.delivery_carrier_id.free_if_more_than:
                    if self.price <= self.delivery_carrier_id.amount:
                        PRICE = 0.0
            if self.delivery_carrier_id.delivery_type == 'base_on_rule':
                PRICE = self.delivery_carrier_id.get_price_from_picking(
                    float(self.price), float(self.weight), 0, 1)
            self.delivery_carrier_charges = PRICE

    #            self.distance = self.routing_id.distance
    #            self.price = self.routing_id.price
    #            self.deliver_date = str((datetime.today()) + \
    #            datetime.timedelta(days=self.routing_id.days))

    @api.multi
    def action_packing(self):
        for rec in self:
            rec.write({'state': 'packing'})
        return True

    @api.multi
    def action_invoicing(self):
        invoice_obj = self.env['account.invoice']
        for rec in self:

            journal_id = self.env['account.invoice']._default_journal()
            account = journal_id.default_credit_account_id
            account_service = account
            product = rec.company_id.product_id or False
            if product:
                account_service = product.property_account_income_id or product.categ_id.property_account_income_categ_id

            line_vals = [(0, 0, {
                'name': rec.number,
                'product_id': product.id,
                'uom_id': product.uom_id.id,
                'price_unit': rec.sub_total,
                'account_id': account.id,
                'weight': rec.total_weight,
                'book_level': rec.booking_level,
                'quantity': rec.no_of_pieces,
            })]
            if rec.delivery_carrier_charges:
                line_vals.append((0, 0, {
                    'name': rec.number,
                    'product_id': product.id,
                    'uom_id': product.uom_id.id,
                    'price_unit': rec.delivery_carrier_charges,
                    'account_id': account_service.id
                }))
            if rec.discount_amount:
                line_vals.append((0, 0, {
                    'name': rec.number,
                    'product_id': product.id,
                    'uom_id': product.uom_id.id,
                    'price_unit': - rec.discount_amount,
                    'account_id': account_service.id
                }))

            invoice_vals = {'partner_id': rec.sender_id.id,
                            'receiever': rec.receiver_id.id,
                            'destination': rec.country_id.id,
                            'date': rec.date,
                            'invoice_line_ids': line_vals,
                            'type': 'out_invoice'}
            invoice_id = invoice_obj.create(invoice_vals)
            rec.track_ref = self.env['ir.sequence'].next_by_code('courier.tracking')
            if invoice_id:
                state = "invoiced"
                if rec.courier_method == "pickup_and_delivery":
                    state = "ready_to_pickup"
                rec.write({'state': state, 'invoice_id': invoice_id.id})
        return True

    @api.multi
    def action_inprogress(self):
        for rec in self:
            rec.write({'state': 'inprogress'})
        return True

    @api.multi
    def set_to_pickedup(self):
        for rec in self:
            rec.write({'state': 'pickedup'})
        return True

    @api.multi
    def set_to_customs_inspection(self):
        for rec in self:
            rec.write({'state': 'customs_inspection'})
        return True

    @api.multi
    def set_to_dnata_facility(self):
        for rec in self:
            rec.write({'state': 'dnata_facility'})
        return True

    @api.multi
    def set_to_departed_facility_in_dubai(self):
        for rec in self:
            rec.write({'state': 'departed_facility_in_dubai'})
        return True

    @api.multi
    def set_to_arrived_at_imamkhomeini_international_airport_ika(self):
        for rec in self:
            rec.write({'state': 'arrived_at_imamkhomeini_international_airport_ika'})
        return True

    @api.multi
    def set_to_clearance_processed(self):
        for rec in self:
            rec.write({'state': 'clearance_processed'})
        return True



    @api.multi
    def action_dispatch(self):
        if self.cod and not self.paid:
            raise UserError(_('In order to dispatch this COD courier, you must make payment first.'))
        elif not self.delivery_driver_id:
            raise UserError(_('Please Assign Driver for Dispatch'))
        for rec in self:
            rec.write({'state': 'dispatched'})
        return True

    @api.multi
    def action_ready_to_dispatch(self):
        if self.cod and not self.paid:
            raise UserError(_('In order to dispatch this COD courier, you must make payment first.'))
        for rec in self:
            rec.write({'state': 'ready_for_dispatched'})
        return True

    @api.multi
    def action_inscan(self):
        if self.cod and not self.paid:
            raise UserError(_('In order to dispatch this COD courier, you must make payment first.'))
        for rec in self:
            rec.write({'state': 'inscan'})
        return True

    @api.multi
    def action_outscan(self):
        if self.cod and not self.paid:
            raise UserError(_('In order to dispatch this COD courier, you must make payment first.'))
        for rec in self:
            rec.write({'state': 'outscan'})
        return True

    @api.multi
    def action_delivered(self):
        for rec in self:
            rec.write({'state': 'delivered'})
        return True

    @api.multi
    def action_damaged(self):
        for rec in self:
            rec.write({'state': 'damaged'})
        return True

    @api.multi
    def action_lost(self):
        for rec in self:
            rec.write({'state': 'lost'})
        return True

    @api.multi
    def action_return(self):
        if self.cod and not self.refund:
            raise UserError(
                _('In order to return this COD courier, you must raise a refund toward payment invoice first.'))
        for rec in self:
            rec.write({'state': 'return'})
        return True

    def action_refund(self):
        for rec in self:
            rec.write({'state': 'refunded'})
        return True

    def action_claim(self):
        for rec in self:
            rec.write({'state': 'claim'})
        return True


# ---------------------courier.history---------------------#
class CourierHistory(models.Model):
    _name = "courier.history"
    _description = "History of Courier"

    name = fields.Char('Name', required=True, help='The name of the History')
    #    from_location_id = fields.Many2one('courier.carrier.location', 'From Location')
    #    to_location_id = fields.Many2one('courier.carrier.location', 'To Location')
    from_location = fields.Char('From Location', help="The name of the from location.")
    to_location = fields.Char('To Location', help="The name of the to location.")
    dispatch_time = fields.Datetime('Dispatch Time', help="Display the dispatch time.")
    deliver_time = fields.Datetime('Deliver Time', help="Display the deliver time.")
    employee_id = fields.Many2one('res.users', 'Employee')
    price = fields.Float('Price', help="Display the price")
    days = fields.Float('Days', help="It is display no. of days")
    distance = fields.Char('Distance', help="It is display the distance")
    provider = fields.Many2one('res.partner', 'Provider', help="The name of the provider")
    driver_id = fields.Many2one('hr.employee', domain=[('is_driver', '=', True)], string='Assigned To',
                                help='The name of the assigned Employee.')
    carrier_id = fields.Many2one('courier.carrier', 'Carrier', help="The name of the carrier")
    courier_id = fields.Many2one('courier.courier', 'Courier', help="The name of the courier")
    from_state = fields.Selection(states, 'State', readonly=True, default='draft', help="The name of the from state ")
    to_state = fields.Selection(states, 'State', readonly=True, default='draft', help="The name of the to_state")
    history_time = fields.Datetime("Date Time", help="It is display history creation time")


# ---------------------courier.history---------------------#
class CourierWarehouse(models.Model):
    _name = "courier.warehouse"
    _rec_name = "name"
    _description = "Warehouse list"

    def default_warehouse_id(self):
        if self.env.user.company_id:
            w_id = self.env["stock.warehouse"].search([("company_id", "=", self.env.user.company_id.id)], limit=1)
            return w_id.id

    name = fields.Char()
    courier_id = fields.Many2one('courier.courier', 'courier')
    driver_id = fields.Many2one('hr.employee', 'Driver', domain=[('is_driver', '=', True)],
                                help='The name of the assigned Employee.')
    collected_by = fields.Char(string="Collected By")
    date = fields.Date(default=fields.Date.context_today)
    main_warehouse_id = fields.Many2one("stock.warehouse", "Main Warehouse", default=default_warehouse_id,
                                        help="Source warehouse")
    product_list = fields.One2many("product.barcode.list", "courier_warehouse_id")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('courier.scanning') or _('New')
        result = super(CourierWarehouse, self).create(vals)
        return result


class ProductBarcodeList(models.Model):
    _name = "product.barcode.list"
    _rec_name = "item_name"

    item_name = fields.Char()
    in_date = fields.Date(default=fields.Date.context_today, )
    Barcode = fields.Char()
    courier_warehouse_id = fields.Many2one("courier.warehouse")

class One2manyinsideform(models.Model):
    _name = "package.tree"

    custom_id = fields.Many2one("courier.courier")

    product_packaging_id = fields.Selection([("box", "Box")])
    length = fields.Float(string="Length in cm", default=1)
    width = fields.Float(string="Width in cm", default=1)
    height = fields.Float(string="height in cm", default=1)
    weight = fields.Float('Actual Weight', help="weight of courier")
    chargeable_weight = fields.Float('Chargeable Weight', help="compared of courier")
    dimensional_weight = fields.Float('Dimensional Weight', help="calculated weight")
    product_description = fields.Char(string="Product Description")
    no_of_boxes = fields.Float('No of Boxes', default=1)
    total_weight_id = fields.Float('Total')


    @api.onchange('height', 'length', 'width','weight', 'no_of_boxes', 'chargeable_weight', 'dimensional_weight')
    def _onchange_weight(self):
        self.dimensional_weight = (self.length * self.width * self.height) / 5000
        if self.weight >= self.dimensional_weight:
            self.chargeable_weight = self.weight
            self.total_weight_id = self.no_of_boxes * self.chargeable_weight
        else:
            self.chargeable_weight = self.dimensional_weight
            self.total_weight_id = self.no_of_boxes * self.chargeable_weight




# @api.depends('demo_id.weight_id')
    # def _compute_all_amount(self):
    #     """
    #     Compute the total amounts of the weight_id.
    #     """
    #     for order in self:
    #         amount = 0.0
    #         for line in order.demo_id:
    #             amount += line.weight_id
    #         order.update({
    #             'dimensional_weight': amount
    #         })

    # @api.onchange('weight', 'price', 'no_of_pieces', 'discount_price', 'dimensional_weight', 'coast')
    # def _onchange_weight(self):
    #     if self.weight >= self.dimensional_weight:
    #         self.chargeable_weight = self.weight
    #         current_price = (self.weight * self.coast) + self.price
    #         self.total_price = current_price
    #     else:
    #         self.chargeable_weight = self.dimensional_weight
    #         current_price = (self.dimensional_weight * self.coast) + self.price
    #         self.total_price = current_price