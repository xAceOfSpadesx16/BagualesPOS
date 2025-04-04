import { ProductsFetcher } from "./requests/fetchers.js";

import { Modal } from "./modal.js";

async function saveProduct(e) {
    e.preventDefault();
    const form = e.target.closest('.modal-container').querySelector('form');
    if (!form) {
        console.error("No se encontró el formulario.");
        return Promise.resolve(false);
    }

    const formData = new FormData(form);

    return ProductsFetcher.productCreate(formData)
        .then(response => {
            if (response.ok) {
                response.json().then(data => {
                    window.location.href = data.redirect_url;
                })
            } else {
                return response.text().then(html => {
                    Modal.updateContent(html);
                    return false;
                });
            }
        })
        .catch(error => {
            console.error("Error en fetch:", error);
            return false;
        });
}

document.addEventListener('click', (e) => {
    const target = e.target;
    if (target.closest('#new-product-button')) {
        ProductsFetcher.productFormGET().then(data => {
            data.text().then(html => {
                const modal = new Modal({ title: 'Nuevo producto', content: html, onSubmit: saveProduct, requireCloseConfirmation: true });
                modal.openModal();
            })
        }).catch(error => {
            console.error(error);
        });

    };

});