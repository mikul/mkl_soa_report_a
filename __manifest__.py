{
    'name': 'Customer Statement of Account',
    'version': '17.1',
    'category': 'Accounting',
    'summary': 'Generates a Customer Statement of Account with a detailed transaction summary',
    'description': 'Displays opening balance, invoiced amount, payments, and balance due',
    'depends': ['account','base'],
    'data': [
        'security/ir.model.access.csv',
        'report/customer_statement_template.xml',
        'report/customer_statement_report.xml',
        'wizard/customer_statement_wizard_view.xml',

    ],
    'installable': True,
    'application': False,
}
