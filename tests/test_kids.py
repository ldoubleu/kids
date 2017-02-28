# -*- coding: utf-8 -*-

#from .common import KARMA, TestKidsCommon
#from openerp.exceptions import Warning, AccessError
#from ..models.kids import UserError

# class TestKids(TestKidsCommon):
# 
#     #@mute_logger('openerp.addons.base.ir.ir_model', 'openerp.models')
#     def test_ask(self):
#         Post = self.env['forum.post']
# 
#         # Public user asks a question: not allowed
#         with self.assertRaises(UserError):
#             Post.sudo(self.user_public).create({
#                 'name': " Question ?",
#                 'forum_id': self.forum.id,
#             })
# 
#         # Portal user asks a question with tags: ok if enough karma
#         self.user_portal.karma = KARMA['ask']
#         Post.sudo(self.user_portal).create({
#             'name': " Q0",
#             'forum_id': self.forum.id,
#             'tag_ids': [(0, 0, {'name': 'Tag0', 'forum_id': self.forum.id})]
#         })
# 
#         self.assertEqual(self.user_portal.karma, KARMA['ask'] + KARMA['gen_que_new'], 'website_forum: wrong karma generation when asking question')
# 
#  
#     def test_close_post_own(self):
#         self.post.create_uid.karma = KARMA['close_own']
#         self.post.close(None)

