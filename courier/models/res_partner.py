# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResPartner(models.Model):
    """ Res Partner """
    _inherit = 'res.partner'
    _description = "Inherit Res Partner"

    code = fields.Char(string='Customer Code', required=False,
                       copy=False, readonly=False, index=True,
                       default=lambda self: _(''))
    zone_id = fields.Many2one('zone.zone', string="Zone", help='The zone where the state is located.')
    area_id = fields.Many2one('area.area', string="Area", help='The Area')
    is_portal_user = fields.Boolean(string="Portal User")

    def create_portal_user(self):
        """ create web portal access """
        if self:
            vals={"name":self.name,
                  "login":self.email if self.email else self.name
                  }
            user_rec = self.env["res.users"].create(vals)
            self.is_portal_user = True
            group_portal = self.env.ref('base.group_portal', False)
            if group_portal:
              user_rec.write({'groups_id':[(6, 0, [group_portal.id])]
                              })



    @api.onchange("area_id")
    def change_area_id(self):
        if self.area_id:
            print(self.area_id.zone_id)
            self.zone_id = self.area_id.zone_id.id

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].sudo().next_by_code(
                                                'res.partner.code') or 'New'
        print(vals['code'])
        if vals.get("street1"):
            vals["street"]= vals.get("street1")

        partner = super(ResPartner, self).create(vals)
        print(partner)
        return partner