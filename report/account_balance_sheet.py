from copy import deepcopy, copy
import netsvc
from report import report_sxw
from account.report.account_balance import account_balance
from account_cost_price import cost_price_parse
from common_report_excel import common_report_excel
from pxgo_openoffice_reports.openoffice_report import openoffice_report

class balance_sheet_parse(account_balance):

    _name = 'report.account.balance_sheet'

    def __init__(self, *args, **kwargs):
        super(balance_sheet_parse, self).__init__(*args, **kwargs)
        self.obj_ab1 = account_balance(*args, **kwargs)
        self.obj_ab2 = account_balance(*args, **kwargs)
        self.obj_ab3 = account_balance(*args, **kwargs)
        #self.localcontext.update({
            #'lines1': self.lines1,
        #})


    def lines1(self, form, ids=[], done=None):
        bal_solde = False
        res_activa = self.obj_ab1.lines(form, ids=[4795])
        space = {
            'credit': '',
            'code': '',
            'bal_type': '',
            'name': '',
            'parent_id': '',
            'level': '',
            'balance': '',
            'debit': '',
            'type': 'space',
            'id': ''
        }
        res_activa.append(space)
        res_activa.append(space)
        res_passiva = self.obj_ab2.lines(form, ids=[4917])
        res_passiva_ignore = self.obj_ab3.lines(form, ids=[5150])
        res_passiva_tmp = res_passiva[:]
        pnl = res_passiva_ignore[0]['balance']
        hide_codes = [i['code'] for i in res_passiva_ignore]
        for r in res_passiva:
            if r['code'] in hide_codes:
                res_passiva_tmp.remove(r)
            #if r['code'] == '330000':
                #res_passiva_tmp[res_passiva_tmp.index(r)]['balance'] += pnl
            if r['code'] == '333400':
                res_passiva_tmp[res_passiva_tmp.index(r)]['balance'] += pnl
        res = res_activa + res_passiva_tmp
        res_final = res[:]
        if form['display_account'] == 'bal_solde':
            res_final.append({
                'credit': 0.0,
                'code': u'333400',
                'bal_type': '',
                'name': u'Saldo Laba dan Rugi',
                'parent_id': (4943, u'330000 Saldo Laba (Rugi)'),
                'level': 4,
                'balance': pnl,
                'debit': 0.0,
                'type': 'view',
                'id': 5222
            })
        for i, r in enumerate(res_final):
            if r['code'].startswith('2') or r['code'].startswith('3'):
                res_final[i]['balance'] *= -1
            if r['balance'] < 0:
                res_final[i]['balance_display'] = '(%s)' % self.formatLang(abs(r['balance']))
            else:
                res_final[i]['balance_display'] = '%s' % self.formatLang(r['balance'])
            res_final[i]['periods'] = []
        return res_final

    def lines_tuple(self, form, ids=[], done=None):
        ''' for Aging report'''
        lines_list = []
        period_ids = self.period_obj.search(self.cr, self.uid,
                args=[('date_start', '>=', self.period_se[0]['date_start']),
                      ('date_start', '<=', self.period_se[1]['date_start'])],
                order='date_start')
        self.periods = self.period_obj.read(self.cr, self.uid, period_ids, ['id','name','date_start','date_stop'])
        netsvc.Logger().notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,
                                      'Periods: %s' % self.periods)
        for p in self.periods:
            new_form = form.copy()
            #new_form['period_from'] = p['id']
            new_form['period_to'] = p['id']
            obj_self = balance_sheet_parse(cr=self.cr, uid=self.uid, name=self.name, context=self.context)
            line = obj_self.lines1(new_form)
            lines_list.append(line)

        return zip(*lines_list)


    def lines(self, form, ids=[], done=None):
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


report_sxw.report_sxw('report.account.balance_sheet',
    'account.account',
    'addons/account_report_extra/report/account_balance_sheet.rml',
    parser=balance_sheet_parse, header="internal")


class balance_sheet_excel_parse(common_report_excel):
    _name = 'report.account.balance_sheet.excel'
    def __init__(self, name, cr, uid, ids, data, context):
        super(common_report_excel, self).__init__(name, cr, uid, ids, data, context)
        self.obj1 = balance_sheet_parse(cr=cr, uid=uid, name=name, context=context)

    def get_report_context(self):
        res = {}
        laccounts, daccounts = self.obj1.lines(self.data['form'])
        #datetime.strptime('2011-09-30','%Y-%m-%d').strftime('%Y')
        res.update({
            'accounts': laccounts,
            'daccounts': daccounts,
            'periods': self.obj1.periods,
            'period_start': self.obj1.period_se[0],
            'period_stop': self.obj1.period_se[1],
        })
        netsvc.Logger().notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,
                                      'Periode %s' % self.obj1.period_se[1]['date_stop'])

        return res

openoffice_report('report.account.balance_sheet.excel',
    'account.account', parser=balance_sheet_excel_parse)

openoffice_report('report.account.balance_sheet.bank',
    'account.account', parser=balance_sheet_excel_parse)

openoffice_report('report.account.balance_sheet.aging.excel',
    'account.account', parser=balance_sheet_excel_parse)


