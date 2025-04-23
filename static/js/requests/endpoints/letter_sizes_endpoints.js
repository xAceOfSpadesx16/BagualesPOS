const LetterSizeEndpoints = Object.freeze({
    LETTER_SIZE_CREATE_FORM: Object.freeze({
        method: 'GET',
        url: '/administracion/talles/create/'
    }),
    LETTER_SIZE_CREATE: Object.freeze({
        method: 'POST',
        url: '/administracion/talles/create/',
        body: (formData) => formData
    }),
    LETTER_SIZE_UPDATE_FORM: Object.freeze({
        method: 'GET',
        url: (pk) => `/administracion/talles/update/${pk}/`
    }),
    LETTER_SIZE_UPDATE: Object.freeze({
        method: 'POST',
        url: (pk) => `/administracion/talles/update/${pk}/`,
        body: (formData) => formData
    }),
    LETTER_SIZE_DELETE: Object.freeze({
        method: 'DELETE',
        url: (pk) => `/administracion/talles/delete/${pk}/`
    })
});

export { LetterSizeEndpoints }