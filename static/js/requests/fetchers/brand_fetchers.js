import { Fetcher } from "./fetcher.js";

import { BrandEndpoints } from "../endpoints/brands_endpoints.js";

class BrandFetcher extends Fetcher {
    static getCreateForm() {
        return this.request(BrandEndpoints.BRAND_CREATE_FORM.url, {
            method: BrandEndpoints.BRAND_CREATE_FORM.method,
        });
    };

    static brandCreate(data) {
        return this.request(BrandEndpoints.BRAND_CREATE.url, {
            method: BrandEndpoints.BRAND_CREATE.method,
            data: BrandEndpoints.BRAND_CREATE.body(data),
            csrfToken: true
        });
    };

    static brandUpdateForm(id) {
        return this.request(BrandEndpoints.BRAND_UPDATE_FORM.url(id), {
            method: BrandEndpoints.BRAND_UPDATE_FORM.method
        });
    };

    static brandUpdate(id, data) {
        return this.request(BrandEndpoints.BRAND_UPDATE.url(id), {
            method: BrandEndpoints.BRAND_UPDATE.method,
            data: BrandEndpoints.BRAND_UPDATE.body(data),
            csrfToken: true
        });
    };

    static brandDelete(id) {
        return this.request(BrandEndpoints.BRAND_DELETE.url(id), {
            method: BrandEndpoints.BRAND_DELETE.method,
            csrfToken: true
        });
    };

}

export { BrandFetcher };