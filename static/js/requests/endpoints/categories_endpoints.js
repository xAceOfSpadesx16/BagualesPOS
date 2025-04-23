const CategoryEndpoints = Object.freeze({
    CATEGORY_CREATE_FORM: Object.freeze({
        method: 'GET',
        url: '/administracion/categorias/create/'
    }),
    CATEGORY_CREATE: Object.freeze({
        method: 'POST',
        url: '/administracion/categorias/create/',
        body: (formData) => formData
    }),
    CATEGORY_UPDATE_FORM: Object.freeze({
        method: 'GET',
        url: (pk) => `/administracion/categorias/update/${pk}/`
    }),
    CATEGORY_UPDATE: Object.freeze({
        method: 'POST',
        url: (pk) => `/administracion/categorias/update/${pk}/`,
        body: (formData) => formData
    }),
    CATEGORY_DELETE: Object.freeze({
        method: 'DELETE',
        url: (pk) => `/administracion/categorias/delete/${pk}/`
    }),
});

export { CategoryEndpoints };