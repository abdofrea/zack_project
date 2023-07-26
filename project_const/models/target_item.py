# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime

class ProjectTarget(models.Model):
    _name = 'project.target'

    name = fields.Many2one('project.target.item',string='البند المستهدف', required=True)
    datasheet_id = fields.Many2one('project.datasheet', store=True)

    invoice_or_recipient = fields.Char(string='رقم الفاتورة أو الواصل', related='datasheet_id.invoice_or_recipient', store=True)
    project_id = fields.Many2one('project.main',related='datasheet_id.project_name',string='أسم المشروع', store=True)

    statement = fields.Many2one('project.datasheet.statement',related='datasheet_id.statement',string='البيان', store=True)
    date_of_invoice = fields.Date(related='datasheet_id.date_of_invoice',string='تاريخ الفاتورة', store=True)
    sheet_number = fields.Integer(related='datasheet_id.sheet_number',string='رقم النموذج', store=True)


    percentage = fields.Float(string='نسبة التوزيع', default=100.0)
    invoice_percentage = fields.Float(string='القيمة من الفاتورة',compute='_compute_percentage_value',readonly=True, store=True)

    @api.depends('datasheet_id.total_value','percentage')
    def _compute_percentage_value(self):
        for elem in self:
            if elem.percentage and elem.datasheet_id:
                elem.invoice_percentage = (elem.percentage/100) * elem.datasheet_id.total_value
            else:
                elem.invoice_percentage = 0.0

    @api.model
    def default_get(self, fields):
        res = super(ProjectTarget, self).default_get(fields)
        res['datasheet_id'] = self._context.get('active_id')
        return res


class ProjectTargetItem(models.Model):
    _name = 'project.target.item'

    name = fields.Char(string='أسم البند')
    description = fields.Text(string='وصف')