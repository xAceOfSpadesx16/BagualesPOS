import { SeasonFetcher } from "../requests/fetchers/season_fetchers.js";

import { Modal } from "../modal.js";
import { saveObject, deleteObject } from "./admin_utils.js";


document.addEventListener('click', (e) => {
    const target = e.target;

    if (target.closest('#new-object-button')) {
        SeasonFetcher.getCreateForm().then(data => {
            data.text().then(html => {
                const saveSeason = (e) => saveObject(e, formData => SeasonFetcher.createSeason(formData));
                const modal = new Modal({ title: 'Nuevo Temporada', content: html, onSubmit: saveSeason, requireCloseConfirmation: true });
                modal.openModal();
            })
        }).catch(error => {
            console.error(error);
        });
    };

    if (target.closest('.edit-btn')) {
        const button = target.closest('.edit-btn');
        const seasonId = button.dataset.objectId;

        SeasonFetcher.getUpdateForm(seasonId).then(data => {
            data.text().then(html => {
                const updateSeason = (e) => saveObject(e, (id, formData) => SeasonFetcher.updateSeason(id, formData));
                const modal = new Modal({ title: 'Editar Temporada', content: html, onSubmit: updateSeason, requireCloseConfirmation: true, confirmButtonDataAttr: { 'data-object-id': seasonId } });
                modal.openModal();
            })
        }).catch(error => {
            console.error(error);
        });
    };

    if (target.closest('.delete-btn')) {
        deleteObject(e, (id) => SeasonFetcher.deleteSeason(id));
    };
})