import netsvc
from pxgo_openoffice_reports.openoffice_report import (OOReport,
                                                openoffice_report)

class common_report_excel(OOReport):

    def __init__(self, name, cr, uid, ids, data, context):
        super(common_report_excel, self).__init__(name, cr, uid, ids, data, context)
        netsvc.Logger().notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,
                                      'Data: %s' % self.data)
        netsvc.Logger().notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,
                                      'Context: %s' % self.context)


