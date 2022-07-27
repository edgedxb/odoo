
{
    'name': 'Edge Budget',
    'category': 'Others',
    'description': """
Use budgets to compare actual with expected revenues and costs
--------------------------------------------------------------
""",

    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/edged_budget_views.xml',
    ],
    'license': 'OEEL-1',
}
