# -*- coding: utf-8 -*-
from odoo import tools, api, fields, models, _

from odoo.exceptions import ValidationError, UserError
from datetime import datetime

class ProjectDataSheet(models.Model):
    _name = 'project.datasheet'
    _description = 'Expenses for services and raw material'
    _rec_name = 'invoice_or_recipient'


    project_name = fields.Many2one('project.main', string='أسم المشروع',required=True)
    type_ids = fields.One2many('project.datasheet.type', 'datasheet_id', string='النوع')
    type_ids_name = fields.Char(string='النوع',compute='get_type_ids_name',store=True)
    grant_id = fields.Many2one('project.grants', string='اسم العهدة', domain="[('project_name','=',project_name),('state','=','open')]",required=True)

    sheet_number = fields.Integer(string='رقم النموذج',required=True)
    date_of_invoice = fields.Date(string='تاريخ الفاتورة',default=fields.Datetime.today(),required=True)
    invoice_percentage = fields.Float(string='نسبة المقاول %',compute='get_invoice_percentage', inverse='get_invoice_percentage_dump', store=True)
    statement = fields.Many2one('project.datasheet.statement',string='البيان')
    #total_value = fields.Float(string='القيمة',compute='_compute_total_value',default=0.0)
    total_value = fields.Float(string='القيمة', default=0.0)
    accumulated_value = fields.Float(string='التراكمي', compute='_compute_accumulation')

    target_item_ids = fields.One2many('project.target','datasheet_id', string='البند المستهدف')
    target_item = fields.Char(string='البند المستهدف', compute='_compute_target_item_char')

    distribution_item_ids = fields.One2many('project.distribution','datasheet_id', string='نسبة التوزيع')
    distribution_item = fields.Char(string='نسبة التوزيع', compute='_compute_distribution_item_char')

    project_stage = fields.Selection(selection=[('stage1', 'الهيكل'), ('stage2', 'تأسيس'), ('stage3', 'التشطيبات'), ('stage4', 'أعمال خارجية')],string="مرحلة")

    invoice_number = fields.Char(string='رقم الفاتورة')
    recipient_number = fields.Char(string='رقم الواصل')

    invoice_or_recipient = fields.Char(string='رقم الفاتورة أو الواصل',compute='_compute_invoiceorrecp')

    recipient_name = fields.Char(string='الاسم')
    contractor_share = fields.Float(string='أتعاب المقاول', compute='_compute_contractor_share',readonly=True)

    state = fields.Selection([
        ('draft', 'مسودة'),
        ('confirm', 'مؤكدة')],
        string='الحالة', tracking=True, default='draft')

    image= fields.Binary(string="صورة الفاتورة", help="ارفق صورة للفاتورة")
    additional_info = fields.Text(string='ملاحظات إضافية')

    @api.depends('project_name')
    def get_invoice_percentage(self):
        for elem in self:
            elem.invoice_percentage = 0
            if elem.project_name:
                elem.invoice_percentage = elem.project_name.invoice_percentage

    def get_invoice_percentage_dump(self):
        pass

    @api.depends('type_ids')
    def get_type_ids_name(self):
        for elem in self:
            elem.type_ids_name = ''
            k = 0
            if elem.type_ids:
                for ele in elem.type_ids:
                    k += 1
                    if k==3:
                        elem.type_ids_name+='أخرى+'
                        break
                    elem.type_ids_name += str(ele.name.name) + '+'
                elem.type_ids_name = str(elem.type_ids_name)[:-1]

    @api.depends('target_item_ids')
    def _compute_target_item_char(self):
        for elem in self:
            items = ''
            for ele in elem.target_item_ids:
                items+=str(ele.name.name)+'+'
            if items == '':
                elem.target_item=''
            else:

                items = items.split('+')
                items.remove('')
                if len(items) > 2:
                    elem.target_item = ''.join([i+'+' for i in items[:2]])+'أخرى'
                else:
                    elem.target_item = ''.join([i + '+' for i in items[:2]])[:-1]


    @api.depends('distribution_item_ids')
    def _compute_distribution_item_char(self):
        for elem in self:
            items = ''
            for ele in elem.distribution_item_ids:
                items+=str(ele.name.name)+'+'
            if items == '':
                elem.distribution_item=''
            else:
                items = items.split('+')
                items.remove('')
                if len(items) > 2:
                    elem.distribution_item = ''.join([i+'+' for i in items[:2]])+'أخرى'
                else:
                    elem.distribution_item = ''.join([i + '+' for i in items[:2]])[:-1]


    @api.depends('invoice_number','recipient_number')
    def _compute_invoiceorrecp(self):
        for elem in self:
            if elem.invoice_number:
                elem.invoice_or_recipient = elem.invoice_number
            elif elem.recipient_number:
                elem.invoice_or_recipient = elem.recipient_number
            else:
                elem.invoice_or_recipient = ''

    @api.depends('total_value','invoice_percentage')
    def _compute_contractor_share(self):
        for elem in self:
            elem.contractor_share = (elem.invoice_percentage/100) * elem.total_value

    @api.depends('type_ids')
    def _compute_total_value(self):
        for elem in self:
            if elem.type_ids:
                for ele in elem.type_ids:
                    elem.total_value+= ele.amount
            else:
                elem.total_value = 0.0

    @api.depends('total_value','project_name')
    def _compute_accumulation(self):
        for elem in self:
            try:
                accumulation_id = int(elem.id)
            except:
                try:
                    accumulation_id = int(str(elem.id).split('_')[1])
                except:
                    self.env.cr.execute("select max(id) from project_datasheet")
                    accumulation_id = self.env.cr.fetchone()[0]
                    if not accumulation_id:
                        accumulation_id = 0
            accumulation_id+=1
            accumulation_result = self.env['project.datasheet'].search([('project_name','=',int(elem.project_name.id)),('id','<',str(accumulation_id)),('state', '=', 'confirm')])
            if not accumulation_result:
                elem.accumulated_value=0
            else:
                for result in accumulation_result:
                    elem.accumulated_value += result.total_value


    @api.constrains('recipient_number','invoice_number')
    def check_one_of_recipient_or_invoice(self):
        for elem in self:
            if (elem.invoice_number and elem.recipient_number):
                raise ValidationError('Please Enter one of the following Fields (Recipient Number, Invoice Number)')

    @api.constrains('target_item_ids')
    def check_target_item_ids(self):
        for elem in self:
            summ = 0
            for ele in elem.target_item_ids:
                summ+=ele.percentage
            if summ != 100:
                raise ValidationError('please enter a valid Targets percentage')

    @api.constrains('distribution_item_ids')
    def check_distribution_item_ids(self):
        for elem in self:
            summ = 0
            for ele in elem.distribution_item_ids:
                summ += ele.percentage
            if summ != 100:
                raise ValidationError('please enter a valid Distribution percentage')

    def makeConfirm(self):
        self.state = 'confirm'

    def makeCancel(self):
        self.state = 'draft'

    @api.model
    def default_get(self, fields):
        res = super(ProjectDataSheet, self).default_get(fields)
        res['project_name'] = self._context.get('active_id')
        res['project_stage'] = self.env['project.main'].search([('id','=',res['project_name'])])[0].project_stage
        return res


    ############# Image resize
    @api.model
    def create(self, vals):
        if 'image' in vals:
            image = tools.ImageProcess(vals['image'])
            # resize uploaded image into 250 X 250
            resize_image = image.resize(720, 720)
            resize_image_b64 = resize_image.image_base64()
            vals['image'] = resize_image_b64
        obj = super(ProjectDataSheet, self).create(vals)
        return obj

    def write(self, vals):
        if 'image' in vals:
            image = tools.ImageProcess(vals['image'])
            # resize uploaded image into 250 X 250
            resize_image = image.resize(720, 720)
            resize_image_b64 = resize_image.image_base64()
            vals['image'] = resize_image_b64
        obj = super(ProjectDataSheet, self).write(vals)
        return obj
    ############# Image resize

