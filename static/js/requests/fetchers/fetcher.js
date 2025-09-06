import { getCookie } from "../../utils.js";

class Fetcher {
    /**
     * Método centralizado para hacer fetch.
     * @param {string} url - La URL del endpoint.
     * @param {Object} options - Opciones de la petición.
     * @param {string} [options.method='GET'] - Método HTTP.
     * @param {Object|null} [options.data=null] - Datos a enviar.
     * @param {boolean} [options.csrfToken=false] - Token CSRF.
     * @returns {Promise} - Se retorna una promesa.
     */
    static request(url, { method = 'GET', data = null, csrfToken = false } = {}) {

        const headers = new Headers();
        let body = data;

        if (data && !(data instanceof FormData)) {
            headers.append('Content-Type', 'application/json');
            body = JSON.stringify(data);
        }

        if (csrfToken) {
            headers.append('X-CSRFToken', getCookie('csrftoken'));
        }

        headers.append('X-Requested-With', 'XMLHttpRequest');

        const options = {
            method,
            headers,
            ...(body && { body })
        };
        return fetch(url, options)
            .catch(error => {
                console.error("Error en la petición:", error);
                throw error;
            });
    }
}

export { Fetcher };