from odoo import api, models, _


class CalloutContractReport(models.AbstractModel):
    _name = 'report.amc_contract_details.callout_contract_report'
    _description = 'Callout Contract Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('selffffffffffffffffffffffffffff', self)
        docs = self.env['amc.contract'].browse(docids[0])
        print('selffffffffffffffffffffffffffff', docs)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'amc.contract',
            'docs': docs,
        }


