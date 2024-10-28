# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'My Project',
    'version': '1.1',
    'sequence': 100,
    'summary': 'Organize and plan your projects',
    'description': "",
    'data': [
        'security/my_project_security.xml',
        'security/ir.model.access.csv',
        'security/record_rule.xml',
        'views/my_project_views.xml',
    ],
    'demo': ['data/project_demo.xml'],
    'qweb': ['static/src/xml/project_templates.xml'],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
