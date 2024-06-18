/* @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { TemplateReceiverPopup } from "@sh_pos_order_sync/app/Popups/TemplateReceiverPopup/TemplateReceiverPopup";

export class SendOrderButton extends Component {
    static template = "sh_pos_order_sync.SendOrderButton";
    setup() {
        super.setup();
        this.report = useService("report");
        this.pos = usePos();
        this.popup = useService("popup");
    }
    async onClick() {
        var self = this;
        if (this.pos.get_order().get_selected_orderline()) {
             self.pos.get_order().is_order_send = true;
             debugger;
            var assigned_config = [self.env.services.pos.config.id];
            await self.pos.db.add_order(self.pos.get_order().export_as_JSON())
            await self.pos.get_order().set_assigned_config(assigned_config);
            await self.pos.push_single_order(self.pos.get_order());
            await self.pos.removeOrder(self.pos.get_order());
            await self.pos.add_new_order();
//            const all_session = await self.pos.orm.silent.call("pos.session", "search_session");
//            if (all_session) {
//                self.pos.all_session = all_session;
//            }
//            let { confirmed } = await this.popup.add(TemplateReceiverPopup);
//            if (confirmed) {
//            } else {
//                return;
//            }
        } else {
            alert("Please select the product !");
        }
    }

}

ProductScreen.addControlButton({
    component: SendOrderButton,
    condition: function () {
        return this.pos.config.user_type == "send" || this.pos.config.user_type == "both";
    },
});