import { MaterialFetcher } from "../requests/fetchers/material_fetchers.js";
import { Modal } from "../modal.js";
import { saveObject, updateObject, deleteObject } from "./admin_utils.js";


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
        const materialId = button.getAttribute('data-object-id');
        MaterialFetcher.getUpdateForm(materialId).then(data => {
            data.text().then(html => {
                const updateMaterial = (e) => updateObject(e, (id, formData) => MaterialFetcher.updateMaterial(id, formData));
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