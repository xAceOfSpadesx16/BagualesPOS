const SupplierEndpoints = Object.freeze({
    SUPPLIER_CREATE_FORM: Object.freeze({
        method: 'GET',
        url: '/administracion/proveedores/create/'
    }),
    SUPPLIER_CREATE: Object.freeze({
        method: 'POST',
        url: '/administracion/proveedores/create/',
        body: (formData) => formData
    }),
    SUPPLIER_UPDATE_FORM: Object.freeze({
        method: 'GET',
        url: (pk) => `/administracion/proveedores/update/${pk}/`
    }),
    SUPPLIER_UPDATE: Object.freeze({
        method: 'POST',
        url: (pk) => `/administracion/proveedores/update/${pk}/`,
        body: (formData) => formData
    }),
    SUPPLIER_DELETE: Object.freeze({
        method: 'DELETE',
        url: (pk) => `/administracion/proveedores/delete/${pk}/`
    }),
})

export { SupplierEndpoints }