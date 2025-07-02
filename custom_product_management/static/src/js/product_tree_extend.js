/** @odoo-module */

import { ListController } from "@web/views/list/list_controller";
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';

export class ProductListController extends ListController {
    setup() {
        super.setup();
    }

    OnExportClick() {
        this.actionService.doAction({
            type: 'ir.actions.act_window',
            res_model: 'product.export.wizard',
            name: 'Export Products to Excel',
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            target: 'new',
            res_id: false,
        });
    }
}

registry.category("views").add("product_export_button_tree", {
    ...listView,
    Controller: ProductListController,
    buttonTemplate: "product_export.ListView.Buttons",
});