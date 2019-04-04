# -*- coding: utf-8 -*-
{
    'name': "Advanced Mrp",

    'summary': """
        Advanced Mrp""",

    'description': """
        Advanced Mrp
    """,

    'author': "AthmanZiri",
    'website': "https://www.innovus.co.ke",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/mrp_bom.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'installable': True,
    'application': True,
    'sequence': 4,
}