import { Fetcher } from "./fetcher.js";

import { SeasonEndpoints } from "../endpoints/seasons_endpoints.js";

class SeasonFetcher extends Fetcher {

    static getCreateForm() {
        return Fetcher.request(SeasonEndpoints.SEASON_CREATE_FORM.url, {
            method: SeasonEndpoints.SEASON_CREATE_FORM.method
        });
    };

    static createSeason(formData) {
        return Fetcher.request(SeasonEndpoints.SEASON_CREATE.url, {
            method: SeasonEndpoints.SEASON_CREATE.method,
            data: SeasonEndpoints.SEASON_CREATE.body(formData),
            csrfToken: true
        });
    };

    static getUpdateForm(pk) {
        return Fetcher.request(SeasonEndpoints.SEASON_UPDATE_FORM.url(pk), {
            method: SeasonEndpoints.SEASON_UPDATE_FORM.method
        });
    };

    static updateSeason(pk, formData) {
        return Fetcher.request(SeasonEndpoints.SEASON_UPDATE.url(pk), {
            method: SeasonEndpoints.SEASON_UPDATE.method,
            data: SeasonEndpoints.SEASON_UPDATE.body(formData),
            csrfToken: true
        });
    };

    static deleteSeason(pk) {
        return Fetcher.request(SeasonEndpoints.SEASON_DELETE.url(pk), {
            method: SeasonEndpoints.SEASON_DELETE.method,
            csrfToken: true
        });
    };
};

export { SeasonFetcher };