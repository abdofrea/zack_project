# -*- coding:utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ProjectMain(models.Model):
    _name = 'project.main'
    _rec_name = 'project_name'

    project_name = fields.Char(string='أسم المشروع',required=True)

    date_of_start = fields.Date(string='تاريخ البدأ',default=fields.Datetime.today(),required=True)
    invoice_percentage = fields.Float(string='نسبة المقاول %')

    location = fields.Char(string='الموقع')
    area_archtictual = fields.Char(string="المساحة المعمارية م2")
    area_constaction = fields.Float(string="المساحة الإنشائية م2",default=0.0)
    area_constaction_long = fields.Float(string="المساحة الإنشائية متر طولي",default=0.0)
    total_area_constaction_long = fields.Float(compute='_compute_total_area_constaction_long',string="إجمالي المساحة الإنشائية")
    project_maneger = fields.Char(string='مدير المشروع')
    excpected_end_time = fields.Integer(string='مدة انتهاء المشروع بالأيام')
    contract_type=fields.Selection(selection=[('type1', 'هيكل خرساني'), ('type2', 'تشطيب'), ('type3', 'تحوير'), ('type4', 'صيانة'), ('type5', 'تسليم مفتاح')],string='نوع العقد')

    area_of_location = fields.Char(string="مساحة الموقع م2")
    project_stage = fields.Selection(selection=[('stage1', 'الهيكل'), ('stage2', 'تأسيس'), ('stage3', 'التشطيبات'), ('stage4', 'أعمال خارجية')])
    clint_name = fields.Many2one('res.partner',string="المالك")
    supervisor_engeneer = fields.Many2one('res.partner',string="المهندس المشرف")
    exepected_cost = fields.Float(string="تكلفة تقديرية", default=0.0)
    total_of_recevied_payment = fields.Float(string="إجمالي دفعات", compute="_compute_total_of_recevied_payment", default=0.0)

    total_of_contractor_deduction = fields.Float(string="تم قبضه", compute="_compute_total_of_contractor_deduction", default=0.0)
    expected_total_of_contractor_deduction = fields.Float(string="الأتعاب",compute="_compute_expected_total_of_contractor_deduction")
    defference_contractor_deduction = fields.Float(string="الأتعاب المستحقة",compute="_compute_defference_contractor_deduction")

    accumulated_value = fields.Float(string='التراكمي', compute='_compute_accumulation', default=0.0)

    total_expenses = fields.Float(string='اجمالي المصروفات', compute='_compute_total_expenses', default=0.0)
    #after_invoces = fields.Float(string="متبقي الخزينة+العهد",compute="_compute_after_invoces")
    #after_grant = fields.Float(string="متبقي الخزينة",compute="_compute_after_grant")

    total_remaining = fields.Float(string="إجمالي المتبقي",compute="_compute_total_remaining")
    total_grants = fields.Float(string="إجمالي العهد (مفتوحة)",compute="_compute_total_grants")
    total_remaining_grants = fields.Float(string='الخزينة',compute='_compute_total_remaining_grants')


    datasheet_ids = fields.One2many('project.datasheet', 'project_name', string='النوع')
    payments_ids = fields.One2many('project.datasheet.payment', 'project_name')
    grants_ids =  fields.One2many('project.grants', 'project_name')

    @api.depends('accumulated_value','total_of_contractor_deduction')
    def _compute_total_expenses(self):
        for elem in self:
            elem.total_expenses=0
            if elem.accumulated_value and elem.total_of_contractor_deduction:
                elem.total_expenses = elem.accumulated_value +elem.total_of_contractor_deduction

    #@api.depends('total_of_recevied_payment','total_of_contractor_deduction','grants_ids')
    @api.depends('total_of_contractor_deduction','grants_ids')
    def _compute_total_remaining_grants(self):
        for elem in self:
            elem.total_remaining_grants=0.0
            total_grants = 0.0
            #if elem.total_of_recevied_payment and elem.total_of_contractor_deduction and elem.grants_ids:
            if elem.grants_ids:
                for ele in elem.grants_ids:
                    if ele.state == 'closed':
                        total_grants+=ele.total_value - ele.remainder
                    elif ele.state == 'open':
                        total_grants+=ele.total_value
                elem.total_remaining_grants=elem.total_of_recevied_payment-(elem.total_of_contractor_deduction + total_grants)

    @api.depends('area_constaction','area_constaction_long')
    def _compute_total_area_constaction_long(self):
        for elem in self:
            elem.total_area_constaction_long = elem.area_constaction+elem.area_constaction_long

    @api.depends('total_of_recevied_payment', 'accumulated_value','total_of_contractor_deduction')
    def _compute_total_remaining(self):
        for elem in self:
            elem.total_remaining=0.0
            if elem.total_of_recevied_payment and elem.accumulated_value:
                elem.total_remaining = elem.total_of_recevied_payment-(elem.accumulated_value+elem.total_of_contractor_deduction)

    @api.depends('grants_ids')
    def _compute_total_grants(self):
        for elem in self:
            elem.total_grants = 0.0
            for ele in elem.grants_ids:
                if ele.state=='open':
                    elem.total_grants+=ele.total_value


    @api.depends('total_of_recevied_payment','total_of_contractor_deduction','accumulated_value')
    def _compute_after_invoces(self):
        for elem in self:
            elem.after_invoces=elem.total_of_recevied_payment - (elem.accumulated_value+elem.total_of_contractor_deduction)

    @api.depends('total_of_recevied_payment', 'grants_ids')
    def _compute_after_grant(self):
        for elem in self:
            total_grants = 0
            for ele in elem.grants_ids:
                if ele.state == 'open':
                    total_grants+=ele.total_value

            elem.after_grant = elem.total_of_recevied_payment - (total_grants + elem.total_of_contractor_deduction)

    @api.depends('payments_ids')
    def _compute_total_of_recevied_payment(self):
        for elem in self:
            if elem.payments_ids:
                for ele in elem.payments_ids:
                    if ele.state == 'confirm' and ele.payment_type == 'Paid':
                        elem.total_of_recevied_payment+=ele.total_value
                    else:
                        elem.total_of_recevied_payment+=0.0
            else:
                elem.total_of_recevied_payment = 0.0

    @api.depends('payments_ids')
    def _compute_total_of_contractor_deduction(self):
        for elem in self:
            if elem.payments_ids:
                for ele in elem.payments_ids:
                    if ele.state == 'confirm' and ele.payment_type == 'contractor_fees':
                        elem.total_of_contractor_deduction += ele.total_value
                    else:
                        elem.total_of_contractor_deduction += 0.0
            else:
                elem.total_of_contractor_deduction = 0.0

    @api.depends('datasheet_ids')
    def _compute_expected_total_of_contractor_deduction(self):
        for elem in self:
            elem.expected_total_of_contractor_deduction = 0.0
            for ele in elem.datasheet_ids:
                elem.expected_total_of_contractor_deduction+=(ele.contractor_share)

    @api.depends('expected_total_of_contractor_deduction','total_of_contractor_deduction')
    def _compute_defference_contractor_deduction(self):
        for elem in self:
            elem.defference_contractor_deduction = 0.0
            if elem.expected_total_of_contractor_deduction and elem.total_of_contractor_deduction:
                elem.defference_contractor_deduction=elem.expected_total_of_contractor_deduction-elem.total_of_contractor_deduction


    @api.depends('datasheet_ids')
    def _compute_accumulation(self):
        for elem in self:
            if elem.datasheet_ids:
                for ele in elem.datasheet_ids:
                    if ele.state == 'confirm':
                        elem.accumulated_value+=ele.total_value
                    else:
                        elem.accumulated_value+=0.0
            else:
                elem.accumulated_value = 0.0

    def filtered_datasheet_view(self):
        tree_id = self.env.ref("project_const.datasheet_tree")
        form_id = self.env.ref("project_const.datasheet_form")
        return {
            'type': 'ir.actions.act_window',
            'name': 'فاتورة',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'project.datasheet',
            'domain': [('project_name', '=', self.id)],
            'views': [(tree_id.id, 'tree'), (form_id.id, 'form')],
            'target': 'current',
        }

    def filtered_payment_view(self):
        tree_id = self.env.ref("project_const.datasheet_payment_tree")
        form_id = self.env.ref("project_const.datasheet_payment_form")
        return {
            'type': 'ir.actions.act_window',
            'name': 'دفعة',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'project.datasheet.payment',
            'domain': [('project_name', '=', self.id)],
            'views': [(tree_id.id, 'tree'), (form_id.id, 'form')],
            'target': 'current',
        }

    def filtered_grants_view(self):
        tree_id = self.env.ref("project_const.datasheet_grants_tree")
        form_id = self.env.ref("project_const.datasheet_grants_form")
        return {
            'type': 'ir.actions.act_window',
            'name': 'عهدة',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'project.grants',
            'domain': [('project_name', '=', self.id)],
            'views': [(tree_id.id, 'tree'), (form_id.id, 'form')],
            'target': 'current',
        }


