from odoo import models, fields, api
from datetime import datetime

class CustomerStatementWizard(models.TransientModel):
    _name = 'customer.statement.wizard'
    _description = 'Customer Statement of Account Wizard'

    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)
    partner_id = fields.Many2one('res.partner', string="Customer", required=True)

    def _get_soa_a_report_base_filename(self):
        """Generates a filename in the format 'Lastname_Fullname_soa_YYYY-MM-DD'."""
        self.ensure_one()
        today_date = datetime.today().strftime('%Y-%m-%d')
        full_name = self.partner_id.name or ''
        filename = f"{full_name}_SOA_{today_date}"
        return filename

    def print_customer_statement(self):
        # Initialize the list for payment details
        sales_details = [] 
        payment_details = []
        opening_details = []

        inv_objs = self.env['account.move'].search([
            ('partner_id', '=', self.partner_id.id),
            ('state', '=', 'posted'),
            ('invoice_date', '<', self.date_from),  # Invoices before the start date
            ('move_type', '=', 'out_invoice')
        ])

        payments_objs = self.env['account.payment'].search([
            ('partner_id', '=', self.partner_id.id),
            ('date', '<', self.date_from),  # Payments before the start date
            ('state', '=', 'posted')
        ])

        # Initialize the list for payment details
        sales_details = [] 
        payment_details = []

        # Initialize opening balance variables
        opening_balance_invoices = 0.0
        opening_balance_payments = 0.0

        # Calculate opening balance using invoices before start_date
        for inv in inv_objs:
            opening_balance_invoices += inv.amount_total

        # Calculate opening balance using payments before start_date
        for payment in payments_objs:
            opening_balance_payments += payment.amount

        # Opening balance is calculated as total payments - total invoices before the start date
        opening_balance = opening_balance_invoices - opening_balance_payments

        data = {
                'id': 0,
                'date': self.date_from.strftime('%m/%d/%Y'),  
                'transaction': '***Opening Balance***',
                'name': '',
                'details': '',
                'amount': opening_balance_invoices,
                'payment': opening_balance_payments,
                'balance': 0.0,               
            }  
        opening_details.append(data)

        #Transaction Summary
        inv_objs = self.env['account.move'].search([
            ('partner_id','=',self.partner_id.id),
            ('state','=','posted'),
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('move_type', '=', 'out_invoice')])
        payments_objs = self.env['account.payment'].search([
            ('partner_id','=',self.partner_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('state','=','posted')])

        for payment in payments_objs:
            details = f"{payment.name}: {payment.journal_id.name} payment for {payment.ref or ''}"
            data = {
                'id': payment.id,
                'date': payment.date.strftime('%m/%d/%Y'),  
                'transaction': 'Payment Received',
                'name': payment.name,         # Payment name
                'details': details,  # Journal name + memo
                'amount': 0.0,                # Fixed 0.0 as per the requirement
                'payment': payment.amount,    # Payment amount
                'balance': 0.0,               # Fixed 0.0 as per the requirement
            }
            payment_details.append(data)

        for inv in inv_objs:
            sale_order_name = ''
            sale_lines = inv.invoice_line_ids.mapped('sale_line_ids')
            if sale_lines:
                sale_orders = sale_lines.mapped('order_id')
                if sale_orders:
                    # If multiple sale orders are found, concatenate their names
                    sale_order_name = ', '.join(sale_orders.mapped('name'))

            details = f'{inv.name}: Invoice for {inv.ref}' if inv.ref  else (f'{inv.name}: Invoice for {sale_order_name}' if sale_order_name else inv.name)
            data = {
                'id': inv.id,
                'date': inv.invoice_date.strftime('%m/%d/%Y') if inv.invoice_date else '',  
                'transaction': 'Invoice',
                'name': inv.name,         
                'details': details,             # Sales details
                'amount': inv.amount_total,                
                'payment': 0.0,        
                'balance': 0.0,               
            }
            sales_details.append(data)

        # Output the list of dictionaries
        transactions = opening_details + payment_details + sales_details
        transactions = sorted(
            transactions,
            key=lambda x: (datetime.strptime(x['date'], '%m/%d/%Y'),x['transaction'], x['id'])
        )
        running_balance = 0.0
        total_amount = 0.0
        total_payment = 0.0
        opening_bal = opening_balance or 0.0
         

        for transaction in transactions:
            running_balance += transaction['amount'] - transaction['payment']
            transaction['balance'] = running_balance
            total_amount += transaction['amount']
            total_payment += transaction['payment']
         
        # Prepare data for the report
        data = {
            'form': {
                'partner_id': self.partner_id,
                'start_date': self.date_from.strftime('%m/%d/%Y'),  # Example value
                'end_date': self.date_to.strftime('%m/%d/%Y'),  # Example value
                'opening_balance': opening_bal,  # Example value
                'invoiced_amount': total_amount,  # Example value
                'amount_paid': total_payment,  # Example value
                'balance_due': total_amount - total_payment,  # Example value
                'transactions': transactions
            }
        }
        print(self.env['res.currency'].browse(36).name,self.env['res.currency'].browse(36).position)
        # Pass data in the context
        return self.env.ref('mkl_soa_report_a.action_variable_month_customer_statement_report').with_context(data=data).report_action(self)
