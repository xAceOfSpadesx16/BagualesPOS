import { CategoryFetcher } from "../requests/fetchers/category_fetchers.js";
import { Modal } from "../modal.js";
import { saveObject, updateObject, deleteObject } from "./admin_utils.js";


document.addEventListener('click', (e) => {
    const target = e.target;
    if (target.closest('#new-object-button')) {

        CategoryFetcher.getCreateForm().then(data => {
            data.text().then(html => {
                const saveCategory = (e) => saveObject(e, formData => CategoryFetcher.categoryCreate(formData));
                const modal = new Modal({ title: 'Nueva Categoria', content: html, onSubmit: saveCategory, requireCloseConfirmation: true });
                modal.openModal();
            })
        }).catch(error => {
            console.error(error);
        });
    };

    if (target.closest('.edit-btn')) {

        const button = target.closest('.edit-btn');

        const categoryId = button.getAttribute('data-object-id');


        CategoryFetcher.categoryUpdateForm(categoryId).then(data => {
            data.text().then(html => {
                const updateCategory = (e) => updateObject(e, (id, formData) => CategoryFetcher.categoryUpdate(id, formData));
                const modal = new Modal({ title: 'Editar Marca', content: html, onSubmit: updateCategory, requireCloseConfirmation: true, confirmButtonDataAttr: { 'data-object-id': categoryId } });
                modal.openModal();
            })
        }).catch(error => {
            console.error(error);
        });
    };

    if (target.closest('.delete-btn')) {
        deleteObject(e, (id) => CategoryFetcher.categoryDelete(id));
    }

})