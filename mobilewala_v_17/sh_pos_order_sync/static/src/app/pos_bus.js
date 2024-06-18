/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosBus } from "@point_of_sale/app/bus/pos_bus_service";
import { _t } from "@web/core/l10n/translation";

patch(PosBus.prototype, {
    // Override
    async sh_update_order_dic(order, related_pos_order = null) {
        var order_line_list = []
        var self = this;
        // push order lines 
        for (let line of related_pos_order.data.lines) {
            order_line_list.push(line[2])
        }
        let order_id = order.id
        console.log('new order ',order_id);
        self.pos.db.pos_order_by_id[order_id] = [{
            'id': order_id,
            'name': order.name,
            'date_order': order.date_order,
            'partner_id': order.partner_id ? order.partner_id[0] : false ,
            'partner_name':  order.partner_id ? order.partner_id[1] : false,
            'pos_reference': order.pos_reference,
            'amount_total': order.amount_total,
            'state': order.state,
        }, order_line_list]
    },
    async sh_update_order(order){
        var self = this;
        var order_line_list = []
        for (let line of order.lines) {
            let dic = {
                'discount': line.discount,
                'id': line.id,
                'order_id': order.id,
                'price_subtotal': line.price_subtotal,
                'price_subtotal_incl': line.price_subtotal_incl,
                'price_unit': line.price_unit,
                'product_id': line.product_id,
                'qty': line.qty
            }
            
            order_line_list.push(dic)
        }
        self.pos.db.pos_order_by_id[ order.id] = [{
            'id':  order.id,
            'name': order.name,
            'date_order': order.date_order,
            'partner_id': order.partner_id ? order.partner_id[0] : false ,
            'partner_name':  order.partner_id ? order.partner_id[1] : false,
            'pos_reference': order.pos_reference,
            'amount_total': order.amount_total,
            'state': order.state,
        }, order_line_list]
    },
    dispatch(notif) {
        var self = this;
        super.dispatch(...arguments);
        console.log('>>notif>> ', notif);
        if (notif['payload'] && "cancel_pos_order" == notif['type']) {
            let order = notif['payload']['cancel_pos_order'];
            this.sh_update_order(order)
            if (order.user_id[0] != self.pos.user.id || order.config_id[0] != self.pos.config.id) {
                if (order.floor_id && order.floor_id[1] && order.table_id && order.table_id[1]) {
                    let order_info = (order.pos_reference + " ( " + order.floor_id[1] + " - " + order.table_id[1])

                    this.pos.sh_send_notification("Order cancel", "danger", (order_info + " ) has been cancel."))
                } else {
                    let order_info = order.pos_reference
                     
                    this.pos.sh_send_notification("Order cancel ", "danger", (order_info + " has been cancel."))
                }
            }
        }
        if (notif['payload'] && "order_paid" == notif['type']) {
            let order = notif['payload']['paid_pos_order']
            this.sh_update_order(notif['payload']['paid_pos_order'])
            if (order.user_id[0] != self.pos.user.id || order.config_id[0] != self.pos.config.id) {
                if (order.floor_id && order.floor_id[1] && order.table_id && order.table_id[1]) {
                    let order_info = (order.pos_reference + " ( " + order.floor_id[1] + " - " + order.table_id[1])

                    this.pos.sh_send_notification("Order Paid", "success", (order_info + " ) has been paid."))
                }else {
                    let order_info = order.pos_reference
                     
                    this.pos.sh_send_notification("Order Paid", "success", (order_info + " has been paid."))
                }
            }
        }
        if (notif['payload'] && "edit_pos_order" == notif['type']) {
            self.sh_update_order_dic( notif['payload'].edit_pos_order[0],notif['payload'].related_pos_order )
            
            if (notif['payload'].edit_pos_order[0].user_id[0] != self.pos.user.id || notif['payload'].edit_pos_order[0].config_id[0] != self.pos.config.id) {
                if (notif['payload'].edit_pos_order[0].floor_id && notif['payload'].edit_pos_order[0].floor_id[1] && notif['payload'].edit_pos_order[0].table_id && notif['payload'].edit_pos_order[0].table_id[1]) {
                    let order_info = (notif['payload'].edit_pos_order[0].pos_reference + " ( " + notif['payload'].edit_pos_order[0].floor_id[1] + " - " + notif['payload'].edit_pos_order[0].table_id[1])

                    if (notif['type'] === "edit_pos_order") {
                        this.pos.sh_send_notification("Order Updated", "warning", (order_info + " ) order has been edited."))
                    }
                }else {
                    let order_info = notif['payload'].edit_pos_order[0].pos_reference
                     
                    this.pos.sh_send_notification("Order Updated", "warning", (order_info + " order has been edited."))
                }
            }
        }
        if (notif['payload'] && "create_new_order" == notif['type']) {
            self.sh_update_order_dic( notif['payload'].new_pos_order[0],notif['payload'].related_pos_order )
            
            if (notif['payload'].new_pos_order[0].user_id[0] != self.pos.user.id || notif['payload'].new_pos_order[0].config_id[0] != self.pos.config.id) {
                if (notif['payload'].new_pos_order[0].floor_id && notif['payload'].new_pos_order[0].floor_id[1] && notif['payload'].new_pos_order[0].table_id && notif['payload'].new_pos_order[0].table_id[1]) {

                    let order_info = (notif['payload'].new_pos_order[0].pos_reference + " ( " + notif['payload'].new_pos_order[0].floor_id[1] + " - " + notif['payload'].new_pos_order[0].table_id[1])

                    if (notif['type'] === "create_new_order") {
                        this.pos.sh_send_notification("Order Created", "success", (order_info + " ) has been created."))
                    }
                } else {
                    let order_info = notif['payload'].new_pos_order[0].pos_reference
                    if (notif['type'] === "create_new_order") {
                        this.pos.sh_send_notification("Order Created", "success", (order_info + " has been created."))
                    } else if (notif['type'] === "edit_pos_order") {
                        this.pos.sh_send_notification("Order Updated", "warning", (order_info + " has been edited."))
                    }
                }
            }
        }
        // if (message.type === "ADYEN_LATEST_RESPONSE" && message.payload === this.pos.config.id) {
        //     this.pos
        //         .getPendingPaymentLine("adyen")
        //         .payment_method.payment_terminal.handleAdyenStatusResponse();
        // }
    },
});
