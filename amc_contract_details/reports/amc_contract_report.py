from odoo import api, models, _


class AmcContractReport(models.AbstractModel):
    _name = 'report.amc_contract_details.amc_contract_report'
    _description = 'AMC Contract Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['amc.contract'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'amc.contract',
            'docs': docs,
        }
