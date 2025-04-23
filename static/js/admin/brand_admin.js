import { BrandFetcher } from "../requests/fetchers/brand_fetchers.js";
import { Modal } from "../modal.js";
import { saveObject, updateObject, deleteObject } from "./admin_utils.js";


document.addEventListener('click', (e) => {
    const target = e.target;
    if (target.closest('#new-object-button')) {

        BrandFetcher.getCreateForm().then(data => {
            data.text().then(html => {
                const saveBrand = (e) => saveObject(e, formData => BrandFetcher.brandCreate(formData));
                const modal = new Modal({ title: 'Nueva Marca', content: html, onSubmit: saveBrand, requireCloseConfirmation: true });
                modal.openModal();
            })
        }).catch(error => {
            console.error(error);
        });
    };

    if (target.closest('.edit-btn')) {

        const button = target.closest('.edit-btn');

        const brandId = button.getAttribute('data-object-id');


        BrandFetcher.brandUpdateForm(brandId).then(data => {
            data.text().then(html => {
                const updateBrand = (e) =>
                    updateObject(e, (id, formData) => BrandFetcher.brandUpdate(id, formData));
                const modal = new Modal({ title: 'Editar producto', content: html, onSubmit: updateBrand, requireCloseConfirmation: true, confirmButtonDataAttr: { 'data-object-id': brandId } });
                modal.openModal();
            })
        }).catch(error => {
            console.error(error);
        });
    };

    if (target.closest('.delete-btn')) {
        deleteObject(e, (id) => BrandFetcher.brandDelete(id));
    }

})