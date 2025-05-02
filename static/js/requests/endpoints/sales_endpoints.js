/**
 * @typedef {Object} SaleDetailBody
 * @property {number} product
 * @property {number} quantity
 */

/**
 * @typedef {Object} SaleEndpoints
 * @property {Object} SALE_DETAILS_CREATE
 * @property {'POST'} SALE_DETAILS_CREATE.method
 * @property {string} SALE_DETAILS_CREATE.url
 * @property {SaleDetailCreateBodyBuilder} SALE_DETAILS_CREATE.body
 * 
 * @property {Object} SALE_DETAILS_DELETE
 * @property {'DELETE'} SALE_DETAILS_DELETE.method
 * @property {SaleDetailDeleteUrlBuilder} SALE_DETAILS_DELETE.url
 * 
 * @property {Object} SALE_DETAILS_QUANTITY_UPDATE
 * @property {'PATCH'} SALE_DETAILS_QUANTITY_UPDATE.method
 * @property {SaleDetailUpdateUrlBuilder} SALE_DETAILS_QUANTITY_UPDATE.url
 * @property {SaleDetailUpdateBodyBuilder} SALE_DETAILS_QUANTITY_UPDATE.body
 */

/**
 * @callback SaleDetailCreateBodyBuilder
 * @param {number} product
 * @param {number} quantity
 * @returns {SaleDetailBody}
 */

/**
 * @callback SaleDetailDeleteUrlBuilder
 * @param {number} pk
 * @returns {string}
 */

/**
 * @callback SaleDetailUpdateUrlBuilder
 * @param {number} pk
 * @returns {string}
 */

/**
 * @callback SaleDetailUpdateBodyBuilder
 * @param {number} quantity
 * @returns {{quantity: number}}
 */

/** @type {SaleEndpoints} */
const SaleEndpoints = Object.freeze({
    SALE_DETAILS_CREATE: Object.freeze({
        method: 'POST',
        url: '/ventas/create-detail/',
        /** @type {SaleDetailCreateBodyBuilder} */
        body: (product, quantity) => ({ product, quantity })
    }),
    SALE_DETAILS_DELETE: Object.freeze({
        method: 'DELETE',
        /** @type {SaleDetailDeleteUrlBuilder} */
        url: (pk) => `/ventas/delete-detail/${pk}/`,
    }),
    SALE_DETAILS_QUANTITY_UPDATE: Object.freeze({
        method: 'PATCH',
        /** @type {SaleDetailUpdateUrlBuilder} */
        url: (pk) => `/ventas/update-detail-quantity/${pk}/`,
        /** @type {SaleDetailUpdateBodyBuilder} */
        body: (quantity) => ({ quantity })
    }),
    CLOSE_SALE_DETAILS: Object.freeze({
        method: 'GET',
        url: (pk) => `/ventas/close/${pk}/`
    }),
    CLOSE_SALE: Object.freeze({
        method: 'PATCH',
        url: (pk) => `/ventas/close/${pk}/`,
        body: (payMethod) => ({ pay_method: payMethod })
    }),
    // UPDATE_CLIENT
    UPDATE_CLIENT: Object.freeze({
        method: 'PATCH',
        url: (pk) => `/ventas/update-client/${pk}/`,
        body: (clientId) => ({ client: clientId })
    })
});

export { SaleEndpoints }