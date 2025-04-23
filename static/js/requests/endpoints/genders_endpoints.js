const GenderEndpoints = Object.freeze({
    GENDER_CREATE_FORM: Object.freeze({
        method: 'GET',
        url: '/administracion/generos/create/'
    }),
    GENDER_CREATE: Object.freeze({
        method: 'POST',
        url: '/administracion/generos/create/',
        body: (formData) => formData
    }),
    GENDER_UPDATE_FORM: Object.freeze({
        method: 'GET',
        url: (pk) => `/administracion/generos/update/${pk}/`
    }),
    GENDER_UPDATE: Object.freeze({
        method: 'POST',
        url: (pk) => `/administracion/generos/update/${pk}/`,
        body: (formData) => formData
    }),
    GENDER_DELETE: Object.freeze({
        method: 'DELETE',
        url: (pk) => `/administracion/generos/delete/${pk}/`
    }),
});

export { GenderEndpoints };