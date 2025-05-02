import { Fetcher } from './fetcher.js';
import { ProductEndpoints } from "../endpoints/products_endpoints.js";



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
    static productDelete(id) {
        return this.request(
            ProductEndpoints.PRODUCT_DELETE.url(id),
            {
                method: ProductEndpoints.PRODUCT_DELETE.method,
                csrfToken: true
            }
        );
    }
}


export { ProductsFetcher }