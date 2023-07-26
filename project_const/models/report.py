# -*- coding:utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class ReportWizard(models.TransientModel):
    _name = "project.wizard.report"

    project_id = fields.Many2one('project.main', string='أسم المشروع', required=True)
    from_sheet_number = fields.Char(string="من النوذج رقم")
    to_sheet_number = fields.Char(string="الى النموذج رقم")
    from_date = fields.Date(string="من تاريخ")
    to_date = fields.Date(string="الى تاريخ")
    def get_report_action(self):
        #'ids': self.ids,
        data = {'model': self._name,  'project_id': int(self.project_id.id),'project_name':self.project_id.project_name,
                'location': self.project_id.location,
                'owner_name': self.project_id.clint_name.name,
                'to_sheet_number':self.to_sheet_number, 'from_sheet_number':self.from_sheet_number, 'from_date':self.from_date, 'to_date':self.to_date}
        return self.env.ref('project_const.report_project_datasheet').with_context(landscape=True).report_action(self, data=data)



class ReportTemplate(models.AbstractModel):
    _name = 'report.project_const.report_project_datasheet_template'

    def getElemOfSearch(self,data):
        search_list = [('project_name','=',data['project_id']),('state', '=', 'confirm')]
        for elem in data.keys():
            if elem == 'to_date' and data[elem] != False:
                search_list.append(('date_of_invoice','<=',data['to_date']))
            elif elem == 'from_date' and data[elem] != False:
                search_list.append(('date_of_invoice','>=',data['from_date']))
            elif elem == 'to_sheet_number' and data[elem] != False:
                search_list.append(('sheet_number','<=',data['to_sheet_number']))
            elif elem == 'from_sheet_number' and data[elem] != False:
                search_list.append(('sheet_number','>=',data['from_sheet_number']))
        return search_list

    @api.model
    def _get_report_values(self, docids, data=None):
        search_list = self.getElemOfSearch(data)
        search_result = self.env['project.datasheet'].search(search_list)

        docs = []
        imgs=[]
        i=0
        accumalative_value=0
        for rows in search_result:
            i+=1

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
            accumalative_value+=rows.total_value
            docs.append({
                'num':i,
                'sheet_number':rows.sheet_number,
                'date_of_invoice':rows.date_of_invoice,
                'total_value':round(rows.total_value,2),
                'accumulated_value':round(accumalative_value,2),
                #'accumulated_value':round(rows.accumulated_value,2),
                'statement':rows.statement.name,
                'type_i':type_i,
                'target_item':rows.target_item,
                'invoice_recipient_number':invoice_recipient_number,
                #'invoice_number':rows.invoice_number,
                #'recipient_number':rows.recipient_number,
                'recipient_name':rows.recipient_name,
                'contractor_share':round(rows.contractor_share,2),
                'additional_info':rows.additional_info,
                'project_stage': str(rows.project_stage).replace('stage1', 'الهيكل').replace('stage2','تأسيس').replace('stage3', 'التشطيبات').replace('stage4', 'أعمال خارجية')
            })
            if rows.image:
                imgs.append(rows.image)

        # 'doc_ids': data['ids'],
        return {'doc_model': data['model'],
                'owner_name': data['owner_name'],
                'location': data['location'],
                'date_time': (datetime.now() + timedelta(hours=2)).strftime("%Y/%m/%d-%H:%M:%S"),
                'docs': docs, 'imgs':imgs,'project_name':data['project_name']}