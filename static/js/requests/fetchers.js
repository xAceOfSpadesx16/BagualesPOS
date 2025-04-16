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

        const headers = new Headers();
        let body = data;

        if (data && !(data instanceof FormData)) {
            headers.append('Content-Type', 'application/json');
            body = JSON.stringify(data);
        }

        if (csrfToken) {
            headers.append('X-CSRFToken', getCookie('csrftoken'));
        }

        const options = {
            method,
            headers,
            ...(body && { body })
        };
        return fetch(url, options)
            .catch(error => {
                console.error("Error en la petición:", error);
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

    static closeSaleDetails(saleId) {
        return this.request(
            SaleEndpoints.CLOSE_SALE_DETAILS.url(saleId),
            {
                method: SaleEndpoints.CLOSE_SALE_DETAILS.method,
            }
        );
    };

    static closeSale(saleId, clientId) {
        return this.request(
            SaleEndpoints.CLOSE_SALE.url(saleId),
            {
                method: SaleEndpoints.CLOSE_SALE.method,
                data: SaleEndpoints.CLOSE_SALE.body(clientId),
                csrfToken: true,
            }
        );
    };

    static updateClient(saleId, clientId) {
        return this.request(
            SaleEndpoints.UPDATE_CLIENT.url(saleId),
            {
                method: SaleEndpoints.UPDATE_CLIENT.method,
                data: SaleEndpoints.UPDATE_CLIENT.body(clientId),
                csrfToken: true,
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

    static productCreate(data) {
        return this.request(
            ProductEndpoints.PRODUCT_CREATE.url,
            {
                method: ProductEndpoints.PRODUCT_CREATE.method,
                data: ProductEndpoints.PRODUCT_CREATE.body(data),
                csrfToken: true
            }
        );
    }

    static productUpdateForm(id) {
        return this.request(
            ProductEndpoints.PRODUCT_UPDATE_FORM.url(id),
            {
                method: ProductEndpoints.PRODUCT_UPDATE_FORM.method,
            }
        );
    }
    static productUpdate(id, data) {
        return this.request(
            ProductEndpoints.PRODUCT_UPDATE.url(id),
            {
                method: ProductEndpoints.PRODUCT_UPDATE.method,
                data: ProductEndpoints.PRODUCT_UPDATE.body(data),
                csrfToken: true
            }
        );
    }
}





export { SalesFetcher, ProductsFetcher };