# -*- coding: utf-8 -*-
{
    'name': 'edge reports',
    'summary': 'Custom reports as per the user requirements',
    'description': 'To generate custom reports',
    'author': 'Mindinfosys',
    'website': 'http://www.mindinfosys.com',
    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Reports',
    'version': '13.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'planning'],

    # always loaded
    'data': [

        'wizard/wizard_planning.xml',


    ],
    # only loaded in demonstration mode
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
