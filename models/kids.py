# -*- coding: utf-8 -*-
from openerp.exceptions import except_orm

# from datetime import datetime
# import uuid
# from werkzeug.exceptions import Forbidden

#import logging
# import openerp
# 
# from openerp import api, tools
# from openerp import SUPERUSER_ID
# from openerp.exceptions import Warning
# from openerp.osv import osv, fields
# from openerp.tools import html2plaintext
# from openerp.tools.translate import _

#_logger = logging.getLogger(__name__)

#Ab Odoo 9 steht UserError in openerp.exceptions bereit. Dann kann folgende Klasse gelöscht werden (und muss "UserError" importiert werden)

class UserError(except_orm):
    def __init__(self, msg):
        super(UserError, self).__init__(msg)