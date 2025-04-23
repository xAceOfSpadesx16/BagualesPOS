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
        url: '/administracion/productos/create/'
    }),
    PRODUCT_CREATE: Object.freeze({
        method: "POST",
        url: '/administracion/productos/create/',
        /** @type {ProductCreateBodyBuilder} */
        body: (formData) => formData
    }),
    PRODUCT_UPDATE_FORM: Object.freeze({
        method: 'GET',
        url: (pk) => `/administracion/productos/update/${pk}/`
    }),
    PRODUCT_UPDATE: Object.freeze({
        method: "POST",
        url: (pk) => `/administracion/productos/update/${pk}/`,
        /** @type {ProductCreateBodyBuilder} */
        body: (formData) => formData
    }),
    PRODUCT_DELETE: Object.freeze({
        method: 'DELETE',
        url: (pk) => `/administracion/productos/delete/${pk}/`
    })
});

export { ProductEndpoints };