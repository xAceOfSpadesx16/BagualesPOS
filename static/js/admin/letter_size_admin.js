import { LetterSizeFetcher } from "../requests/fetchers/letter_size_fetchers.js";
import { Modal } from "../modal.js";
import { saveObject, deleteObject } from "./admin_utils.js";


document.addEventListener('click', (e) => {
    const target = e.target;
    if (target.closest('#new-object-button')) {
        LetterSizeFetcher.getCreateForm().then(data => {
            data.text().then(html => {
                const saveLetterSize = (e) => saveObject(e, formData => LetterSizeFetcher.createLetterSize(formData));
                const modal = new Modal({ title: 'Nuevo Talle', content: html, onSubmit: saveLetterSize, requireCloseConfirmation: true });
                modal.openModal();
            })
        }).catch(error => {
            console.error(error);
        });
    };

    if (target.closest('.edit-btn')) {
        const button = target.closest('.edit-btn');
        const letterSizeId = button.dataset.objectId;

        LetterSizeFetcher.getUpdateForm(letterSizeId).then(data => {
            data.text().then(html => {
                const updateLetterSize = (e) => saveObject(e, (id, formData) => LetterSizeFetcher.updateLetterSize(id, formData));
                const modal = new Modal({ title: 'Editar Talle', content: html, onSubmit: updateLetterSize, requireCloseConfirmation: true, confirmButtonDataAttr: { 'data-object-id': letterSizeId } });
                modal.openModal();
            })
        }).catch(error => {
            console.error(error);
        });
    };

    if (target.closest('.delete-btn')) {
        deleteObject(e, (id) => LetterSizeFetcher.deleteLetterSize(id));
    };
})