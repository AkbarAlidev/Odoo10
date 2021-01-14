# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2020 Febno Technologies
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from .google_maps import GoogleMaps
from odoo import models, fields, api
import datetime
import time


class CourierCarrier(models.Model):
    _inherit = 'courier.carrier'

    @api.multi
    @api.onchange('from_location_id', 'to_location_id')
    def get_duration(self):
        origin = ''
        destination = ''
        for rec in self:
            origin = rec.from_location_id and rec.from_location_id.city + ' ' + \
                    rec.from_location_id.street + ' ' +\
                    rec.from_location_id.street2 + \
                    ' ' + rec.from_location_id.state_id.code + ' ' + \
                    rec.from_location_id.zip
            destination = rec.to_location_id and rec.to_location_id.city + ' ' + \
                    rec.to_location_id.street + ' ' +\
                    rec.to_location_id.street2 + \
                    ' ' + rec.to_location_id.state_id.code + ' ' + \
                    rec.to_location_id.zip
            departure_time = self._context.get('departure_time')
            if not departure_time:
                n = datetime.datetime.now()
                departure_time = int(time.mktime(n.timetuple()))
            maps = GoogleMaps()
            duration = maps.duration(origin, destination, mode='driving', departure_time=departure_time)
            distance = maps.distance(origin, destination, mode='driving', departure_time=departure_time)
            rec.distance = distance
            rec.days = duration


class CourierRouting(models.Model):
    _inherit = 'courier.routing'

    @api.multi
    @api.onchange('from_location_id', 'to_location_id')
    def get_duration(self):
        origin = ''
        destination = ''
        for rec in self:
            if rec.from_location_id and rec.to_location_id:
                origin = rec.from_location_id and rec.from_location_id.city + ' ' + \
                        rec.from_location_id.street + ' ' +\
                        rec.from_location_id.street2 + \
                        ' ' + rec.from_location_id.state_id.code + ' ' + \
                        rec.from_location_id.zip
                destination = rec.to_location_id.city + ' '+ ' ' + \
                            rec.to_location_id.street+ ' ' + \
                            rec.to_location_id.street2 + \
                            ' ' + rec.to_location_id.state_id.code + ' ' + \
                                rec.to_location_id.zip
                departure_time = self._context.get('departure_time')
                if not departure_time:
                    n = datetime.datetime.now()
                    departure_time = int(time.mktime(n.timetuple()))
                maps = GoogleMaps()
                duration = maps.duration(origin, destination, mode='driving', departure_time=departure_time)
                distance = maps.distance(origin, destination, mode='driving', departure_time=departure_time)
                rec.distance = distance
                rec.days = duration

class CourierRoutingPath(models.Model):
    _inherit = 'courier.routing.path'

    @api.multi
    @api.onchange('from_location_id', 'to_location_id')
    def get_duration(self):
        origin = ''
        destination = ''
        for rec in self:
            if rec.from_location_id and rec.to_location_id:
                origin = rec.from_location_id and rec.from_location_id.city + ' ' + \
                        rec.from_location_id.street + ' ' +\
                        rec.from_location_id.street2 + \
                        ' ' + rec.from_location_id.state_id.code + ' ' + \
                        rec.from_location_id.zip
                destination = rec.to_location_id.city + ' '+ ' ' + \
                            rec.to_location_id.street+ ' ' + \
                            rec.to_location_id.street2 + \
                            ' ' + rec.to_location_id.state_id.code + ' ' + \
                                rec.to_location_id.zip
                departure_time = self._context.get('departure_time')
                if not departure_time:
                    n = datetime.datetime.now()
                    departure_time = int(time.mktime(n.timetuple()))
                maps = GoogleMaps()
                duration = maps.duration(origin, destination, mode='driving', departure_time=departure_time)
                distance = maps.distance(origin, destination, mode='driving', departure_time=departure_time)
                rec.distance = distance
                rec.days = duration

class hr_job(models.Model):
    _inherit = 'hr.job'

    @api.multi
    def get_duration(self):
        origin = 'Gandhinagar 301 Siddharz zavod'
        destination = 'Airport Ahmedabad'
        departure_time = self._context.get('departure_time')
        if not departure_time:
            n = datetime.datetime.now()
            departure_time = int(time.mktime(n.timetuple()))
        maps = GoogleMaps()
        duration = maps.duration(origin, destination, mode='driving', departure_time=departure_time)
        distance = maps.distance(origin, destination, mode='driving', departure_time=departure_time)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: