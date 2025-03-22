const ProductEndpoints = Object.freeze({
    PRODUCT_CREATE_FORM: Object.freeze({
        method: 'GET',
        url: '/productos/create/'
    })
});

const SaleEndpoints = Object.freeze(
    {
        SALE_DETAILS_CREATE: Object.freeze({
            method: 'POST',
            url: '/ventas/create-detail/',
            /**
             * 
             * @param {number} product_id 
             * @param {number} quantity 
             * @returns {{ product_id: number, quantity: number }}
             */
            body: (product_id, quantity) => ({ 'product': product_id, 'quantity': quantity })
        }),
        SALE_DETAILS_DELETE: Object.freeze({
            method: 'DELETE',
            url: (pk) => `/ventas/delete-detail/${pk}/`,
        }),
        SALE_DETAILS_QUANTITY_UPDATE: Object.freeze({
            method: 'PATCH',
            /**
             * 
             * @param {number} pk 
             * @returns {string}
             */
            url: (pk) => `/ventas/update-detail-quantity/${pk}/`,
            /**
             * 
             * @param {number} quantity 
             * @returns {{ quantity: number }}
             */
            body: (quantity) => ({ 'quantity': quantity })
        }),
    }
)

export { ProductEndpoints, SaleEndpoints }