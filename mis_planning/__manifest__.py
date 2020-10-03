# -*- coding: utf-8 -*-
{
    'name': 'Mis Project Planning',
    'version': '13.0.1',
    'category': 'Project',
    'summary': """ """,
    'description': """ Project Planning
                    """,
    'author': "Hafeel",
    'website': 'Mindifnosys.com',
    'depends': ['base','crm', 'project', 'planning'],
    'data': [
        'views/crm_lead_views.xml',
        'views/planning_views.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
