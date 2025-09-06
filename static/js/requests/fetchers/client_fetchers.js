import { Fetcher } from "./fetcher.js";
import { ClientEndpoints } from "../endpoints/clients_endpoints.js";

class ClientFetcher extends Fetcher {

    // Client Endpoints
    static clientGetCreateForm() {
        return this.request(ClientEndpoints.CLIENT_CREATE_FORM.url, {
            method: ClientEndpoints.CLIENT_CREATE_FORM.method,
        });
    };

    static clientCreate(data) {
        return this.request(ClientEndpoints.CLIENT_CREATE.url, {
            method: ClientEndpoints.CLIENT_CREATE.method,
            data: ClientEndpoints.CLIENT_CREATE.body(data),
            csrfToken: true
        });
    };

    static clientUpdateForm(pk) {
        return this.request(ClientEndpoints.CLIENT_UPDATE_FORM.url(pk), {
            method: ClientEndpoints.CLIENT_UPDATE_FORM.method
        });
    };

    static clientUpdate(pk, data) {
        return this.request(ClientEndpoints.CLIENT_UPDATE.url(pk), {
            method: ClientEndpoints.CLIENT_UPDATE.method,
            data: ClientEndpoints.CLIENT_UPDATE.body(data),
            csrfToken: true
        });
    };

    static clientSoftDelete(pk) {
        return this.request(ClientEndpoints.CLIENT_DELETE.url(pk), {
            method: ClientEndpoints.CLIENT_DELETE.method,
            csrfToken: true
        });
    };

    static clientRestore(pk) {
        return this.request(ClientEndpoints.CLIENT_RESTORE.url(pk), {
            method: ClientEndpoints.CLIENT_RESTORE.method,
            csrfToken: true
        });
    };

    static clientList() {
        return this.request(ClientEndpoints.CLIENT_LIST.url, {
            method: ClientEndpoints.CLIENT_LIST.method
        });
    };

    static clientDetail(pk) {
        return this.request(ClientEndpoints.CLIENT_DETAIL.url(pk), {
            method: ClientEndpoints.CLIENT_DETAIL.method
        });
    };


    // Customer Account Endpoints
    static clientCCDetail(pk) {
        return this.request(ClientEndpoints.CLIENT_CC_DETAIL.url(pk), {
            method: ClientEndpoints.CLIENT_CC_DETAIL.method
        });
    };

    static clientCCSoftDelete(pk) {
        return this.request(ClientEndpoints.CLIENT_CC_SOFT_DELETE.url(pk), {
            method: ClientEndpoints.CLIENT_CC_SOFT_DELETE.method,
            csrfToken: true
        });
    };

    static clientCCUpdateForm(pk) {
        return this.request(ClientEndpoints.CLIENT_CC_UPDATE_FORM.url(pk), {
            method: ClientEndpoints.CLIENT_CC_UPDATE_FORM.method
        });
    };

    static clientCCUpdate(pk, data) {
        return this.request(ClientEndpoints.CLIENT_CC_UPDATE.url(pk), {
            method: ClientEndpoints.CLIENT_CC_UPDATE.method,
            data: ClientEndpoints.CLIENT_CC_UPDATE.body(data),
            csrfToken: true
        });
    };

    // Balance Record Endpoints
    static clientCCRecordDetail(pk) {
        return this.request(ClientEndpoints.CLIENT_CC_RECORD_DETAIL.url(pk), {
            method: ClientEndpoints.CLIENT_CC_RECORD_DETAIL.method
        });
    };

    static clientCCRecordCreate(data) {
        return this.request(ClientEndpoints.CLIENT_CC_RECORD_CREATE.url, {
            method: ClientEndpoints.CLIENT_CC_RECORD_CREATE.method,
            data: ClientEndpoints.CLIENT_CC_RECORD_CREATE.body(data),
            csrfToken: true
        });
    };


}

export { ClientFetcher };