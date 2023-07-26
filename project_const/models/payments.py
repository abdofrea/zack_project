# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime



class ProjectDataSheetPayments(models.Model):
    _name = 'project.datasheet.payment'
    _description = 'Payment for services and raw material'
    _rec_name = "invoice_number"

    project_name = fields.Many2one('project.main', string='أسم المشروع',required=True)
    date_of_invoice = fields.Date(string='تاريخ الدفعة',default=fields.Datetime.today(),required=True)
    total_value = fields.Float(string='القيمة',default=0.0)
    payment_type = fields.Selection(selection=([('contractor_fees', 'أتعاب مقاول'), ('Paid', 'قبض من زبون')]), string='نوع الدفعة')
    payment_method = fields.Selection(selection=([('cash', 'كاش'), ('check', 'شيك'),('from_owner','مدفوعات من المالك'), ('other','أخرى')]), string='طريقة الدفع')
    invoice_number = fields.Char(string='رقم الفاتورة أو الواصل')
    recipient_name = fields.Char(string='إسم المستلم')
    #recipient_from = fields.Char(string='أستلمت من')
    #payment_number = fields.Char(string='دفعة رقم')
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('confirm', 'مؤكدة')],
        string='الحالة', tracking=True, default='draft')

    image= fields.Binary(string="صورة الفاتورة", help="ارفق صورة للفاتورة")
    additional_info = fields.Text(string='ملاحظات إضافية')

    def print_report(self):
        report_data = {
            'user_id': self.create_uid.name,
            'project_name': self.project_name.project_name,
            'clint_name': self.project_name.clint_name.name,
            'date_of_invoice': str(self.date_of_invoice),
            'total_value': self.total_value,
            'payment_method': self.payment_method,
            'recipient_name': self.recipient_name,
            'additional_info': self.additional_info or ''
        }

        return self.env.ref('project_const.payment_receive_report').report_action(self, data=report_data)

    def makeConfirm(self):
        self.state = 'confirm'

    def makeCancel(self):
        self.state = 'draft'

    @api.model
    def default_get(self, fields):
        res = super(ProjectDataSheetPayments, self).default_get(fields)
        res['project_name'] = self._context.get('active_id')
        return res



