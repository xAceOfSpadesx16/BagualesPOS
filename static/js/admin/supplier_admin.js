import { SupplierFetcher } from "../requests/fetchers/supplier_fetchers.js";

import { Modal } from "../modal.js";
import { saveObject, deleteObject } from "./admin_utils.js";


document.addEventListener('click', (e) => {
    const target = e.target;
    if (target.closest('#new-object-button')) {
        SupplierFetcher.getCreateForm().then(data => {
            data.text().then(html => {
                const saveSupplier = (e) => saveObject(e, formData => SupplierFetcher.createSupplier(formData));
                const modal = new Modal({ title: 'Nuevo Proveedor', content: html, onSubmit: saveSupplier, requireCloseConfirmation: true });
                modal.openModal();
            })
        }).catch(error => {
            console.error(error);
        });
    };

    if (target.closest('.edit-btn')) {
        const button = target.closest('.edit-btn');
        const supplierId = button.dataset.objectId;

        SupplierFetcher.getUpdateForm(supplierId).then(data => {
            data.text().then(html => {
                const updateSupplier = (e) => saveObject(e, (id, formData) => SupplierFetcher.updateSupplier(id, formData));
                const modal = new Modal({ title: 'Editar Proveedor', content: html, onSubmit: updateSupplier, requireCloseConfirmation: true, confirmButtonDataAttr: { 'data-object-id': supplierId } });
                modal.openModal();
            })
        }).catch(error => {
            console.error(error);
        });
    };

    if (target.closest('.delete-btn')) {
        deleteObject(e, (id) => SupplierFetcher.deleteSupplier(id));
    };
});