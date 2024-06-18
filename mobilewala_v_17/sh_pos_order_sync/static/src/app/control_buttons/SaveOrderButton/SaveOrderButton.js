  /** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class SaveOrderButton extends Component {
    static template = "sh_pos_order_sync.SaveOrderButton";
    setup() {
        super.setup();
        this.pos = usePos();
    }
    async onClick(){
        var self = this;
        if (self.pos.get_order().is_edit) {
            var order = self.pos.get_order()
            self.pos.push_single_order(order);
            await self.pos.removeOrder(order);
            await self.pos.db.remove_order(order)
            await self.pos.add_new_order();
            $(".save_button").removeClass("show_save_button");
        }
    }
}

ProductScreen.addControlButton({
    component: SaveOrderButton,
    condition: function () {
        return true
    },
})
