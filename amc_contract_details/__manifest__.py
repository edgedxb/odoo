# -*- coding: utf-8 -*-
{
    'name': 'AMC Contract Details',
    'version': '14.0.2.1.0',
    'summary': 'AMC Contract Details',
    'description': """AMC Contract Details""",
    'category': 'Others',
    'author': 'MindInfosys',
    'maintainer': 'MindInfosys',
    'license': 'AGPL-3',
    'depends': ['crm','account','base', 'mail','product','mis_planning'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/mail_template.xml',
        'data/ir_cron.xml',
        'views/amc_contract_view.xml',
        'reports/report.xml',
        'reports/amc_contract_report.xml'
    ],
    'demo': [],
    'qweb': [],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
