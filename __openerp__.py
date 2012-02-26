{
    'name': 'Account Report Extra',
    'version': '0.1',
    'author': "Ahmad 'Ata' Tanwir",
    'category': 'Account/Report/Extra',
    'description': 'Extra Report for accounting',
    'depends': ['account','pxgo_openoffice_reports'],
    'update_xml':[
        'wizard/account_report_cost_price.xml',
        'wizard/account_report_profit_and_loss.xml',
        'wizard/account_report_balance_sheet.xml',
        'report/account_report.xml',
    ],
    'init_xml': [],
    'installable': True,
    'active': False,
}
