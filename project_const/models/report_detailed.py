# -*- coding:utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class ReportWizard(models.TransientModel):
    _name = "project.wizard1.report"
    project_id = fields.Many2one('project.main', string='أسم المشروع', required=True)
    # from_sheet_number = fields.Char(string="من النوذج رقم")
    # to_sheet_number = fields.Char(string="الى النموذج رقم")
    # from_date = fields.Date(string="من تاريخ")
    # to_date = fields.Date(string="الى تاريخ")
    def get_report_action(self):
        #'ids': self.ids,
        #data = {'model': self._name, 'ids': self.ids, 'project_id': int(self.project_id.id),'project_name':self.project_id.name, 'to_sheet_number':self.to_sheet_number, 'from_sheet_number':self.from_sheet_number, 'from_date':self.from_date, 'to_date':self.to_date}
        data = {'model': self._name,  'project_id': int(self.project_id.id),
                'project_name': self.project_id.project_name,
                'owner_name':self.project_id.clint_name.name,
                'location': self.project_id.location,
                'total_of_recevied_payment': self.project_id.total_of_recevied_payment,
                'total_remaining': self.project_id.total_remaining,
                'total_remaining_grants': self.project_id.total_remaining_grants,
                'total_expenses':self.project_id.total_expenses,
                'defference_contractor_deduction':self.project_id.defference_contractor_deduction}
        res = self.env.ref('project_const.report1_project_datasheet').with_context(landscape=True).report_action(self, data=data)

        return res

class ReportTemplate(models.AbstractModel):
    _name = 'report.project_const.report_project_datasheet_template1'

    def getElemOfSearch(self,data):
        search_list = [('project_name','=',data['project_id']),('state', '=', 'confirm')]
        return search_list

    @api.model
    def _get_report_values(self, docids, data=None):
        search_list = self.getElemOfSearch(data)
        search_result = self.env['project.datasheet'].search(search_list)
        docs = []
        imgs=[]
        accum_vals = 0
        for rows in search_result:
            ########### Type name section
            type_i = ''
            k=0
            for elem in rows.type_ids:
                k+=1
                if k==3:
                    type_i+='أخرى+'
                    break
                type_i+=str(elem.name.name)+'+'
            type_i = type_i[:-1]
            #################################
            if rows.invoice_number and not rows.recipient_number:
                invoice_recipient_number = 'فاتورة - '+str(rows.invoice_number)
            elif not rows.invoice_number and rows.recipient_number:
                invoice_recipient_number = 'واصل - '+str(rows.recipient_number)
            else:
                invoice_recipient_number=''
            accum_vals+=rows.total_value
            docs.append({
                'sheet_number':str(rows.sheet_number),
                'date_of_invoice':str(rows.date_of_invoice)+'1',
                'total_value':round(rows.total_value,2),
                'statement':rows.statement.name,
                'type_i':type_i,
                'target_item':rows.target_item,
                'invoice_recipient_number':invoice_recipient_number,
                # 'invoice_number':rows.invoice_number,
                # 'recipient_number':rows.recipient_number,
                'recipient_name':rows.recipient_name,
                'contractor_share':round(rows.contractor_share,2),
                'project_stage' :  str(rows.project_stage).replace('stage1', 'الهيكل').replace('stage2', 'تأسيس').replace('stage3', 'التشطيبات').replace('stage4', 'أعمال خارجية')
            })
            if rows.image:
                imgs.append(rows.image)

        search_result = self.env['project.datasheet.payment'].search([('project_name','=',data['project_id']),('state', '=', 'confirm')])
        for rows in search_result:
            if rows.invoice_number:
                invoice_recipient_number = 'فاتورة - '+str(rows.invoice_number)
            else:
                invoice_recipient_number='*'
            docs.append({
                'sheet_number': '/',
                'date_of_invoice': str(rows.date_of_invoice) + '0',
                'total_value': rows.total_value,
                'statement': rows.payment_type,
                'type_i': '*',
                'target_item': "*",
                'invoice_recipient_number': invoice_recipient_number,
                # 'invoice_number': rows.invoice_number,
                #'recipient_number': "*",
                'recipient_name': rows.recipient_name,
                'contractor_share': "*",
                'project_stage':"/"
            })
            if rows.image:
                imgs.append(rows.image)

        docs.sort(key=lambda x:x['date_of_invoice'])

        # 'doc_ids': data['ids'],
        return {
                'doc_model': data['model'],
                'docs': docs,
                'imgs':imgs,
                'project_name':data['project_name'],
                'owner_name':data['owner_name'],
                'location':data['location'],
                'date_time':(datetime.now()+timedelta(hours=2)).strftime("%Y/%m/%d-%H:%M:%S"),
                'total_of_recevied_payment':data['total_of_recevied_payment'],'accum_vals':round(accum_vals,2),'total_remaining':data['total_remaining'],'total_remaining_grants':data['total_remaining_grants'],'defference_contractor_deduction':data['defference_contractor_deduction'],'total_expenses':data['total_expenses']}