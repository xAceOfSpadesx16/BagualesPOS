
const ClientEndpoints = Object.freeze({
    // Client Endpoints
    CLIENT_CREATE_FORM: Object.freeze({
        method: 'GET',
        url: '/clientes/create/'
    }),
    CLIENT_CREATE: Object.freeze({
        method: 'POST',
        url: '/clientes/create/',
        body: (formData) => formData
    }),
    CLIENT_UPDATE_FORM: Object.freeze({
        method: 'GET',
        url: (pk) => `/clientes/update/${pk}/`
    }),
    CLIENT_UPDATE: Object.freeze({
        method: 'POST',
        url: (pk) => `/clientes/update/${pk}/`,
        body: (formData) => formData
    }),
    CLIENT_DELETE: Object.freeze({
        method: 'POST',
        url: (pk) => `/clientes/delete/${pk}/`
    }),

    CLIENT_LIST: Object.freeze({
        method: 'GET',
        url: '/clientes/',
    }),

    CLIENT_DETAIL: Object.freeze({
        method: 'GET',
        url: (pk) => `/clientes/${pk}/`
    }),

    CLIENT_RESTORE: Object.freeze({
        method: 'POST',
        url: (pk) => `/clientes/restore/${pk}/`
    }),

    // Customer Account Endpoints

    CLIENT_CC_DETAIL: Object.freeze({
        method: 'GET',
        url: (pk) => `/clientes/cc/${pk}/`,
    }),

    CLIENT_CC_UPDATE_FORM: Object.freeze({
        method: 'GET',
        url: (pk) => `/clientes/cc/${pk}/update/`
    }),

    CLIENT_CC_UPDATE: Object.freeze({
        method: 'POST',
        url: (pk) => `/clientes/cc/${pk}/update/`,
        body: (formData) => formData
    }),

    CLIENT_CC_SOFT_DELETE: Object.freeze({
        method: 'POST',
        url: (pk) => `/clientes/cc/${pk}/delete/`
    }),

    // Balance Record Endpoints
    CLIENT_CC_RECORD_DETAIL: Object.freeze({
        method: 'GET',
        url: (pk) => `/clientes/cc/record/${pk}/`,
    }),

    CLIENT_CC_RECORD_CREATE: Object.freeze({
        method: 'POST',
        url: '/clients/cc/record/create/',
        body: (formData) => formData
    }),

});

export { ClientEndpoints };