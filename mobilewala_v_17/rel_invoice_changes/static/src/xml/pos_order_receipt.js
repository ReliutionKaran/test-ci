/** @odoo-module **/

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
   export_for_printing() {
      return {
         ...super.export_for_printing(...arguments),
         current_order: this.pos.get_order()
      };
   }
});
