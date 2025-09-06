import { GenderFetcher } from "../requests/fetchers/gender_fetchers.js";
import { Modal } from "../modal.js";
import { saveObject, deleteObject } from "./admin_utils.js";


document.addEventListener('click', (e) => {
    const target = e.target;
    if (target.closest('#new-object-button')) {
        GenderFetcher.getGenderCreateForm().then(data => {
            data.text().then(html => {
                const saveGender = (e) => saveObject(e, formData => GenderFetcher.createGender(formData));
                const modal = new Modal({ title: 'Crear Genero', content: html, onSubmit: saveGender, requireCloseConfirmation: true });
                modal.openModal();
            })
        }).catch(error => {
            console.error(error);
        });
    };

    if (target.closest('.edit-btn')) {
        const button = target.closest('.edit-btn');
        const genderId = button.dataset.objectId;

        GenderFetcher.getGenderUpdateForm(genderId).then(data => {
            data.text().then(html => {
                const updateGender = (e) => saveObject(e, (id, formData) => GenderFetcher.updateGender(id, formData));
                const modal = new Modal({ title: 'Editar Genero', content: html, onSubmit: updateGender, requireCloseConfirmation: true, confirmButtonDataAttr: { 'data-object-id': genderId } });
                modal.openModal();
            })
        }).catch(error => {
            console.error(error);
        });
    };

    if (target.closest('.delete-btn')) {
        deleteObject(e, (id) => GenderFetcher.deleteGender(id));
    }
})