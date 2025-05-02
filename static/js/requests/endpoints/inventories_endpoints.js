const InventoryEndpoints = Object.freeze({
    INVENTORY_QUANTITY_UPDATE: Object.freeze({
        method: 'POST',
        url: (pk) => `/inventario/update/${pk}/`,
        body: (quantity, operation) => ({ quantity, operation })
    })
})

export { InventoryEndpoints }