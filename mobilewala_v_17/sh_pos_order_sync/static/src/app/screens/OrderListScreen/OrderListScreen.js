/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { OrderListScreen } from "@sh_pos_order_list/apps/screen/order_list_screen/order_list_screen";
import { _t } from "@web/core/l10n/translation";
import { Packlotline } from "@point_of_sale/app/store/models";


patch(OrderListScreen.prototype, {
    async cancel_pos_order(event) {
        var self = this;
        var order_id = $(event.currentTarget.closest("tr")).attr("data-id");
        console.log('order_id',this);

        await self.env.services.orm.call("pos.order", "cancel_order", [[parseInt(order_id)]])
    },
    pay_pos_order(event) {
        var self = this;
        var order_id = $(event.currentTarget.closest("tr")).attr("data-id");
        var order_data = self.pos.db.pos_order_by_id[order_id];

        var current_order = self.pos.get_order();
        if (self.pos.get_order() && self.pos.get_order().get_orderlines() && self.pos.get_order().get_orderlines().length > 0) {
            var orderlines = self.pos.get_order().get_orderlines();
            [...orderlines].map(async (line) => await current_order.removeOrderline(line))
        }

        $(".save_button").addClass("show_save_button");
        order_data[1].forEach((each_order_line) => {
            var product = self.pos.db.get_product_by_id(each_order_line.product_id);
            if (product) {
                current_order.add_product(product, {
                    quantity: each_order_line.qty,
                    price: each_order_line.price_unit,
                    discount: each_order_line.discount,
                });
                if (each_order_line.lot_details) {
                    each_order_line.lot_details.forEach((each_lot) => {
                        var newPackLotLine = new Packlotline({}, { order_line: current_order.get_selected_orderline() });
                        newPackLotLine.lot_name = each_lot;
                        current_order.get_selected_orderline().pack_lot_lines.add(newPackLotLine);
                    });
                }
            }
        });
        if (order_data[0].partner_id) {
            current_order.set_partner(self.pos.db.get_partner_by_id(order_data[0].partner_id));
        }
        current_order.is_edit = true;
        current_order.is_pay_order = true;

        current_order.name = order_data[0].pos_reference;
        current_order.assigned_config = order_data[0].assigned_config;
        if (order_data[0].sender_config) {
            current_order.sender_config = order_data[0].sender_config;
        }
        this.pos.showScreen('PaymentScreen')
    },
    edit_pos_order(event) {
        var self = this;
        var order_id = $(event.currentTarget.closest("tr")).attr("data-id");
        var order_data = self.pos.db.pos_order_by_id[order_id];

        var current_order = self.pos.get_order();
        if (self.pos.get_order() && self.pos.get_order().get_orderlines() && self.pos.get_order().get_orderlines().length > 0) {
            var orderlines = self.pos.get_order().get_orderlines();
            [...orderlines].map(async (line) => await current_order.removeOrderline(line))
        }
        $(".save_button").addClass("show_save_button");
        order_data[1].forEach((each_order_line) => {
            var product = self.pos.db.get_product_by_id(each_order_line.product_id);
            if (product) {
                current_order.add_product(product, {
                    quantity: each_order_line.qty,
                    price: each_order_line.price_unit,
                    discount: each_order_line.discount,
                    customerNote: each_order_line.customer_note || null,
                });
                if (each_order_line.lot_details) {
                    each_order_line.lot_details.forEach((each_lot) => {
                        var newPackLotLine = new Packlotline({}, { order_line: current_order.get_selected_orderline() });
                        newPackLotLine.lot_name = each_lot;
                        current_order.get_selected_orderline().pack_lot_lines.add(newPackLotLine);
                    });
                }
            }
        });
        if (order_data[0].partner_id) {
            current_order.set_partner(self.pos.db.get_partner_by_id(order_data[0].partner_id));
        }
        current_order.is_edit = true;
        current_order.name = order_data[0].pos_reference;
        current_order.assigned_config = order_data[0].assigned_config;
        if (order_data.sender_config && order_data[0].sender_config[0]) {
            current_order.sender_config = order_data[0].sender_config[0];
        }
        this.pos.showScreen('ProductScreen')
    }
})