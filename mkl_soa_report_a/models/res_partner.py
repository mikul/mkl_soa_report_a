from odoo import models, api
from datetime import datetime

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_soa_a_report_base_filename(self):
        """Generates a filename in the format 'Lastname_Fullname_soa_YYYY-MM-DD'."""
        self.ensure_one()
        today_date = datetime.today().strftime('%Y-%m-%d')
        full_name = self.name or ''
        filename = f"{full_name}_SOA_{today_date}"
        return filename

    def _get_statement_data(self, date_from=None, date_to=None):
        # Apply date filters on transactions based on date_from and date_to
        opening_balance = 1000  # Replace with actual calculation
        invoiced_amount = 2000  # Replace with actual calculation
        amount_paid = 500       # Replace with actual calculation
        balance_due = opening_balance + invoiced_amount - amount_paid

        transaction_summary = [
            # Filter transactions within the date range (replace with actual filtered transactions)
            {
                'date': datetime.today().strftime('%Y-%m-%d'),
                'transaction_type': 'Invoice',
                'details': 'Invoice #INV001',
                'amount': 1000,
                'payment': 500,
                'balance': 500,
            },
        ]

        return {
            'opening_balance': opening_balance,
            'invoiced_amount': invoiced_amount,
            'amount_paid': amount_paid,
            'balance_due': balance_due,
            'transaction_summary': transaction_summary,
        }
