import { Fetcher } from "./fetcher.js";

import { ColorEndpoints } from "../endpoints/colors_endpoints.js";

class ColorFetcher extends Fetcher {

    static getCreateForm() {
        return this.request(ColorEndpoints.COLOR_CREATE_FORM.url, {
            method: ColorEndpoints.COLOR_CREATE_FORM.method,
        });
    };

    static createColor(formData) {
        return this.request(ColorEndpoints.COLOR_CREATE.url, {
            method: ColorEndpoints.COLOR_CREATE.method,
            data: formData,
            csrfToken: true
        });
    };

    static colorUpdateForm(pk) {
        return this.request(ColorEndpoints.COLOR_UPDATE_FORM.url(pk), {
            method: ColorEndpoints.COLOR_UPDATE_FORM.method,
        });
    };

    static updateColor(pk, formData) {
        return this.request(ColorEndpoints.COLOR_UPDATE.url(pk), {
            method: ColorEndpoints.COLOR_UPDATE.method,
            data: formData,
            csrfToken: true
        });
    }
    static deleteColor(pk) {
        return this.request(ColorEndpoints.COLOR_DELETE.url(pk), {
            method: ColorEndpoints.COLOR_DELETE.method,
            csrfToken: true
        });
    }
}

export { ColorFetcher };