import { ProductsFetcher } from "../requests/fetchers/product_fetcher.js";

import { Modal } from "../modal.js";
import { saveObject, deleteObject } from "./admin_utils.js";

document.addEventListener('click', (e) => {
    const target = e.target;

    if (target.closest('#new-object-button')) {
        ProductsFetcher.productFormGET().then(data => {
            const saveProduct = (e) => saveObject(e, formData => ProductsFetcher.productCreate(formData));
            data.text().then(html => {
                const modal = new Modal({ title: 'Nuevo producto', content: html, onSubmit: saveProduct, requireCloseConfirmation: true });
                modal.openModal();
            })
        }).catch(error => {
            console.error(error);
        });
    }


    else if (target.closest('.edit-btn')) {
        const button = target.closest('.edit-btn');
        const productId = button.dataset.objectId;

        ProductsFetcher.productUpdateForm(productId).then(data => {
            data.text().then(html => {
                const updateProduct = (e) => saveObject(e, (id, formData) => ProductsFetcher.productUpdate(id, formData));
                const modal = new Modal({ title: 'Editar producto', content: html, onSubmit: updateProduct, requireCloseConfirmation: true, confirmButtonDataAttr: { 'data-object-id': productId } });
                modal.openModal();
            })
        }).catch(error => {
            console.error(error);
        });
    }


    else if (target.closest('.delete-btn')) {
        deleteObject(e, (id) => ProductsFetcher.productDelete(id));
    }


});