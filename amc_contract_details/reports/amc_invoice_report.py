from odoo import api, models, _


class AmcInvoiceReport(models.AbstractModel):
    _name = 'report.amc_contract_details.amc_invoice_report'
    _description = 'Amc Invoice Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['amc.contract'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'amc.contract',
            'docs': docs,
        }
