import { Fetcher } from './fetcher.js';
import { CLIENT_CC_CREATE_API } from '../endpoints/clients_cc_endpoints.js';
import { ClientCCEndpoints } from '../endpoints/clients_cc_endpoints.js';

export class ClientCCFetcher {
    static createMovement(data) {
        return Fetcher.request(CLIENT_CC_CREATE_API, {
            method: 'POST',
            data: data,
            csrfToken: true
        }).then(response => response.json());
    }

    static deleteMovement(pk) {
        return Fetcher.request(ClientCCEndpoints.CLIENT_CC_DELETE.url(pk), {
            method: ClientCCEndpoints.CLIENT_CC_DELETE.method,
            csrfToken: true
        }).then(response => response.json());
    }
} 