/** @odoo-module */
import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class TemplateReceiverPopup extends AbstractAwaitablePopup {
    static template = "sh_pos_order_sync.TemplateReceiverPopup";
    setup() {
        super.setup();
        this.pos = usePos();
    }
    async confirm() {
        this.props.resolve({ confirmed: true, payload: await this.getPayload() });
        var self = this;
        var assigned_config = [];
        for(let i=0;i<$("tr.highlight").length;i++){
            let line = $("tr.highlight")[i]
            assigned_config.push(parseInt(line.getAttribute("data-value")));
        }
        self.pos.get_order().is_order_send = true;
        await self.pos.db.add_order(self.pos.get_order().export_as_JSON())
        await self.pos.get_order().set_assigned_config(assigned_config);
        await self.pos.push_single_order(self.pos.get_order());
        await self.pos.removeOrder(self.pos.get_order());
        await self.pos.add_new_order();
        self.cancel()
    }
    async onClickSessionRow( event ) {
        var self = this;

        if (!self.pos.config.sh_allow_multiple_selection) {
            $(".session_row.highlight").removeClass("highlight");
        }
        if ($(event.currentTarget).hasClass("highlight")) {
            $(event.currentTarget).removeClass("highlight");
        } else {
            $(event.currentTarget).addClass("highlight");
        }
        if (!self.pos.config.sh_allow_multiple_selection) {
            self.pos.get_order().is_order_send = true;
            await self.pos.get_order().set_assigned_config([$(event.currentTarget).data("value")]);
            await self.pos.db.add_order(self.pos.get_order().export_as_JSON())
            await self.pos.push_orders(self.pos.get_order());
            await self.pos.removeOrder(self.pos.get_order());
            await self.pos.add_new_order()
            self.cancel()
        }
    }
}
  