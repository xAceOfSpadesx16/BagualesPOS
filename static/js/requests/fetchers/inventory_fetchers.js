import { Fetcher } from "./fetcher.js";
import { InventoryEndpoints } from "../endpoints/inventories_endpoints.js";

class InventoryFetcher {
    static updateInventoryQuantity(pk, quantity, operation) {
        return Fetcher.request(InventoryEndpoints.INVENTORY_QUANTITY_UPDATE.url(pk), {
            method: InventoryEndpoints.INVENTORY_QUANTITY_UPDATE.method,
            data: InventoryEndpoints.INVENTORY_QUANTITY_UPDATE.body(quantity, operation),
            csrfToken: true
        });
    }
}

export { InventoryFetcher };