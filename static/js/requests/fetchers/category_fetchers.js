import { Fetcher } from "./fetcher.js";

import { CategoryEndpoints } from "../endpoints/categories_endpoints.js";

class CategoryFetcher extends Fetcher {

    static getCreateForm() {
        return this.request(CategoryEndpoints.CATEGORY_CREATE_FORM.url);
    }

    static categoryCreate(data) {
        return this.request(CategoryEndpoints.CATEGORY_CREATE.url, {
            method: CategoryEndpoints.CATEGORY_CREATE.method,
            data: CategoryEndpoints.CATEGORY_CREATE.body(data),
            csrfToken: true
        });
    }

    static categoryUpdateForm(id) {
        return this.request(CategoryEndpoints.CATEGORY_UPDATE_FORM.url(id));
    }

    static categoryUpdate(id, data) {
        return this.request(CategoryEndpoints.CATEGORY_UPDATE.url(id), {
            method: CategoryEndpoints.CATEGORY_UPDATE.method,
            data: CategoryEndpoints.CATEGORY_UPDATE.body(data),
            csrfToken: true
        });
    }

    static categoryDelete(id) {
        return this.request(CategoryEndpoints.CATEGORY_DELETE.url(id), {
            method: CategoryEndpoints.CATEGORY_DELETE.method,
            csrfToken: true
        });
    }
}

export { CategoryFetcher };