import netsvc
from osv import fields, osv

class account_profit_and_loss_report(osv.osv_memory):
    _inherit = "account.common.account.report"
    _name = 'account.profit_and_loss.report'
    _description = 'Profit And Report'

    _columns = {
        'format_file': fields.selection([('pdf', 'PDF'),
                                         ('excel', 'Excel'),
                                        ], 'Format', required=True),
        #'aging': fields.boolean('Aging'),
        #'summary':  fields.boolean('Summary'),
        'template':fields.selection([('default','Default'),
                                ('aging','Aging'),
                                ('bank','For Bank')],
                                'Template', required=True)
    }

    _defaults = {
        'journal_ids': [],
        'format_file': 'excel',
        #'aging': False,
        #'summary': False,
        'format_file': 'excel',
        'template': 'default',
    }

    #def onchange_aging(self, cr, uid, ids, aging=False,
        #fiscalyear_id=False, context=None):
        #if aging:
            #return {'value': {'filter': 'filter_period',
                    #'format_file': 'excel',
                    #'display_account': 'bal_all',
                    #'date_from': False,
                    #'date_to': False}}
        #return {}

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
        #data['form'].update(self.read(cr, uid, ids, ['format_file','aging','summary'])[0])
        data['form'].update(self.read(cr, uid, ids, ['format_file','template'])[0])
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        netsvc.Logger().notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,
                                      'Data: %s' % data)
        #if data['form']['aging']:
            #return {'type': 'ir.actions.report.xml', 'report_name': 'account.profit_and_loss.aging.excel', 'datas': data}
        #if data['form']['format_file'] == 'excel':
            #return {'type': 'ir.actions.report.xml', 'report_name': 'account.profit_and_loss.excel', 'datas': data}
        #return {'type': 'ir.actions.report.xml', 'report_name': 'account.profit_and_loss', 'datas': data}

        if data['form']['template'] == 'aging':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.profit_and_loss.aging.excel', 'datas': data}
        if data['form']['template'] == 'bank':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.profit_and_loss.bank', 'datas': data}
        if data['form']['format_file'] == 'excel':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.profit_and_loss.excel', 'datas': data}
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.profit_and_loss', 'datas': data}

account_profit_and_loss_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
