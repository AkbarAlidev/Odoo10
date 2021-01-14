# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Courier Website',
    'version': '10.0.0.0.1',
    'description': 'This module display tracking status to end user',
    'author': 'Febno',
    'category': 'website',
    'depends': [
        'website','web_settings_dashboard'
    ],
    'data': [
        'data/data_view.xml',
        'views/template_register_view.xml',
        'views/website_template_view.xml',
    ],
    'qweb': ['static/src/xml/template.xml'],
    'installable': True,
}