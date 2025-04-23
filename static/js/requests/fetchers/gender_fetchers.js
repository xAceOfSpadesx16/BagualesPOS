import { Fetcher } from "./fetcher.js";

import { GenderEndpoints } from "../endpoints/genders_endpoints.js";

class GenderFetcher extends Fetcher {
    static getGenderCreateForm() {
        return this.request(GenderEndpoints.GENDER_CREATE_FORM.url);
    };
    static createGender(formData) {
        return this.request(GenderEndpoints.GENDER_CREATE.url, {
            method: GenderEndpoints.GENDER_CREATE.method,
            data: GenderEndpoints.GENDER_CREATE.body(formData),
            csrfToken: true
        });
    };
    static getGenderUpdateForm(pk) {
        return this.request(GenderEndpoints.GENDER_UPDATE_FORM.url(pk));
    };
    static updateGender(pk, formData) {
        return this.request(GenderEndpoints.GENDER_UPDATE.url(pk), {
            method: GenderEndpoints.GENDER_UPDATE.method,
            data: GenderEndpoints.GENDER_UPDATE.body(formData),
            csrfToken: true
        });
    };
    static deleteGender(pk) {
        return this.request(GenderEndpoints.GENDER_DELETE.url(pk), {
            method: GenderEndpoints.GENDER_DELETE.method,
            csrfToken: true,
        });
    };
}

export { GenderFetcher };