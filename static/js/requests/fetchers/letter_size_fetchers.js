import { Fetcher } from "./fetcher.js";

import { LetterSizeEndpoints } from "../endpoints/letter_sizes_endpoints.js";

class LetterSizeFetcher extends Fetcher {
    static getCreateForm() {
        return this.request(LetterSizeEndpoints.LETTER_SIZE_CREATE_FORM.url, {
            method: LetterSizeEndpoints.LETTER_SIZE_CREATE_FORM.method,
        });
    };

    static createLetterSize(formData) {
        return this.request(LetterSizeEndpoints.LETTER_SIZE_CREATE.url, {
            method: LetterSizeEndpoints.LETTER_SIZE_CREATE.method,
            data: LetterSizeEndpoints.LETTER_SIZE_CREATE.body(formData),
            csrfToken: true
        });
    };

    static getUpdateForm(pk) {
        return this.request(LetterSizeEndpoints.LETTER_SIZE_UPDATE_FORM.url(pk), {
            method: LetterSizeEndpoints.LETTER_SIZE_UPDATE_FORM.method,
        });
    };

    static updateLetterSize(pk, formData) {
        return this.request(LetterSizeEndpoints.LETTER_SIZE_UPDATE.url(pk), {
            method: LetterSizeEndpoints.LETTER_SIZE_UPDATE.method,
            data: LetterSizeEndpoints.LETTER_SIZE_UPDATE.body(formData),
            csrfToken: true
        });
    };

    static deleteLetterSize(pk) {
        return this.request(LetterSizeEndpoints.LETTER_SIZE_DELETE.url(pk), {
            method: LetterSizeEndpoints.LETTER_SIZE_DELETE.method,
            csrfToken: true,
        });
    };
}

export { LetterSizeFetcher };