{
    'name': 'Edge Helpdesk',
    'category': 'Operations/Helpdesk',
    'summary': 'Edgedxb Project, Tasks, After Sales',
    'depends': ['helpdesk', 'sale_management','helpdesk_sale'],
    'auto_install': True,
    'description': """
Edge helpdesk tickets.
    """,
    'data': [
        'views/helpdesk_views.xml',
    ],
}
