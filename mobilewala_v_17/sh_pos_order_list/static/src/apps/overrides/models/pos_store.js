/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { _t } from "@web/core/l10n/translation";


patch(PosStore.prototype, {
    async _processData(loadedData) {
        await super._processData(...arguments);
        if(loadedData['pos_order_by_id']){
            this.db.pos_order_by_id = loadedData['pos_order_by_id']
        }else{
            this.db.pos_order_by_id = {}
        }
        if(loadedData['pos_order_line_by_id']){
            this.db.pos_order_line_by_id = loadedData['pos_order_line_by_id']
        }else{
            this.db.pos_order_line_by_id = {}
        }
    },
    push_single_order(order) {
        var self = this;
        const result = super.push_single_order(order)
        var date = new Date()
        var date_str =  date.getFullYear() +'-'+  date.getMonth() +'-'+ date.getDate() +'- '+ date.getHours()+':'+ date.getMinutes()+ ':'+ date.getSeconds();
        if (result){
            var order_line_list = []
            for (let line of order.get_orderlines()){
                order_line_list.push(line.export_as_JSON())
            }
            result.then(function (Orders) {
                if ( Orders ){
                    let order_id = Orders[0].id
                    self.db.pos_order_by_id[order_id] = [{
                        'id': order_id, 
                        'name': Orders[0].name  , 
                        'date_order':  date_str, 
                        'partner_id':  order.get_partner() ? order.get_partner().id : false , 
                        'partner_name':  order.get_partner() ? order.get_partner().name : false , 
                        'pos_reference': order.name, 
                        'amount_total': order.get_total_with_tax() , 
                        'state': Orders[0].account_move ? 'invoiced' : 'paid', 
                    }, order_line_list]
                }
            })
        }
        return result
    }
})