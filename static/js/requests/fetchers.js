import { getCookie } from "../utils.js";
import { ProductEndpoints, SaleEndpoints } from "./endpoints.js";

class Fetcher {
    /**
     * Método centralizado para hacer fetch.
     * @param {string} url - La URL del endpoint.
     * @param {Object} options - Opciones de la petición.
     * @param {string} [options.method='GET'] - Método HTTP.
     * @param {Object|null} [options.data=null] - Datos a enviar.
     * @param {boolean} [options.csrfToken=false] - Token CSRF.
     * @returns {Promise} - Se retorna una promesa.
     */
    static request(url, { method = 'GET', data = null, csrfToken = false } = {}) {
        const headers = {
            'Content-Type': 'application/json',
        };

        if (csrfToken) {
            headers['X-CSRFToken'] = getCookie('csrftoken');
        }

        const options = {
            method,
            headers,
            ...(data && { body: JSON.stringify(data) })
        };

        return fetch(url, options)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw {
                            status: response.status,
                            message: err.message || err.detail
                        };
                    });
                }
                const contentType = response.headers.get('Content-Type');

                if (contentType && contentType.includes('application/json')) {
                    return response.json();
                } else if (contentType && contentType.includes('text/html')) {
                    return response.text();
                } else {
                    throw new Error('Unsupported response format');
                }
            })
            .catch(error => {
                console.error(error);
                throw error;
            });
    }
}

class SalesFetcher extends Fetcher {

    /**
     * Crea un nuevo detalle de venta.
     * @typedef {Object} SaleDetailCreateResponse
     * @property {Object} product - Datos del producto.
     * @property {string} product.name - Nombre del producto.
     * @property {number} quantity - Cantidad vendida.
     * @property {string} sale_price - Precio unitario con formato.
     * @property {string} total_price - Precio total con formato.
     * @property {string} total_sale_amount - Monto total de la venta tras agregar el detalle.
     * @property {number} id - ID del detalle de venta creado.
     *
     * 
     * @param {number} productId - Id de Producto.
     * @param {number} quantity - Cantidad a vender.
     * @returns {Promise<SaleDetailCreateResponse>}
     */
    static createSaleDetail(productId, quantity) {
        return this.request(
            SaleEndpoints.SALE_DETAILS_CREATE.url,
            {
                method: SaleEndpoints.SALE_DETAILS_CREATE.method,
                data: SaleEndpoints.SALE_DETAILS_CREATE.body(productId, quantity),
                csrfToken: true,
            }
        );
    };

    /**
     * Elimina un detalle de venta.
     * @typedef {Object} SaleDetailDeleteResponse
     * @property {number} total_sale_amount - Monto total de la venta tras eliminar el detalle.
     * 
     * @param {number} detailId - Id de Venta.
     * @returns {Promise<SaleDetailDeleteResponse>}
     */
    static deleteSaleDetail(detailId) {
        return this.request(
            SaleEndpoints.SALE_DETAILS_DELETE.url(detailId),
            {
                method: SaleEndpoints.SALE_DETAILS_DELETE.method,
                csrfToken: true
            }
        );
    };

    /**
     * Actualiza la cantidad de un detalle de venta.
     * @typedef {Object} SaleDetailUpdateQuantityResponse
     * @property {number} quantity - Nueva cantidad vendida.
     * @property {string} sale_price - Precio unitario con formato.
     * @property {string} total_price - Precio total con formato.
     * @property {string} total_sale_amount - Monto total de la venta con formato.
     * 
     * 
     * @param {number} detailId 
     * @param {number} quantity 
     * @returns {Promise<SaleDetailUpdateQuantityResponse>}
     */

    static updateSaleDetailQuantity(detailId, quantity) {
        return this.request(
            SaleEndpoints.SALE_DETAILS_QUANTITY_UPDATE.url(detailId),
            {
                method: SaleEndpoints.SALE_DETAILS_QUANTITY_UPDATE.method,
                data: SaleEndpoints.SALE_DETAILS_QUANTITY_UPDATE.body(quantity),
                csrfToken: true
            }
        );
    };
}

class ProductsFetcher extends Fetcher {

    /**
     * Obtiene el formulario para crear un producto.
     * 
     * @returns {Promise}
     */
    static productFormGET() {
        return this.request(
            ProductEndpoints.PRODUCT_CREATE_FORM.url,
            {
                method: ProductEndpoints.PRODUCT_CREATE_FORM.method,
            }
        );
    }
}





export { SalesFetcher, ProductsFetcher };