import { ProductsFetcher } from "./requests/fetchers.js";

import { Modal } from "./modal.js";

const modal = new Modal();


document.addEventListener('click', (e) => {
    const target = e.target;
    if (target.closest('#abrir_modal')) {
        ProductsFetcher.productFormGET().then(data => {
            modal.updateModal('Nuevo producto', data, () => { }, () => { });
            modal.openModal();
        }).catch(error => {
            console.error(error);
        });
    };

});