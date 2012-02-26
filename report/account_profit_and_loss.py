import netsvc
from report import report_sxw
from account.report.account_balance import account_balance
from account_cost_price import cost_price_parse
from common_report_excel import common_report_excel
from pxgo_openoffice_reports.openoffice_report import openoffice_report

class profit_and_loss_parse(account_balance):

    _name = 'report.account.profit_and_loss'

    def __init__(self, *args, **kwargs):
        super(profit_and_loss_parse, self).__init__(*args, **kwargs)
        self.obj_ab1 = account_balance(*args, **kwargs)

    def lines1(self, form, ids=[5150], done=None, bank=False):
        res = super(profit_and_loss_parse ,self).lines(form, ids, done)
        level = res[0]['level'] - 1
        for r in res:
            res[res.index(r)]['level'] -= level
            if r['code'].startswith('4') or r['code'].startswith('8') \
                or r['code'].startswith('70')\
                or r['code'].startswith('71'):
                    res[res.index(r)]['balance'] *= -1
            if bank:
                #if r['code'].startswith('7'):
                    #res[res.index(r)]['balance'] *= -1
                pass
        res_cost = self.obj_ab1.lines(form, ids=[4962])
        hide_codes = [i['code'] for i in res_cost[1:]]
        res_final = res[:]
        for r in res:
            if r['code'] in hide_codes:
                try:
                    res_final.remove(r)
                except:
                    pass
        for i, r in enumerate(res_final):
            if r['balance'] < 0:
                res_final[i]['balance_display'] = '(%s)' % self.formatLang(abs(r['balance']))
            else:
                res_final[i]['balance_display'] = '%s' % self.formatLang(r['balance'])

            #if r['code'] == '700000':
                #res_final.insert(i,{
                    #'credit': '',
                    #'code': '',
                    #'bal_type': '',
                    #'name': '',
                    #'parent_id': '',
                    #'level': '',
                    #'balance': '',
                    #'debit': '',
                    #'type': '',
                    #'id': ''
                #})

        return res_final
    def lines_tuple(self, form, ids=[], done=None):
        ''' for Aging report'''
        lines_list = []
        period_obj = self.pool.get('account.period')
        period_se = period_obj.read(self.cr, self.uid,
                    [form['period_from'],form['period_to']],
                    ['id','date_start'])
        period_ids = period_obj.search(self.cr, self.uid,
                args=[('date_start', '>=', period_se[0]['date_start']),
                      ('date_start', '<=', period_se[1]['date_start'])],
                order='date_start')
        self.periods = period_obj.read(self.cr, self.uid, period_ids, ['id','name'])
        netsvc.Logger().notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,
                                      'Periods: %s' % self.periods)
        for p in self.periods:
            new_form = form.copy()
            new_form['period_from'] = p['id']
            new_form['period_to'] = p['id']
            obj_self = profit_and_loss_parse(cr=self.cr, uid=self.uid, name=self.name, context=self.context)
            netsvc.Logger().notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,
                                      'New Form: %s' % new_form)
            line = obj_self.lines1(new_form)
            lines_list.append(line)

        return zip(*lines_list)


    def lines(self, form, ids=[5150], done=None):
        if form['template'] == 'bank' :
            res = self.lines1(form, ids, done, True)
        else:
            res = self.lines1(form, ids, done)
        if form['format_file'] == 'pdf' :
            return res
        self.periods = []
        self.period_obj = self.pool.get('account.period')
        self.period_se = self.period_obj.read(self.cr, self.uid,
                    [form['period_from'],form['period_to']],
                        ['id','date_start','date_stop'])
        if form['template'] == 'aging':
            period_lines = self.lines_tuple(form, ids, done)
            for i, r in enumerate(res):
                res[i]['periods'] = period_lines[i]
        if form['template'] == 'bank' :
            lres = []
            dres = {}
            for r in res:
                if r['type'] == 'view' or r['type'] == 'space' or r['code'] == '333400':
                    lres.append(r)
                    dres['c_%s' % r['code']] = r
            return (lres, dres)
        return (res, {})



report_sxw.report_sxw('report.account.profit_and_loss',
    'account.account',
    'addons/account_report_extra/report/account_profit_and_loss.rml',
    parser=profit_and_loss_parse, header="internal")

class profit_and_loss_excel_parse(common_report_excel):

    _name = 'report.account.profit_and_loss.excel'

    def __init__(self, name, cr, uid, ids, data, context):
        super(common_report_excel, self).__init__(name, cr, uid, ids, data, context)
        self.obj1 = profit_and_loss_parse(cr=cr, uid=uid, name=name, context=context)

    def get_report_context(self):
        res = {}
        laccounts, daccounts = self.obj1.lines(self.data['form'])
        res.update({
            'accounts': laccounts,
            'daccounts': daccounts,
            'periods': self.obj1.periods,
            'period_start': self.obj1.period_se[0],
            'period_stop': self.obj1.period_se[1],
        })
        return res

openoffice_report('report.account.profit_and_loss.excel',
    'account.account', parser=profit_and_loss_excel_parse)

openoffice_report('report.account.profit_and_loss.bank',
    'account.account', parser=profit_and_loss_excel_parse)

openoffice_report('report.account.profit_and_loss.aging.excel',
    'account.account', parser=profit_and_loss_excel_parse)
