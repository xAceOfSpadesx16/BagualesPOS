const MaterialEndpoints = Object.freeze({
    MATERIAL_CREATE_FORM: Object.freeze({
        method: 'GET',
        url: '/administracion/materiales/create/'
    }),
    MATERIAL_CREATE: Object.freeze({
        method: 'POST',
        url: '/administracion/materiales/create/',
        body: (formData) => formData
    }),
    MATERIAL_UPDATE_FORM: Object.freeze({
        method: 'GET',
        url: (pk) => `/administracion/materiales/update/${pk}/`
    }),
    MATERIAL_UPDATE: Object.freeze({
        method: 'POST',
        url: (pk) => `/administracion/materiales/update/${pk}/`,
        body: (formData) => formData
    }),
    MATERIAL_DELETE: Object.freeze({
        method: 'DELETE',
        url: (pk) => `/administracion/materiales/delete/${pk}/`
    }),
});

export { MaterialEndpoints };