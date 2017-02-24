# -*- coding: utf-8 -*-
import numbers

from openerp import models, fields, api, exceptions
from openerp.osv.expression import is_leaf, OR, AND, FALSE_LEAF, TRUE_LEAF, TRUE_DOMAIN
from ..models.kids import UserError
from openerp.exceptions import Warning, AccessError

# res.partner.category,name



class ResPartner(models.Model):
    """Erweiterungen des res.partner modells für kids"""
    _inherit = "res.partner"

    # env['res.partner'].browse(18).relation_all_ids.filtered(lambda r: r.relation_id.type_id == env.ref('kids.kids_Beziehungsart_ElternKind')).mapped('other_partner_id')
    
#     kinder_ids = fields.One2many(
#         string='Kinder',
#         compute='_compute_kinder',
#         # store=False)  # the default
#         #search='_search_is_Eltern'
#         )
#     kinder_ids = fields.One2many(
#         'res.partner',  # related model
#         'partner_id',  # field for "this" on related model
#         'zugehörige Kinder (falls vorhanden)')


    kinder_ids = fields.One2many(
        comodel_name='res.partner',
#         relation='res_partner_relation',
#         column1='left_partner_id',
#         column2='right_partner_id',
        string='Kinder des aktuellen Partners',
        compute='_calc_kinder_ids',
        inverse='_write_kinder_ids',
        auto_join=True,
        # selectable=False,
        copy=False,
    )

    is_Eltern = fields.Boolean(
        string='Eltern?',
        compute='_compute_is_Eltern',
        # store=False)  # the default
        search='_search_is_Eltern'
        )
 

    search_kinder = fields.Many2one(
            comodel_name='res.partner',
            domain=lambda self: ['&', ('relation_all_ids.record_type', '=', 'b'), ('relation_all_ids.relation_id.type_id.id', '=', self.env.ref('kids.kids_Beziehungsart_ElternKind').id)],
            compute=lambda self: None,
            # search='_search_kinder',
            string='Kinder'
        )  


    @api.depends('category_id')
    def _compute_is_Eltern(self):
        for partner in self:
            partner.is_Eltern = not partner.is_company and self.env.ref('kids.res_partner_category_Eltern').id  in partner.category_id.mapped('id')

    def _search_is_Eltern(self, operator, value):
        return [('name', operator, value)]


    @api.multi
    @api.depends('relation_all_ids')
    def _calc_kinder_ids(self):
        if self.env.context.get('PreventWriteKinderIdsLoop'):
            return
        for partner in self:
            partner.kinder_ids = self.env['res.partner.relation'].search(['&', ('left_partner_id', '=', partner.id), ('type_id.id', '=', self.env.ref('kids.kids_Beziehungsart_ElternKind').id)]).mapped('right_partner_id')

#     @api.multi
#     def write(self,values):
#         super(ResPartner,self).write(values)

    
    def _write_kinder_ids(self):
        if self.env.context.get('PreventWriteKinderIdsLoop'):
            return
        k_ids = []
        for kind in self.kinder_ids:
            if isinstance(kind.id, models.NewId):
                # wir haben ein hinzugefügtes Kind
                kind = kind.create({'firstname': kind.firstname,
                                                       'birthdate_date':kind.birthdate_date,
                                                       'gender': kind.gender})
                kind_rel_vals = {'left_partner_id': self.id,
                                 'right_partner_id': kind.id,
                                 'type_id': self.env.ref('kids.kids_Beziehungsart_ElternKind').id}
#                                'create_uid': self.env.uid,
#                                'write_uid': self.env.uid}
                new_rel = self.env['res.partner.relation'].create(kind_rel_vals)
                k_ids +=[new_rel.id]
            else:
#                 kind = kind.update({'firstname': kind.firstname,
#                                     'birthdate_date':kind.birthdate_date,
#                                     'gender': kind.gender})
                k_ids+=[kind.id]
