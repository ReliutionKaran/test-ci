/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { _t } from "@web/core/l10n/translation";


patch(PosStore.prototype, {
    sh_send_notification( title, type, message ) {
        if (this.env.services.notification) {
            this.env.services.notification.add( message, {
                // type: "info",
                // type: "warning",
                // type: "danger",
                type: type,
                title: _t(title),
                sticky: true 
            });
        }
    },
})