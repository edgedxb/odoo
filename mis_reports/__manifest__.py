{
    'name': 'MIS-Reports',
    'version': '13.0.0.1',
    'summary': """MIS Reports""",
    'category': 'Report',
    'author': 'Hafeel Salim, hafeel.salim@gmail.com',
    'company': 'mindinfosys.com, UAE',
    'description': 'Report Customization',
    'website': 'www.mindinfosys.com',
    'depends': ['base', 'account','sale', 'purchase'],
    'data': [
        'reports/invoice_report_templates.xml',
#        'reports/report_list.xml',
#        'reports/purchase_report_templates.xml',
        'reports/payment_report_template.xml',
        'reports/sale_template.xml',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}