import { ColorFetcher } from "../requests/fetchers/color_fetchers.js";
import { Modal } from "../modal.js";
import { saveObject, updateObject, deleteObject } from "./admin_utils.js";


document.addEventListener('click', (e) => {
    const target = e.target;
    if (target.closest('#new-object-button')) {
        ColorFetcher.getCreateForm().then(data => {
            data.text().then(html => {
                const saveColor = (e) => saveObject(e, formData => ColorFetcher.createColor(formData));
                const modal = new Modal({ title: 'Nuevo Color', content: html, onSubmit: saveColor, requireCloseConfirmation: true });
                modal.openModal();
            })
        }).catch(error => {
            console.error(error);
        });
    }

    if (target.closest('.edit-btn')) {

        const button = target.closest('.edit-btn');

        const colorId = button.getAttribute('data-object-id');

        ColorFetcher.colorUpdateForm(colorId).then(data => {
            data.text().then(html => {
                const updateColor = (e) => updateObject(e, (id, formData) => ColorFetcher.updateColor(id, formData));
                const modal = new Modal({ title: 'Editar Color', content: html, onSubmit: updateColor, requireCloseConfirmation: true, confirmButtonDataAttr: { 'data-object-id': colorId } });
                modal.openModal();
            })
        }).catch(error => {
            console.error(error);
        });
    }

    if (target.closest('.delete-btn')) {
        deleteObject(e, (id) => ColorFetcher.deleteColor(id));
    }
})