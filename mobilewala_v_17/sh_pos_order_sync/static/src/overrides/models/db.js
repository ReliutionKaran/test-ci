/** @odoo-module */

import { PosDB } from "@point_of_sale/app/store/db";
import { patch } from "@web/core/utils/patch";

patch(PosDB.prototype, {
    all_configs: function (all_config) {
        this.all_config = [];
        this.config_by_id = {};
        for (var i = 0, len = all_config.length; i < len; i++) {
            var each_config = all_config[i];
            this.all_config.push(each_config);
            this.config_by_id[each_config.id] = each_config;
        }
    },
})