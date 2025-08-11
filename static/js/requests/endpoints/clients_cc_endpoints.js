const ClientCCEndpoints = Object.freeze({
    CLIENT_CC_CREATE: Object.freeze({
        method: 'POST',
        url: '/clients/cc/api/create/',
        body: (data) => data,
        csrf: true
    }),
    CLIENT_CC_DELETE: Object.freeze({
        method: 'DELETE',
        url: (pk) => `/clients/cc/api/delete/${pk}/`,
        csrf: true
    }),
});

export { ClientCCEndpoints }
