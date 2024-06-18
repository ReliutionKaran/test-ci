/** @odoo-module */

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { registry } from "@web/core/registry";

export class ShReceiptScreen extends ReceiptScreen {
    static template = "ShReceiptScreen";
    static components = { OrderReceipt };
    confirm() {
        this.pos.showScreen('ProductScreen')
    }
    /**
     * @override
     */
    async printReceipt() {
        var self = this;
        this.buttonPrintReceipt.el.className = "fa fa-fw fa-spin fa-circle-o-notch";
        const isPrinted = await this.printer.print(
            OrderReceipt,
            {
                data: self.props.order.export_for_printing(),
                formatCurrency: this.env.utils.formatCurrency,
            },
            { webPrintFallback: true }
        );

        if (isPrinted) {
            this.props.order._printed = true;
        }

        if (this.buttonPrintReceipt.el) {
            this.buttonPrintReceipt.el.className = "fa fa-print";
        }
        this.currentOrder._printed = false;
    }
    
    get order_data(){
        var order = this.props.order.export_for_printing()
        var date = new Date(this.props.selected_order.date_order+' PM UTC');
        order['date']  =  date.toLocaleString()
        return order
    }
    get isBill() {
        return true;
    }
}

registry.category("pos_screens").add("ShReceiptScreen", ShReceiptScreen);
