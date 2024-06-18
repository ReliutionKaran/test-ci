/** @odoo-module */

import { Order, Orderline} from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    constructor(attr, options) {
        super.constructor(attr, options);
        this.is_order_send = false
        this.is_reprint = false;
    },
    init_from_JSON(json) {
        this.is_edit = json.is_edit || false;
        super.init_from_JSON(json);
    },
    export_as_JSON() {
        var json = super.export_as_JSON()
        json.assigned_config = this.get_assigned_config() || null;
        json.sh_is_order_send = this.is_order_send || false;
        json.sender_config = this.sender_config || this.pos.config.id
        return json;
    },
    set_assigned_config(assigned_config) {
        this.assigned_config = assigned_config;
    },
    get_assigned_config() {
        return this.assigned_config;
    },
    export_for_printing() {
        var self = this;
        var orders = super.export_for_printing()
        var new_val = {
            assigned_config: this.get_assigned_config() || false,
        };
        if (self.is_reprint && self.payment_data) {
            new_val["paymentlines"] = [];
            new_val["change"] = self.amount_return;
            _.each(self.payment_data, function (each_payment_data) {
                if (each_payment_data.amount && Math.abs(each_payment_data.amount) != self.amount_return) {
                    var payment_data = { amount: each_payment_data.amount, name: each_payment_data.payment_method_id[1] };
                    new_val["paymentlines"].push(payment_data);
                }
            });
        }
        $.extend(orders, new_val);
        return orders;
    },
    set_orderline_options(orderline, options) {
        super.set_orderline_options(orderline, options)
        if(options.customerNote !== undefined){
            orderline.set_customer_note(options.customerNote);
        }
    },
});
