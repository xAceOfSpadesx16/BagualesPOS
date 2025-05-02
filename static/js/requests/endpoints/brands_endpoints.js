
const BrandEndpoints = Object.freeze({
    BRAND_CREATE_FORM: Object.freeze({
        method: 'GET',
        url: '/administracion/marcas/create/'
    }),
    BRAND_CREATE: Object.freeze({
        method: 'POST',
        url: '/administracion/marcas/create/',
        body: (formData) => formData
    }),
    BRAND_UPDATE_FORM: Object.freeze({
        method: 'GET',
        url: (pk) => `/administracion/marcas/update/${pk}/`
    }),
    BRAND_UPDATE: Object.freeze({
        method: 'POST',
        url: (pk) => `/administracion/marcas/update/${pk}/`,
        body: (formData) => formData
    }),
    BRAND_DELETE: Object.freeze({
        method: 'DELETE',
        url: (pk) => `/administracion/marcas/delete/${pk}/`
    }),
});

export { BrandEndpoints };