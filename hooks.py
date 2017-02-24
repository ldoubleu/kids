# -*- encoding: utf-8 -*-
##############################################################################
#
#    Partner Address on Map module for Odoo
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import SUPERUSER_ID
from openerp.api import Environment
import time
import logging

SWISS_DEFAULT_SALE_TAX = 0.08
SWISS_DEFAULT_PURCHASE_TAX = 0.08
SWISS_CHART_DEFAULT_CODE_DIGITS = 4

_logger = logging.getLogger(__name__)

def set_swiss_chart_of_accounts_for_all_init_data_companies(cr, pool):
    """ install a swiss chart of accounts for the installed swiss companies (in data) """
    

    # 1. Versuch zum Auslesen von externen ID's:
    #swiss_chart_template_id = pool['ir.model.data'].search_read(cr, SUPERUSER_ID, [('name','=','l10nch_chart_template'),('module','=','l10n_ch')],  limit=1)[0]['res_id']
    #swiss_currency_id = pool['ir.model.data'].search_read(cr, SUPERUSER_ID, [('name','=','CHF'),('module','=','base')], limit=1)[0]['res_id']
    
    # 2. Versuch zum Auslesen von externen ID's:
    #swiss_currency_id = pool['ir.model.data'].get_object_reference(cr, SUPERUSER_ID, 'base', 'CHF')[1]
    #swiss_chart_template_id = pool['ir.model.data'].get_object_reference(cr, SUPERUSER_ID, 'l10n_ch', 'l10nch_chart_template')[1]
    
    # so ist es am leserlichsten:
    swiss_currency_id = Environment(cr, SUPERUSER_ID, {}).ref('base.CHF').id
    swiss_chart_template_id = Environment(cr, SUPERUSER_ID, {}).ref('l10n_ch.l10nch_chart_template').id

    # dieses Pattern sieht man oft.. 
    #with Environment.manage():
    #    env = Environment(cr, SUPERUSER_ID, {})
    #    comp = env["res.company"].search([...])
        

    # Installation Schweizer Kontenplan für alle Kids-Unternehmen
    # inspiriert vom Installer des Moduls account: odoo/addons/account/account.py:execute() (wird von account_followup -> account -> voucher -> account installiert)
 
    # Kontenplan-Standardwerte setzen    
    tax_templ_obj = pool.get('account.tax.template')
    complete_tax_set = False
    sale_tax = SWISS_DEFAULT_SALE_TAX
    purchase_tax = SWISS_DEFAULT_PURCHASE_TAX
    sale_tax_rate = 15
    purchase_tax_rate = 15
    code_digits = SWISS_CHART_DEFAULT_CODE_DIGITS
    
    # Werte (Steuerwerte, Anzahl Kontenplanziffern) aus dem Schweizer Kontenplan lesen (l10n_ch.l10nch_chart_template - über die Abhängigkeit "l10n_ch" in __openerp__ installiert)
    if swiss_chart_template_id:
        # update complete_tax_set, sale_tax and purchase_tax
        chart_template = pool.get('account.chart.template').browse(cr, SUPERUSER_ID, swiss_chart_template_id)
        if chart_template.complete_tax_set:
            complete_tax_set = chart_template.complete_tax_set
            # default tax is given by the lowest sequence. For same sequence we will take the latest created as it will be the case for tax created while isntalling the generic chart of account
            sale_tax_ids = tax_templ_obj.search(cr, SUPERUSER_ID,
                [("chart_template_id", "=", swiss_chart_template_id), ('type_tax_use', 'in', ('sale','all'))],
                order="sequence, id desc")
            purchase_tax_ids = tax_templ_obj.search(cr, SUPERUSER_ID,
                [("chart_template_id", "=", swiss_chart_template_id), ('type_tax_use', 'in', ('purchase','all'))],
                order="sequence, id desc")
            sale_tax = sale_tax_ids and sale_tax_ids[0] or False
            purchase_tax = purchase_tax_ids and purchase_tax_ids[0] or False
            code_digits = chart_template.code_digits if chart_template.code_digits else SWISS_CHART_DEFAULT_CODE_DIGITS
            
    
    # Kids-Unternehmen ermitteln
    kids_company_ids = pool['ir.model.data'].search_read(cr, SUPERUSER_ID, [('name','=like','kids_res_company%'), ('model','=','res.company'), ('module','=','kids')], ['name', 'res_id'])
    kids_company_ids.insert(0,{'id': 1, 'name': 'base.main_company', 'res_id': 1})  # odoo -main-company ID am Anfang einfügen
    
    # durch alle Kids-Unternehmen gehen (alte Version). Hier waren die Unternehmen in diesm Post-Installations-Script hardgecoded. Besser: siehe unten
#     for company_ref in [{'module': 'base', 'refid': 'main_partner'},
#                         {'module': 'kids', 'refid': 'kids_res_company_1'},
#                         {'module': 'kids', 'refid': 'kids_res_company_2'}]:
#         company_id = pool['ir.model.data'].get_object_reference(cr, SUPERUSER_ID, company_ref['module'], company_ref['refid'])[1]            
    
    # durch alle Kids-Unternehmen gehen    
    for company in kids_company_ids:
        
        #Installation Geschäftsjahr (account.fiscalyear)
        #Datei: odoo/addons/account/installer.py. 
        _logger.debug(u"Aufsetzen Geschäftsjahr für Kids Stamm-Unternehmen '%s' mit ID: %s", company["name"], company["res_id"])
        wizard = pool.get('account.installer')
        wizard_id = wizard.create(cr, SUPERUSER_ID, {
            'date_start': time.strftime('%Y-01-01'),
            'date_stop': time.strftime('%Y-12-31'),
            'period': 'month',
            'company_id': company["res_id"],
            'has_default_company': True,
            'charts': 'configurable'
        }, context={})
        wizard.execute(cr, SUPERUSER_ID, [wizard_id], context={})        
        
        
        #Installation Kontoplan
        #Datei: odoo/addons/account/account.py
        _logger.debug(u"Aufsetzen Kontenplan für Kids Stamm-Unternehmen '%s' mit ID: %s", company["name"], company["res_id"])
        wizard = pool.get('wizard.multi.charts.accounts')
        wizard_id = wizard.create(cr, SUPERUSER_ID, {
            'company_id': company["res_id"],
            'chart_template_id': swiss_chart_template_id,
            'code_digits': code_digits,
            'sale_tax': sale_tax,
            'purchase_tax': purchase_tax,
            'sale_tax_rate': sale_tax_rate,
            'purchase_tax_rate': purchase_tax_rate,
            'complete_tax_set': complete_tax_set,
            'currency_id': swiss_currency_id,
        }, context={})
        wizard.execute(cr, SUPERUSER_ID, [wizard_id], context={})    
     
    #Installationsassistenten "Configure Accounting Data" und "Set Your Accounting Options" deaktivieren
    #(wurden bei der Installation von Modul "account" installiert
    
#     pool['ir.actions.todo'].search([('action_id.name','in',['Configure Accounting Data',
#                                                             'Set Your Accounting Options',
#                                                             'Open Sale Menu'])]
#                                   ).write({'state': 'done'})
    
    
    return
