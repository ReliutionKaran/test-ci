{
    'name': 'Invoice Changes',
    'summary': 'Customer invoice',
    'version': '17.1',
    'sequence': '1',
    'depends': [
        'point_of_sale',
        'product',
        'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'reports/inherit_invoice_report.xml',
        'views/res_company_form_view.xml',
        'views/master_product_menu.xml',
        'views/inherit_product_template.xml',
        'views/inherit_account_move_form.xml',

    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'rel_invoice_changes/static/src/**/*',
        ]}
}