#                 partner_kind_relations += ({'left_partner_id': self.id,
#                                                 'right_partner_id': kind.id,
#                                                 'type_id': self.env.ref('kids.kids_Beziehungsart_ElternKind'),
#                                                 'create_uid': self.env.uid,
#                                                 'write_uid': self.env.uid})
        self = self.with_context(PreventWriteKinderIdsLoop=True)
        self.kinder_ids=k_ids
        #self = self.with_context(PreventWriteKinderIdsLoop=False)
                 
     
    
    # @api.model
    # def _search_relation_leftside_type_id(self, operator, value):
    
    # _search_relation_type_id von partner-contact/partner_relation/res_partner.py überschreiben, damit bei der Suche nur noch das eine Ende
    # der Beziehung gefunden wird 
    @api.model
    def _search_relation_type_id(self, operator, value):
        """Search partners with a relation type based on the left-side (the original search found both ends of partners)."""
        result = []
        SUPPORTED_OPERATORS = (
            '=',
            '!=',
            'like',
            'not like',
            'ilike',
            'not ilike',
            'in',
            'not in',
        )
        if operator not in SUPPORTED_OPERATORS:
            raise exceptions.ValidationError(
                _('Unsupported search operator "%s"') % operator)
        type_selection_model = self.env['res.partner.relation.type.selection']
        relation_type_selection = []
        if operator == '=' and isinstance(value, numbers.Integral):
            relation_type_selection += type_selection_model.browse(value)
        elif operator == '!=' and isinstance(value, numbers.Integral):
            relation_type_selection = type_selection_model.search([
                ('id', operator, value),
            ])
        else:
#             relation_type_selection = type_selection_model.search([
#                 '|',
#                 ('type_id.name', operator, value),
#                 ('type_id.name_inverse', operator, value),
#             ])
            relation_type_selection = type_selection_model.search([
                ('name', operator, value),
            ])
        if not relation_type_selection:
            result = [FALSE_LEAF]
        for relation_type in relation_type_selection:
            result = OR([
                result,
                [
                    ('relation_all_ids.type_selection_id.id', '=',
                     relation_type.id),
                ],
            ])
        return result             
    

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Injiziere Kinder-Filter bei Namenssuche, falls die Suche auf dem "search_kinder"-Feld stattfindet (s.o bei der Feld-Definition)"""
#         if FLAG_FOR_KINDERDOMAIN in args:
#             kinder_domain = ['&', ('relation_all_ids.relation_id.type_id.id', '=', self.env.ref('kids.kids_Beziehungsart_ElternKind').id),
#                                   ('relation_all_ids.record_type', '=', 'b')]
#             #Pseudo-Domain wieder entfernen. War nur als Flag in Domain-Eigenschaft des "search_kinder"-Feldes gesetzt
#             args.pop(args.index(FLAG_FOR_KINDERDOMAIN))       
#             args = args + kinder_domain
        return super(ResPartner, self).name_search(name, args=args, operator=operator, limit=limit)
        
        


# #       for partner in self:
# #           partner.kinder_ids = partner.relation_all_ids.filtered(lambda r: r.relation_id.type_id == env.ref('kids.kids_Beziehungsart_ElternKind')).mapped('other_partner_id')
#         kinder_filter = [('relation_all_ids.relation_id.type_id.id', '=', self.env.ref('kids.kids_Beziehungsart_ElternKind').id)]
#         kinder_filter = AND([kinder_filter, [('relation_all_ids.record_type', '=', "b")]])  # "b" meint den linken Teil der Beziehung, d.h. Kind
#         if value:
#             result = AND([kinder_filter, [('name', operator, value)]])
#         # env['res.partner.relation'].search([('type_id.id','=',env.ref('kids.kids_Beziehungsart_ElternKind').id),('right_partner_id.name','ilike','ha')]).right_partner_id.name
#         return [('name', operator, value)]
