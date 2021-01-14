# -*- coding: utf-8 -*-

{
    'name': "Hide defualt report in Accounting",

    'summary': """
        Hide defualt report in Accounting""",
    'author': 'Febno,'
             ,
    'website': "http://febno.com",
    'category': 'Reporting',
    'version': '10.0.1.1.1',
    'license': 'AGPL-3',

    'depends': ['account'],
    'data': [
        'views/hide_reportview.xml',
    ],
    'installable': True,
}
