import { Fetcher } from "./fetcher.js";

import { MaterialEndpoints } from "../endpoints/materials_endpoints.js";

class MaterialFetcher extends Fetcher {

    static getCreateForm() {
        return this.request(MaterialEndpoints.MATERIAL_CREATE_FORM.url, {
            method: MaterialEndpoints.MATERIAL_CREATE_FORM.method
        });
    }

    static createMaterial(formData) {
        return this.request(MaterialEndpoints.MATERIAL_CREATE.url, {
            method: MaterialEndpoints.MATERIAL_CREATE.method,
            data: MaterialEndpoints.MATERIAL_CREATE.body(formData),
            csrfToken: true
        });
    };

    static getUpdateForm(id) {
        return this.request(MaterialEndpoints.MATERIAL_UPDATE_FORM.url(id), {
            method: MaterialEndpoints.MATERIAL_UPDATE_FORM.method
        });
    };

    static updateMaterial(id, formData) {
        return this.request(MaterialEndpoints.MATERIAL_UPDATE.url(id), {
            method: MaterialEndpoints.MATERIAL_UPDATE.method,
            data: MaterialEndpoints.MATERIAL_UPDATE.body(formData),
            csrfToken: true
        });
    };

    static deleteMaterial(id) {
        return this.request(MaterialEndpoints.MATERIAL_DELETE.url(id), {
            method: MaterialEndpoints.MATERIAL_DELETE.method,
            csrfToken: true
        });
    };
};

export { MaterialFetcher };