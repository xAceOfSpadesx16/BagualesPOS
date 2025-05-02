const SeasonEndpoints = Object.freeze({
    SEASON_CREATE_FORM: Object.freeze({
        method: 'GET',
        url: '/administracion/temporadas/create/'
    }),
    SEASON_CREATE: Object.freeze({
        method: 'POST',
        url: '/administracion/temporadas/create/',
        body: (formData) => formData
    }),
    SEASON_UPDATE_FORM: Object.freeze({
        method: 'GET',
        url: (pk) => `/administracion/temporadas/update/${pk}/`
    }),
    SEASON_UPDATE: Object.freeze({
        method: 'POST',
        url: (pk) => `/administracion/temporadas/update/${pk}/`,
        body: (formData) => formData
    }),
    SEASON_DELETE: Object.freeze({
        method: 'DELETE',
        url: (pk) => `/administracion/temporadas/delete/${pk}/`
    }),
});

export { SeasonEndpoints };