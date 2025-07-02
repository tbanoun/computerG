/** @odoo-module */

import { KanbanController } from "@web/views/kanban/kanban_controller";
import { registry } from '@web/core/registry';
import { kanbanView } from '@web/views/kanban/kanban_view';

export class ProductKanbanController extends KanbanController {
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

registry.category("views").add("product_export_button_kanban", {
    ...kanbanView,
    Controller: ProductKanbanController,
    buttonTemplate: "product_export.KanbanView.Buttons",
});