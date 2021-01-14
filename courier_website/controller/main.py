# -*- coding: utf-8 -*-
import odoo.http as http
from odoo.http import request


class CourierWebsite(http.Controller):

    @http.route('/page/trackingpage', type='http', auth='public', website=True, csrf=False)
    def show_tracking_webpage(self, **kw):
        values = {'courier': {}}
        courier = request.env['courier.courier']
        location_dict = {}
        hist_location = []
        if kw and 'track' in kw:
            courier_rec = courier.sudo().search(['|',
                                                 ('track_ref', '=', str(kw['track'])),
                                                 ('number', '=', str(kw['track']))
                                                 ])
            current_loc = courier_rec.street
            start_loc = courier_rec.routing_id.from_location_id.street
            end_loc = courier_rec.routing_id.to_location_id.street
            for rec in courier_rec.history_ids:
                hist_location.append(rec.to_location)

            if start_loc == current_loc:
                location_dict[start_loc] = 'current'
            elif start_loc in hist_location:
                location_dict[start_loc] = 'done'
            else:
                location_dict[start_loc] = 'grayout'

            for loc in hist_location:
                if loc == current_loc:
                    location_dict[loc] = 'current'
                elif loc in hist_location:
                    location_dict[loc] = 'done'
                else:
                    location_dict[loc] = 'grayout'
            if end_loc == current_loc:
                location_dict[end_loc] = 'current'
            elif end_loc in hist_location:
                location_dict[end_loc] = 'done'
            else:
                location_dict[end_loc] = 'grayout'
            values['courier'] = courier_rec
            values['locations'] = location_dict
        if kw and not values['courier']:
            values.update({'show': True,
                           'track': kw['track']})

        return http.request.render('courier_website.website_courier_page_id', values)
