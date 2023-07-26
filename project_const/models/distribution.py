# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime

class ProjectTarget(models.Model):
    _name = 'project.distribution'

    name = fields.Many2one('project.distribution.item',string='الدور', required=True)
    datasheet_id = fields.Many2one('project.datasheet')

    invoice_or_recipient = fields.Char(string='رقم الفاتورة أو الواصل', related='datasheet_id.invoice_or_recipient')
    project_id = fields.Many2one('project.main',related='datasheet_id.project_name',string='أسم المشروع')
    percentage = fields.Float(string='نسبة التوزيع', default=100.0)
    invoice_percentage = fields.Float(string='القيمة من الفاتورة',compute='_compute_percentage_value',readonly=True)

    @api.depends('datasheet_id','percentage')
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
    _name = 'project.distribution.item'

    name = fields.Char(string='أسم الدور')
    description = fields.Text(string='وصف')