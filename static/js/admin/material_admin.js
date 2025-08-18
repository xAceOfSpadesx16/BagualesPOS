import { MaterialFetcher } from "../requests/fetchers/material_fetchers.js";
import { Modal } from "../modal.js";
import { saveObject, deleteObject } from "./admin_utils.js";


document.addEventListener('click', (e) => {
    const target = e.target;
    if (target.closest('#new-object-button')) {
        MaterialFetcher.getCreateForm().then(data => {
            data.text().then(html => {
                const saveMaterial = (e) => saveObject(e, formData => MaterialFetcher.createMaterial(formData));
                const modal = new Modal({ title: 'Nuevo Material', content: html, onSubmit: saveMaterial, requireCloseConfirmation: true });
                modal.openModal();
            })
        }).catch(error => {
            console.error(error);
        });
    };

    if (target.closest('.edit-btn')) {
        const button = target.closest('.edit-btn');
        const materialId = button.dataset.objectId;

        MaterialFetcher.getUpdateForm(materialId).then(data => {
            data.text().then(html => {
                const updateMaterial = (e) => saveObject(e, (id, formData) => MaterialFetcher.updateMaterial(id, formData));
                const modal = new Modal({ title: 'Editar Material', content: html, onSubmit: updateMaterial, requireCloseConfirmation: true, confirmButtonDataAttr: { 'data-object-id': materialId } });
                modal.openModal();
            })
        }).catch(error => {
            console.error(error);
        });
    };

    if (target.closest('.delete-btn')) {
        deleteObject(e, (id) => MaterialFetcher.deleteMaterial(id));
    };
});