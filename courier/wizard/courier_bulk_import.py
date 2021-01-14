# -*- coding: utf-8 -*-
import binascii
import csv
import tempfile
import base64
import logging
import os

_logger = logging.getLogger(__name__)
import xlrd

from odoo import models, fields, tools, api
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class courierbulkimport(models.TransientModel):
    _name = 'courier.bulk.import'

    attachment_ids = fields.Many2many('ir.attachment', string='Upload File')
    file_data = fields.Binary('Archivo')
    file_name = fields.Char('File Name')
    xlsx_file = fields.Binary(string='Excel File')

    def import_buttoncsv(self):
        if not self.csv_validator(self.file_name):
            raise UserError(("kindly upload  .csv"))
        file_path = tempfile.gettempdir() + '/file.csv'
        data = self.file_data
        f = open(file_path, 'wb')
        f.write(base64.b64decode(data))
        # f.write(data.decode('base64'))
        f.close()
        archive = csv.DictReader(open(file_path))
        archive_lines = []
        try:
            for line in archive:
                archive_lines.append(line)

            for row in archive_lines:
                print("line",row)
                customer_name = row.get("Customer","")
                customer_phone = row.get("Tel1","")
                customer_mobile =row.get("Tel2","")
                customer_address = row.get("Address","")
                customer_city = row.get("City","")
                customer_area = row.get("Area","")
                customer_zone = row.get("Zone","")
                customer_zip = row.get("Zip","")
                customer_state = row.get("State","")
                customer_country = row.get("Country","")
                courier_method = row.get("Courier Method","")
                courier_type = row.get("Courier Type","")
                service_type_value = row.get("Service Type","")
                service_type =""
                if service_type_value:
                    if service_type_value =="Same Day Delivery Service(Bullet Service)":
                        service_type = "same_day_delivery_service"
                    if service_type_value =="Next Day Delivery Service":
                        service_type = "next_day_delivery_service"
                    if service_type_value =="COD E-commerce Shipments":
                        service_type = "cod_ecommerce_shipments"
                    if service_type_value =="Return Service(RTS)":
                        service_type = "return_service"
                    if service_type_value =="International OutBond Express":
                        service_type = "internal_outbond_express"
                # courier_date_val = datetime(*xlrd.xldate_as_tuple(str(row[11].value), 0))
                # print("-",datetime.strptime(str(row[11].value).encode('utf-8'), "%Y-%m-%d"))
                courier_date_val = "2020-03-21"
                recever_name = row.get("Recipient","")
                recever_phone = row.get("Recipient Phone","")
                recever_phone = row.get("Recipient Mobile","")
                amount = row.get("Price","")
                weight = row.get("Weight","")
                paid = row.get("","")
                no_of_pieces = row.get("Quantity","")
                cod =row.get("COD","")

                if courier_method == "Pickup & Delivery":
                    courier_method = "pickup_and_delivery"
                else:
                    courier_method = "delivery"

                existing_country = self.env['res.country'].search([("name", "ilike", customer_country)],
                                                                  limit=1)
                if existing_country:
                    customer_country_id = existing_country.id
                else:
                    rec_country_id = self.env['res.country.state'].create({"name": customer_state})
                    customer_country_id = rec_country_id.id
                existing_state = self.env['res.country.state'].search([("name", "ilike", customer_state)],
                                                                      limit=1)
                if existing_state:
                    customer_state_id = existing_state.id
                else:
                    rec_state_id = self.env['res.country.state'].create(
                        {"name": customer_state, "code": customer_state, "country_id": customer_country_id})
                    customer_state_id = rec_state_id.id
                existing_courier_type = self.env["courier.type"].search([("name", "ilike", courier_type)],limit=1)
                if existing_courier_type:
                    courier_type_id = existing_courier_type.id
                else:
                    rec_courier_type = self.env['courier.type'].create(
                        {"name": courier_type, "code": courier_type})
                    courier_type_id = rec_courier_type.id
                customer_area_rec =False
                if customer_area:
                    customer_area_rec =self.env['area.area'].search([("name","=",customer_area)])
                    if not customer_area_rec:
                        customer_zone_rec = self.env['zone.zone'].search([("name","=",customer_zone)])
                        if not customer_zone_rec:
                            customer_zone_rec = self.env['zone.zone'].create({"name": customer_zone})
                        customer_area_rec = self.env['area.area'].create({"name": customer_area,"zone_id":customer_zone_rec.id})
                print (customer_area_rec)
                if customer_name:
                    exisitng_customer = self.env['res.partner'].search(
                        [("name", "ilike", customer_name), ("phone", "=", customer_phone)])
                    if not exisitng_customer:
                        exisitng_customer = self.env['res.partner'].create(
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
                    exisitng_customer = self.env['res.partner'].search(
                        [("name", "ilike", recever_name), ("phone", "=", recever_phone)])
                    if not exisitng_customer:
                        exisitng_customer = self.env['res.partner'].create(
                            {"name": recever_name, "phone": recever_phone})
                    receiver_id = exisitng_customer
                    company_id = self.env["res.company"].search([("name", "ilike", "ON TIME COURIER")])
                    vals = {'sender_id': sender_id.id,
                            'receiver_id': receiver_id.id,
                            'weight': str(weight).split('.')[0],
                            'price': str(amount).split('.')[0],
                            'street': str(customer_address).split('.')[0],
                            'paid': paid,
                            "area_id":customer_area_rec.id,
                            "zone_id":customer_area_rec.zone_id.id,
                            "company_id": company_id.id,
                            'cod': True if cod=="1" else False,
                            'street2': "",
                            "no_of_pieces":no_of_pieces,
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
                    courier = self.env['courier.courier'].create(vals)
                    print(courier)

        except Exception as E:
            _logger.warning(E)
            raise ValidationError(E)

    @api.model
    def csv_validator(self, xml_name):
        name, extension = os.path.splitext(xml_name)
        return True if extension == '.csv' else False

    @api.multi
    def download_file_format(self):
        """ Donwload the template file for import"""
        doc_id = self.env['ir.attachment'].search([("datas_fname","=","BulkImportTemplateFile.csv")],limit=1)
        if not doc_id:
            path = os.path.dirname(os.path.realpath(__file__))
            parent_file_path = os.path.abspath(os.path.join(path, os.pardir))
            # create a directory under static folder
            xml_directory = parent_file_path + '/static/src/template/'
            xls_file_filepath = xml_directory + "import_details.csv"
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
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }


    def confirm_upload(self):
        """ Read the Excel and create Courier datas"""

        result = {}
        if self.xlsx_file:
            try:
                fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.xlsx_file))
                fp.seek(0)
                workbook = xlrd.open_workbook(fp.name)
                sheet = workbook.sheet_by_index(0)
                #                 no = 0
                sheet.cell_value(0, 0)
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

                        existing_country = self.env['res.country'].search([("name", "ilike", customer_country)],
                                                                          limit=1)
                        if existing_country:
                            customer_country_id = existing_country.id
                        else:
                            rec_country_id = self.env['res.country.state'].create({"name": customer_state})
                            customer_country_id = rec_country_id.id
                        existing_state = self.env['res.country.state'].search([("name", "ilike", customer_state)],
                                                                              limit=1)
                        if existing_state:
                            customer_state_id = existing_state.id
                        else:
                            rec_state_id = self.env['res.country.state'].create(
                                {"name": customer_state, "code": customer_state, "country_id": customer_country_id})
                            customer_state_id = rec_state_id.id
                        existing_courier_type = self.env["courier.type"].search([("name", "ilike", courier_type)])
                        if existing_courier_type:
                            courier_type_id = existing_courier_type.id
                        else:
                            rec_courier_type = self.env['courier.type'].create(
                                {"name": courier_type, "code": courier_type})
                            courier_type_id = rec_courier_type.id
                        if customer_name:
                            exisitng_customer = self.env['res.partner'].search(
                                [("name", "ilike", customer_name), ("phone", "=", customer_phone)])
                            if not exisitng_customer:
                                exisitng_customer = self.env['res.partner'].create(
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
                            exisitng_customer = self.env['res.partner'].search(
                                [("name", "ilike", recever_name), ("phone", "=", recever_phone)])
                            if not exisitng_customer:
                                exisitng_customer = self.env['res.partner'].create(
                                    {"name": recever_name, "phone": recever_phone})
                            receiver_id = exisitng_customer
                            company_id = self.env["res.company"].search([("name", "ilike", "ON TIME COURIER")])
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
                                    # 'date': datetime.strptime(str(courier_date_val),
                                    #                           tools.DEFAULT_SERVER_DATE_FORMAT)

                                    # 'date': datetime.strptime(courier_date_val, "%d/%M/%Y"),
                                    }
                            print(vals)
                            courier = self.env['courier.courier'].create(vals)
                            print(courier)


            except Exception as E:
                _logger.warning(E)
                raise ValidationError(E)

        return result
