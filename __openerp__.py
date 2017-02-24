# -*- coding: utf-8 -*-
{
    'name': "kids",

    'summary': """
        Module for childcare institutions in Switzerland""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Backplane GmbH",
    'website': "http://www.backplane.ch",
    'application': True,
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Customer Relationship Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        #'multi_company',
        'l10n_ch',
        #'account_accountant',
        'account_followup',             # Managment der Zahlungserinnerungen, Installiert account (über Dependenciy "account_voucher") mit
        'account_analytic_analysis',   
        'partner_street_number',
        'partner_relations',
        'partner_firstname',
        'partner_contact_gender',
        'partner_contact_birthdate'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/kidsbasedata.yml',
        'views/res_partner.xml',
        'data/kidsinitdata.yml'        
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'post_init_hook': 'set_swiss_chart_of_accounts_for_all_init_data_companies',         
}