class ProjectDataSheetStatement(models.Model):
    _name = 'project.datasheet.statement'
    _description = 'Expenses for services and raw material'
    _rec_name = 'name'
    name = fields.Char(string='إسم البيان')
    description = fields.Char(string='وصف')

class ProjectDataSheetType(models.Model):
    _name = 'project.datasheet.type'
    _description = 'Expenses for services and raw material'
    _rec_name = 'name'
    datasheet_id = fields.Many2one('project.datasheet')
    project_id = fields.Many2one('project.main',related='datasheet_id.project_name')
    invoice_or_recipient = fields.Char(string='رقم الفاتورة أو الواصل', related='datasheet_id.invoice_or_recipient')

    name = fields.Many2one('project.datasheet.type.name', string='الإسم',ondelete='cascade', required=True)
    quantity = fields.Float(string='الكمية')
    unit_of_measure = fields.Many2one('project.datasheet.type.uom',string='الوحدة')
    amount = fields.Float(string='إجمالي السعر')
    description = fields.Char(string='Description')

class ProjectDataSheetTypeUOM(models.Model):
    _name = 'project.datasheet.type.uom'
    _description = 'Project datasheet type UOM'
    name=fields.Char(string='UOM')

class ProjectDataSheetTypeNAME(models.Model):
    _name = 'project.datasheet.type.name'
    _description = 'Project datasheet type UOM'
    name=fields.Char(string='الإسم')

# class ProjectDataSheetTargetItem(models.Model):
#     _name = 'project.datasheet.targetitem'
#     _description = 'Expenses for services and raw material'
#     _rec_name = 'name'
#     name = fields.Char(string='name')
#     description = fields.Char(string='description')


