# -*- coding: utf-8 -*-
######################################################################################################
#
# Copyright (C) B.H.C. sprl - All Rights Reserved, http://www.bhc.be
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# This code is subject to the BHC License Agreement
# Please see the License.txt file for more information
# All other rights reserved
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied,
# including but not limited to the implied warranties
# of merchantability and/or fitness for a particular purpose
######################################################################################################
from odoo import api, fields, models, _


class CourierRouting(models.Model):
    _inherit = 'courier.routing'
    
    @api.multi
    def open_map(self):
        for rec in self:
            from_url="https://www.google.co.in/maps/dir/"
            if rec.from_location_id.street:
                from_url+=rec.from_location_id.street.replace(' ','+')
            if rec.from_location_id.city:
                from_url+='+'+rec.from_location_id.city.replace(' ','+')
            if rec.from_location_id.state_id:
                from_url+='+'+rec.from_location_id.state_id.name.replace(' ','+')
            if rec.from_location_id.country_id:
                from_url+='+'+rec.from_location_id.country_id.name.replace(' ','+')
            if rec.from_location_id.zip:
                from_url+='+'+rec.from_location_id.zip.replace(' ','+') + '/'
            if rec.to_location_id.street:
                from_url+=rec.to_location_id.street.replace(' ','+')
            if rec.to_location_id.city:
                from_url+='+'+rec.to_location_id.city.replace(' ','+')
            if rec.to_location_id.state_id:
                from_url+='+'+rec.to_location_id.state_id.name.replace(' ','+')
            if rec.to_location_id.country_id:
                from_url+='+'+rec.to_location_id.country_id.name.replace(' ','+')
            if rec.from_location_id.zip:
                from_url+='+'+rec.to_location_id.zip.replace(' ','+')
            return {
                'type': 'ir.actions.act_url',
                'name': "Address",
                'target': 'new',
                'url': from_url,
                'nodestroy': True,
                'target_type': 'public',
            }
    

class CourierRoutingPath(models.Model):
    
    _inherit = 'courier.routing.path'
    @api.multi
    def open_map(self):
        for rec in self:
            from_url="https://www.google.co.in/maps/dir/"
            if rec.from_location_id.street:
                from_url+=rec.from_location_id.street.replace(' ','+')
            if rec.from_location_id.city:
                from_url+='+'+rec.from_location_id.city.replace(' ','+')
            if rec.from_location_id.state_id:
                from_url+='+'+rec.from_location_id.state_id.name.replace(' ','+')
            if rec.from_location_id.country_id:
                from_url+='+'+rec.from_location_id.country_id.name.replace(' ','+')
            if rec.from_location_id.zip:
                from_url+='+'+rec.from_location_id.zip.replace(' ','+') + '/'
            if rec.to_location_id.street:
                from_url+=rec.to_location_id.street.replace(' ','+')
            if rec.to_location_id.city:
                from_url+='+'+rec.to_location_id.city.replace(' ','+')
            if rec.to_location_id.state_id:
                from_url+='+'+rec.to_location_id.state_id.name.replace(' ','+')
            if rec.to_location_id.country_id:
                from_url+='+'+rec.to_location_id.country_id.name.replace(' ','+')
            if rec.from_location_id.zip:
                from_url+='+'+rec.to_location_id.zip.replace(' ','+')
            return {
                'type': 'ir.actions.act_url',
                'name': "Address",
                'target': 'new',
                'url': from_url,
                'nodestroy': True,
                'target_type': 'public',
            }

class launch_map(models.Model):
    
    _inherit = "res.partner"

    @api.multi
    def open_map(self):
        for partner in self:
            url="http://maps.google.com/maps?oi=map&q="
            if partner.street:
                url+=partner.street.replace(' ','+')
            if partner.city:
                url+='+'+partner.city.replace(' ','+')
            if partner.state_id:
                url+='+'+partner.state_id.name.replace(' ','+')
            if partner.country_id:
                url+='+'+partner.country_id.name.replace(' ','+')
            if partner.zip:
                url+='+'+partner.zip.replace(' ','+')
            return {
                'type': 'ir.actions.act_url',
                'name': "Address",
                'target': 'self',
                'url': url,
                'nodestroy': True,
                'target_type': 'public',
            }
