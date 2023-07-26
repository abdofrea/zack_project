# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Customers Project Construction',
    'category': 'Extra',
    'summary': 'Customers Project Construction',
    'sequence': 10,
    'version': '1.0',
    'description': """Customers Project Construction Module for Mohammed Elbahry,
     Made By Abdulwahed Freaa """,
    'depends': [],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/project_main.xml',
        'views/view.xml',
        'views/report_view.xml',
        'views/view_type_name.xml',
        'views/payments_view.xml',
        'views/grants_view.xml',
        'views/report_view1.xml',
        'views/target_item.xml',
        'views/distribution.xml',
        'views/statment_view.xml',
        'views/project_datasheet_type_views.xml',
        'reports/report.xml',
        'reports/report1.xml',
        'reports/payment_slip.xml',
    ],
    'installable': True,
    'application': True,
}

# 'security/ir.model.access.csv',
#         'data/data.xml',
#         'views/costumers.xml',
#         'views/transaction.xml'
#'reports/report_detail.xml'
#'reports/report_attendance.xml',
#'views/employee.xml',
# 'views/adminX.xml',
# 'views/check_INS_OUTS.xml',
