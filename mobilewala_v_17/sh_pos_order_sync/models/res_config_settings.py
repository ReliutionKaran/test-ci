# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    pos_sh_nick_name = fields.Char(related='pos_config_id.sh_nick_name',string="Nick Name", readonly=False)
    pos_user_type = fields.Selection(
        [('send', 'Send'), ('receive', 'Receive'), ('both', 'Send / Receive')],related='pos_config_id.user_type', string="User Type ", readonly=False)
    pos_sh_allow_payment = fields.Boolean(related='pos_config_id.sh_allow_payment',string="Allow To Pay Order", readonly=False)
    pos_sh_allow_edit = fields.Boolean(related='pos_config_id.sh_allow_edit',string="Allow To Edit Order", readonly=False)
    pos_sh_allow_cancel = fields.Boolean(related='pos_config_id.sh_allow_cancel',string="Allow To Cancel Order", readonly=False)
    pos_sh_allow_multiple_selection = fields.Boolean(related='pos_config_id.sh_allow_multiple_selection',
        string="Allow Multiple Selection of Validator", readonly=False)
