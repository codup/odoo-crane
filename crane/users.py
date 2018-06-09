# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2014-2018 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, fields, models

class Users(models.Model):
    _inherit = 'res.users'

    signature_image = fields.Binary("Signature Image")
