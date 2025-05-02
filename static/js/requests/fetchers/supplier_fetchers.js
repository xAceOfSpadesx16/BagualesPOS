import { Fetcher } from "./fetcher.js";

import { SupplierEndpoints } from "../endpoints/suppliers_endpoints.js";

class SupplierFetcher {

    static getCreateForm() {
        return Fetcher.request(SupplierEndpoints.SUPPLIER_CREATE_FORM.url, {
            method: SupplierEndpoints.SUPPLIER_CREATE_FORM.method
        });
    };

    static createSupplier(formData) {
        return Fetcher.request(SupplierEndpoints.SUPPLIER_CREATE.url, {
            method: SupplierEndpoints.SUPPLIER_CREATE.method,
            data: SupplierEndpoints.SUPPLIER_CREATE.body(formData),
            csrfToken: true
        });
    };

    static getUpdateForm(pk) {
        return Fetcher.request(SupplierEndpoints.SUPPLIER_UPDATE_FORM.url(pk), {
            method: SupplierEndpoints.SUPPLIER_UPDATE_FORM.method
        });
    };

    static updateSupplier(pk, formData) {
        return Fetcher.request(SupplierEndpoints.SUPPLIER_UPDATE.url(pk), {
            method: SupplierEndpoints.SUPPLIER_UPDATE.method,
            data: SupplierEndpoints.SUPPLIER_UPDATE.body(formData),
            csrfToken: true
        });
    };

    static deleteSupplier(pk) {
        return Fetcher.request(SupplierEndpoints.SUPPLIER_DELETE.url(pk), {
            method: SupplierEndpoints.SUPPLIER_DELETE.method,
            csrfToken: true
        });
    };

}

export { SupplierFetcher };