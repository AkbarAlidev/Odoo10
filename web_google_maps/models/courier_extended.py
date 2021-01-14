# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.addons.base_geolocalize.models import res_partner


class CourierCourier(models.Model):
    _inherit = "courier.courier"

    street = fields.Char(string='Street',
                         help='The name of the street')
    street2 = fields.Char(string='Street2',
                          help='The name of the another street2.')
    zip = fields.Char(string='Zip', change_default=True,
                      help='The name of the zip code.')
    city = fields.Char(string='City', help='The name of the city.')
    state_id = fields.Many2one(comodel_name='res.country.state', string='State',
                               help='The name of the state.')
    country_id = fields.Many2one(comodel_name='res.country',
                                 string='Country',
                                 help='The name of the country.')
    latitude = fields.Float(string='Latitude', digits=(16, 8),
                            help='Latitude of the place.')
    longitude = fields.Float(string='Longitude', digits=(16, 8),
                             help='Longitude of the place.')
    previous_location = fields.Char('Previous Location')

    #    current_location = fields.Char('Current Location')

    @api.model
    def create(self, vals):
        if 'street' in vals:
            vals.update({'previous_location': vals['street']})
        if 'sender_location_id' in vals:
            loc_rec = self.env['courier.carrier.location'].search([("id","=",int(vals.get("sender_location_id")))])
            if loc_rec:
                vals.update({'previous_location': loc_rec.street})
                loc_rec.write({"partner_id":int(vals.get("sender_id"))})

        return super(CourierCourier, self).create(vals)

    def write(self, vals):
        hist_obj = self.env['courier.history']
        for rec in self:
            if 'street' in vals:
                rec.previous_location = rec.street
            if 'state' in vals:
                history = hist_obj.search([('courier_id', '=', rec.id),
                                           ('from_state', '=', rec.state),
                                           ('to_state', '=', vals['state'])], limit=1)
                history.write({
                    'from_location': rec.previous_location,
                    'to_location': rec.street
                })
        return super(CourierCourier, self).write(vals)

    @api.multi
    def open_map(self):
        for rec in self:
            if not rec.street:
                raise Warning(_(
                    'Please select Location first'))
            result = res_partner.geo_find(res_partner.geo_query_address(street=rec.street,
                                                                        zip=rec.zip,
                                                                        city=rec.city,
                                                                        state=rec.state_id.name,
                                                                        country=rec.country_id.name))
            if result is None:
                result = res_partner.geo_find(res_partner.geo_query_address(
                    city=rec.city,
                    state=rec.state_id.name,
                    country=rec.country_id.name
                ))
            if result:
                rec.write({
                    'latitude': result[0],
                    'longitude': result[1],
                })

            from_url = "https://www.google.co.in/maps/dir/"
            if not rec.routing_id:
                raise Warning(_(
                    'Please select routing first'))
            if rec.routing_id:
                if rec.routing_id.from_location_id.street:
                    from_url += rec.routing_id.from_location_id.street.replace(' ', '+')
                if rec.routing_id.from_location_id.city:
                    from_url += '+' + rec.routing_id.from_location_id.city.replace(' ', '+')
                if rec.routing_id.from_location_id.state_id:
                    from_url += '+' + rec.routing_id.from_location_id.state_id.name.replace(' ', '+')
                if rec.routing_id.from_location_id.country_id:
                    from_url += '+' + rec.routing_id.from_location_id.country_id.name.replace(' ', '+')
                if rec.routing_id.from_location_id.zip:
                    from_url += '+' + rec.routing_id.from_location_id.zip.replace(' ', '+') + '/'
                if rec.routing_id.to_location_id.street:
                    from_url += rec.routing_id.to_location_id.street.replace(' ', '+')
                if rec.routing_id.to_location_id.city:
                    from_url += '+' + rec.routing_id.to_location_id.city.replace(' ', '+')
                if rec.routing_id.to_location_id.state_id:
                    from_url += '+' + rec.routing_id.to_location_id.state_id.name.replace(' ', '+')
                if rec.routing_id.to_location_id.country_id:
                    from_url += '+' + rec.routing_id.to_location_id.country_id.name.replace(' ', '+')
                if rec.routing_id.from_location_id.zip:
                    from_url += '+' + rec.routing_id.to_location_id.zip.replace(' ', '+')
                return {
                    'type': 'ir.actions.act_url',
                    'name': "Address",
                    'target': 'new',
                    'url': from_url,
                    'nodestroy': True,
                    'target_type': 'public',
                }

    @api.multi
    def action_map_route(self):
        self.ensure_one()
        context = self.env.context.copy()
        user_id = self
        if not all([user_id.longitude, user_id.latitude]):
            raise Warning(_(
                'You have not defined your geolocation'))
        context.update({
            'origin_latitude': user_id.latitude,
            'origin_longitude': user_id.longitude,
            'destination_latitude': self.latitude,
            'destination_longitude': self.longitude
        })
        partners = [user_id.id, self.id]
        view_map_id = self.env.ref('web_google_maps.view_courier_map')
        return {
            'name': _('Map'),
            'type': 'ir.actions.act_window',
            'res_model': 'courier.courier',
            'view_mode': 'map',
            'view_type': 'map',
            'views': [(view_map_id.id, 'map')],
            'context': context,
            'domain': [('id', 'in', partners)]
        }

    @api.model
    def create_partner_from_map(self, values):
        default_fields = ['street', 'street2',
                          'city', 'zip', 'country_id', 'state_id',
                          'latitude', 'longitude']
        if isinstance(values, dict) and any(
                val in default_fields for val in values.keys()):
            courier_id = self.env['courier.courier'].create(values)
            return courier_id
        else:
            return False




