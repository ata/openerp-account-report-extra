import netsvc
from osv import fields, osv

class account_balance_sheet_report(osv.osv_memory):
    _inherit = "account.common.account.report"
    _name = 'account.balance_sheet.report'
    _description = 'Balance Sheet'

    _columns = {
        'format_file': fields.selection([('pdf', 'PDF'),
                                         ('excel', 'Excel'),
                                        ], 'Format', required=True),
        'template':fields.selection([('default','Default'),
                                ('aging','Aging'),
                                ('bank','For Bank')],
                                'Template', required=True)
    }

    _defaults = {
        'journal_ids': [],
        'format_file': 'excel',
        'template': 'default',
    }

    def onchange_template(self, cr, uid, ids, template,
        fiscalyear_id=False, context=None):
        if template == 'aging':
            return {'value': {'filter': 'filter_period',
                    'format_file': 'excel',
                    'display_account': 'bal_all',
                    'date_from': False,
                    'date_to': False}}
        return {}

    def _print_report(self, cr, uid, ids, data, context=None):
        data['form'].update(self.read(cr, uid, ids, ['format_file','template'])[0])
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        netsvc.Logger().notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,
                                      'Data: %s' % data)
        if data['form']['template'] == 'aging':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.balance_sheet.aging.excel', 'datas': data}
        if data['form']['template'] == 'bank':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.balance_sheet.bank', 'datas': data}
        if data['form']['format_file'] == 'excel':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.balance_sheet.excel', 'datas': data}
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.balance_sheet', 'datas': data}

account_balance_sheet_report()
