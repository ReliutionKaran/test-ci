/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { _t } from "@web/core/l10n/translation";

patch(PosStore.prototype, {
    //@override
    constructor(attr, options) {
        super.constructor(attr, options);
        this.save = false;
        this.is_new = false
    },
    async _processData(loadedData) {
        await super._processData(loadedData)
        if(loadedData['sh_config_data']){
            this.db.all_configs(loadedData['sh_config_data']);
        }
    },
    add_new_order(){
        if(!this.is_new){
            return super.add_new_order()
        }else{
            return false
        }
    },
});