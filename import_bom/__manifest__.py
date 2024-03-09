# -*- coding: utf-8 -*-
{
    'name': "Import BoM",
    'summary': """
        Import BoM with Lines
    """,
    'description': """
        This module will creating and manage the BoM with Lines functionality
    """,
    'author': "Reliution",
    'website': "https://www.reliution.com/",
    'license': 'OPL-1',
    'version': '17.0.0.1',
    'category': 'Manufacturing/Manufacturing',
    'depends': ['product', 'base', 'mrp', 'sale'],
    'data': [
        'wizard/read_csv.xml',
        'views/import_menu.xml',
        'security/ir.model.access.csv',
    ],
    'external_dependencies': {
        'python': ['pandas'],
    },
    'application': True,
    'installable': True,
    'sequence': 0
}
