/**
 * @typedef {Object} ProductBody
 * @property {string} name
 * @property {number} brand
 * @property {number} category
 * @property {number|null} [material]
 * @property {number} numeric_size
 * @property {number|null} [letter_size]
 * @property {number} cost_price
 * @property {number} sale_price
 * @property {number} gender
 * @property {number} color
 * @property {number} season
 * @property {string} details
 * @property {File|null} [image]
 */

/**
 * @typedef {Object} ProductEndpoints
 * @property {Object} PRODUCT_CREATE_FORM
 * @property {'GET'} PRODUCT_CREATE_FORM.method
 * @property {'/productos/create/'} PRODUCT_CREATE_FORM.url
 * @property {Object} PRODUCT_CREATE
 * @property {'POST'} PRODUCT_CREATE.method
 * @property {'/productos/create/'} PRODUCT_CREATE.url
 * @property {ProductCreateBodyBuilder} PRODUCT_CREATE.body
 */

/**
 * @callback ProductCreateBodyBuilder
 * @param {string} name
 * @param {number} brand
 * @param {number} category
 * @param {number|null} [material]
 * @param {number} numeric_size
 * @param {number|null} [letter_size]
 * @param {number} cost_price
 * @param {number} sale_price 
 * @param {number} gender
 * @param {number} color
 * @param {number} season
 * @param {string} details
 * @param {File|null} [image]
 * @returns {ProductBody}
 */

/** @type {ProductEndpoints} */
const ProductEndpoints = Object.freeze({
    PRODUCT_CREATE_FORM: Object.freeze({
        method: 'GET',
        url: '/productos/create/'
    }),
    PRODUCT_CREATE: {
        method: "POST",
        url: '/productos/create/',
        /** @type {ProductCreateBodyBuilder} */
        body: (formData) => formData
    }
});

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
});

export { ProductEndpoints, SaleEndpoints };