class ProjectGrants(models.Model):
    _name = 'project.grants'
    _rec_name = 'complete_name'

    project_name = fields.Many2one('project.main',string='أسم المشروع',required=True)
    complete_name = fields.Char(string='اسم العهدة', compute='_compute_complete_name')
    grant_name = fields.Char(string='رقم العهدة')
    datasheet_ids = fields.One2many('project.datasheet','grant_id',string='فواتير تحت العهدة', readonly=True)
    remainder = fields.Float(string="متبقي", compute='_compute_reminder')
    grants_expence = fields.Float(string='مصروفات العهدة', compute='_compute_reminder')
    date_of_start = fields.Date(string='تاريخ الاستلام',default=fields.Datetime.today(),required=True)
    date_of_end = fields.Date(string='تاريخ القفل')
    total_value = fields.Float(string='القيمة', required=True)
    name_of_granted = fields.Char(string="اسم المستلم", required=True)
    state = fields.Selection([('closed', 'مقفلة'),('open', 'مفتوحة'),('draft', 'مسودة')],default='draft')
    additional_info = fields.Text(string='ملاحظات اضافية')

    def makeConfirm(self):
        self.state = 'closed'

    def makeCancel(self):
        self.state = 'open'

    def makeDraft(self):
        self.state = 'draft'

    @api.depends('project_name','name_of_granted','total_value','date_of_start')
    def _compute_complete_name(self):
        for elem in self:
            if elem.project_name and elem.name_of_granted and elem.total_value and elem.date_of_start:
                elem.complete_name = str(elem.date_of_start)+'_'+str(elem.project_name.project_name)+'_'+str(elem.name_of_granted)+'_'+str(int(elem.total_value))
            else:
                elem.complete_name=''

    @api.depends('total_value','datasheet_ids')
    def _compute_reminder(self):
        for elem in self:
            if elem.total_value and elem.datasheet_ids:
                total_invoice = 0
                for ele in elem.datasheet_ids:
                    if ele.state == 'confirm':
                        total_invoice+= ele.total_value
                elem.remainder = elem.total_value - total_invoice
                elem.grants_expence = total_invoice
            else:
                elem.grants_expence = 0.0
                elem.remainder = 0.0

    @api.model
    def default_get(self, fields):
        res = super(ProjectGrants, self).default_get(fields)
        res['project_name'] = self._context.get('active_id')
        return res