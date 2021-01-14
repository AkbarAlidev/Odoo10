# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    product_id = fields.Many2one('product.product', 'Product', default=lambda self: self.env['product.product'].search(
        [('type', '=', 'service')], limit=1).id, help="Display the service type of product.")
    terms_condition = fields.Html('Terms & Conditions', help="Terms and conditions for a company")
