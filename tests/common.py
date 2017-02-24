# -*- coding: utf-8 -*-

from openerp.tests import common

KARMA = {
    'ask': 5, 'ans': 10,
    'com_own': 5, 'com_all': 10,
    'com_conv_all': 50,
    'upv': 5, 'dwv': 10,
    'edit_own': 10, 'edit_all': 20,
    'close_own': 10, 'close_all': 20,
    'unlink_own': 10, 'unlink_all': 20,
    'gen_que_new': 1, 'gen_que_upv': 5, 'gen_que_dwv': -10,
    'gen_ans_upv': 10, 'gen_ans_dwv': -20,
}


class TestKidsCommon(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestKidsCommon, cls).setUpClass()

        Forum = cls.env['forum.forum']
        Post = cls.env['forum.post']

        # Test users
        TestUsersEnv = cls.env['res.users'].with_context({'no_reset_password': True})
        group_employee_id = cls.env.ref('base.group_user').id
        group_portal_id = cls.env.ref('base.group_portal').id
        group_public_id = cls.env.ref('base.group_public').id
        cls.user_employee = TestUsersEnv.create({
            'firstname': 'Helge',
            'lastname': 'Schneider',
            'login': 'hesche',
            'alias_name': 'helge',
            'email': 'lweber@gmx.ch',
            'groups_id': [(6, 0, [group_employee_id])]
        })


