# -*- coding: utf-8 -*-
{
    'name': 'Mis Project Planning',
    'version': '13.0.1',
    'category': 'CRM',
    'summary': """ """,
    'description': """ Project Planning
                    """,
    'author': "Hafeel",
    'website': 'Mindifnosys.com',
    'depends': ['base','crm', 'planning', 'sale'],
    'data': [
        'views/area_views.xml',
        'views/crm_lead_views.xml',
        'views/planning_views.xml',
        'data/mail_template_data.xml',
        'views/planning_status_views.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
