import netsvc
from report import report_sxw
from account.report.account_balance import account_balance
from common_report_excel import common_report_excel
from pxgo_openoffice_reports.openoffice_report import openoffice_report

class cost_price_parse(account_balance):

    _name = 'report.account.cost_price'

    def lines1(self, form, ids=[4962], done=None):
        res = super(cost_price_parse ,self).lines(form, ids, done)
        level = res[0]['level'] - 1
        for i, r in enumerate(res):
            res[i]['level'] -= level
        res_final = res[:]
        for i, r in enumerate(res_final):
            if r['balance'] < 0:
                res_final[i]['balance_display'] = '(%s)' % self.formatLang(abs(r['balance']))
            else:
                res_final[i]['balance_display'] = '%s' % self.formatLang(r['balance'])
            res_final[i]['periods'] = []
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
            obj_self = cost_price_parse(cr=self.cr, uid=self.uid, name=self.name, context=self.context)
            netsvc.Logger().notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,
                                      'New Form: %s' % new_form)
            line = obj_self.lines1(new_form)
            lines_list.append(line)

        return zip(*lines_list)


    def lines(self, form, ids=[4962], done=None):
        self.ids = ids
        res = self.lines1(form, ids, done)
        self.periods = []
        if form['aging']:
            period_lines = self.lines_tuple(form, ids, done)
            for i, r in enumerate(res):
                res[i]['periods'] = period_lines[i]
        if form['summary']:
            sres = []
            for r in res:
                if r['type'] == 'view' or r['type'] == 'space':
                    sres.append(r)
            return sres
        return res


report_sxw.report_sxw('report.account.cost_price',
    'account.account',
    'addons/account_report_extra/report/account_cost_price.rml',
    parser=cost_price_parse, header="internal")


class cost_price_excel_parse(common_report_excel):

    _name = 'report.account.cost_price.excel'

    def __init__(self, name, cr, uid, ids, data, context):
        super(common_report_excel, self).__init__(name, cr, uid, ids, data, context)
        self.obj1 = cost_price_parse(cr=cr, uid=uid, name=name, context=context)

    def get_report_context(self):
        netsvc.Logger().notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,
                                      'Data: %s' % self.data)
        res = {}
        res.update({
            'accounts': self.obj1.lines(self.data['form']),
            'periods': self.obj1.periods,
        })
        return res

openoffice_report('report.account.cost_price.excel',
    'account.account', parser=cost_price_excel_parse)

openoffice_report('report.account.cost_price.aging.excel',
    'account.account', parser=cost_price_excel_parse)


