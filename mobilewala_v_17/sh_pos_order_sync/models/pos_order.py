# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api

class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    @api.model
    def get_table_draft_orders(self, table_id):
        table_orders = super(PosOrder, self).get_table_draft_orders(table_id)
        sh_table_orders = []
        if table_orders and len(table_orders) > 0:
            for each_table_order in table_orders:
                if not each_table_order.get('assigned_config'):
                    sh_table_orders.append(each_table_order)
        return sh_table_orders
    
    def _get_fields_for_draft_order(self):
        fields = super(PosOrder, self)._get_fields_for_draft_order()
        fields.append('assigned_config')
        return fields

    def action_pos_order_paid(self):
        res = super(PosOrder, self).action_pos_order_paid()
        notifications = []
        assigned_config = []
        user_ids = []
        if self.assigned_config:
            for each_assigned_config in self.assigned_config:
                assigned_config.append(int(each_assigned_config.id))

            session_obj = self.env['pos.session'].search([('config_id', 'in', assigned_config), ('state', '=', 'opened')])

            for each_session_user in session_obj.user_id:
                user_ids.append(each_session_user.partner_id.id)
                sh_pos_order = self.read(['amount_total', 'date_order', 'name', 'partner_id', 'pos_reference', 'sender_config', 'state', 'lines'])
                if sh_pos_order:
                    sh_pos_order['partner_id'] = sh_pos_order.get('partner_id', False) if sh_pos_order.get('partner_id')[0] else False
                    sh_pos_order['partner_name'] = sh_pos_order.get('partner_id', False) if sh_pos_order.get('partner_id')[1] else False
                    sh_pos_order['lines'] = self.lines.read(['discount', 'order_id', 'price_subtotal', 'price_subtotal_incl', 'price_unit', 'product_id', 'qty'], load=False)
                notifications.append([each_session_user.partner_id, "order_paid", {'paid_pos_order': sh_pos_order}])
        if self.user_id.partner_id.id not in user_ids:
            order_data = self.read()[0]
            order_data['lines'] = self.lines.read(load=False) 
            notifications.append([self.user_id.partner_id, "order_paid", {'paid_pos_order': order_data }])
        self.env['bus.bus']._sendmany(notifications)
        return res

    @api.model
    def _process_order(self, order, draft, existing_order):
        if order.get('data') and not order.get('data').get('statement_ids'):
            draft = True
        order_id = super(PosOrder, self)._process_order(
            order, draft, existing_order)
        order_obj = self.search([('id', '=', order_id)])
        notifications = []
        assigned_config = []
        if existing_order:
            if existing_order.state == 'draft':
                print('\n\n\n order_obj.assigned_config ---> ', order_obj.assigned_config)
                session_obj = self.env['pos.session'].search([('state', '=', 'opened')])

                for each_session_user in session_obj.user_id:
                    notifications.append([each_session_user.partner_id, "edit_pos_order", {'edit_pos_order': order_obj.read(),  'related_pos_order': order}])
                print('\n\n\n notifications ===> ', notifications)
                notifications.append([order_obj.user_id.partner_id, "edit_pos_order", {'edit_pos_order': order_obj.read(),  'related_pos_order': order}])
        else:
            if order_obj.state != 'cancel':
                if order_obj.assigned_config:

                    for each_assigned_config in order_obj.assigned_config:

                        assigned_config.append(int(each_assigned_config.id))

                    session_obj = self.env['pos.session'].search(
                        [('config_id', 'in', assigned_config), ('state', '=', 'opened')])

                    for each_session_user in session_obj.user_id:
                        if each_session_user.id != order_obj.user_id.id:
                            notifications.append(
                                [each_session_user.partner_id, "create_new_order", {'new_pos_order': order_obj.read(), 'related_pos_order': order}])
                notifications.append(
                    [order_obj.user_id.partner_id, "create_new_order", {'new_pos_order': order_obj.read(), 'related_pos_order': order}])
        
        self.env['bus.bus']._sendmany(notifications)
        return order_id

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res['assigned_config'] = ui_order.get('assigned_config', False)
        res['sh_is_order_send'] = ui_order.get('sh_is_order_send', False)
        res['sender_config'] = ui_order.get('sender_config', False)
        return res

    @api.model
    def cancel_order(self, order_id):
        order_obj = self.search([('id', '=', order_id)])
        order_obj.write({'state': 'cancel'})
        notifications = []
        assigned_config = []
        if order_obj.assigned_config:
            for each_assigned_config in order_obj.assigned_config:

                assigned_config.append(int(each_assigned_config.id))

            session_obj = self.env['pos.session'].search(
                [('config_id', 'in', assigned_config), ('state', '=', 'opened')])

            for each_session_user in session_obj.user_id:
                if each_session_user.id != self.env.user.id:
                    notifications.append(
                                [each_session_user.partner_id, "cancel_pos_order", {'cancel_pos_order': order_obj.read()}])
        notifications.append(
            [order_obj.user_id.partner_id, "stock_update", {'cancel_pos_order': order_obj.read()}])
        self.env['bus.bus']._sendmany(notifications)
        return order_obj.id

    assigned_config = fields.Many2many("pos.config", string="Assigned Config ")
    sh_is_order_send = fields.Boolean()
    sender_config = fields.Many2one("pos.config", string="Sender Config ")
