const ColorEndpoints = Object.freeze({
    COLOR_CREATE_FORM: Object.freeze({
        method: 'GET',
        url: '/administracion/colores/create/'
    }),
    COLOR_CREATE: Object.freeze({
        method: 'POST',
        url: '/administracion/colores/create/',
        body: (formData) => formData
    }),
    COLOR_UPDATE_FORM: Object.freeze({
        method: 'GET',
        url: (pk) => `/administracion/colores/update/${pk}/`
    }),
    COLOR_UPDATE: Object.freeze({
        method: 'POST',
        url: (pk) => `/administracion/colores/update/${pk}/`,
        body: (formData) => formData
    }),
    COLOR_DELETE: Object.freeze({
        method: 'DELETE',
        url: (pk) => `/administracion/colores/delete/${pk}/`
    }),
});

export { ColorEndpoints }