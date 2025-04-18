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
            console.log(response.ok)
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

async function updateProduct(e) {
    const button = e.target.closest('#confirm_modal');
    const form = e.target.closest('.modal-container').querySelector('form');
    if (!form) {
        console.error("No se encontró el formulario.");
        return Promise.resolve(false);
    }

    const formData = new FormData(form);
    const productId = button.getAttribute('data-product-id');

    return ProductsFetcher.productUpdate(productId, formData)
        .then(response => {
            const contentType = response.headers.get('Content-Type');
            if (contentType.toLowerCase().includes("application/json")) {
                response.json().then(data => {
                    window.location.href = data.redirect_url;
                })
            }
            if (contentType.toLowerCase().includes("text/html")) {
                response.text().then(html => {
                    Modal.updateContent(html);
                    return false;
                })
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

    if (target.closest('.delete-btn')) {
        const button = target.closest('.delete-btn');
        const productId = button.getAttribute('data-product-id');
        ProductsFetcher.productDelete(productId).then(response => response.json()).then(data => {
            const row = button.closest('tr');
            row.remove();
            // agregar dialogo de exito
        }).catch(error => {
            console.error(error);
        });
    };

    if (target.closest('.edit-btn')) {
        const button = target.closest('.edit-btn');
        const productId = button.getAttribute('data-product-id');
        ProductsFetcher.productUpdateForm(productId).then(data => {
            data.text().then(html => {
                const modal = new Modal({ title: 'Editar producto', content: html, onSubmit: updateProduct, requireCloseConfirmation: true, confirmButtonDataAttr: { 'data-product-id': productId } });
                modal.openModal();
            })
        }).catch(error => {
            console.error(error);
        });
    }


});