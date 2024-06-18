# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models

class PosConfig(models.Model):
    _inherit = "pos.config"

    sh_nick_name = fields.Char(string="Nick Name")
    user_type = fields.Selection(
        [('send', 'Send'), ('receive', 'Receive'), ('both', 'Send / Receive')], string="User Type ")
    sh_allow_payment = fields.Boolean(string="Allow To Pay Order")
    sh_allow_edit = fields.Boolean(string="Allow To Edit Order")
    sh_allow_cancel = fields.Boolean(string="Allow To Cancel Order")
    sh_allow_multiple_selection = fields.Boolean(
        string="Allow Multiple Selection of Validator")
    
    def get_tables_order_count(self):
        result = super(PosConfig, self).get_tables_order_count()
        
        tables = self.env['restaurant.table'].search([('floor_id.pos_config_id', 'in', self.ids)])
        domain = [('state', '=', 'draft'), ('table_id', 'in', tables.ids), ('assigned_config','=',False)]

        order_stats = self.env['pos.order'].read_group(domain, ['table_id'], 'table_id')
        orders_map = dict((s['table_id'][0], s['table_id_count']) for s in order_stats)
        result = []
        for table in tables:
            result.append({'id': table.id, 'orders': orders_map.get(table.id, 0)})
        
        return result
