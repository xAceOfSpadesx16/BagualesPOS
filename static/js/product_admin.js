import { ProductsFetcher } from "./requests/fetchers.js";

import { Modal } from "./modal.js";


document.addEventListener('click', (e) => {
    const target = e.target;
    if (target.closest('#abrir_modal')) {
        ProductsFetcher.productFormGET().then(data => {
            let modal = new Modal({ title: 'Nuevo producto', content: data });
            modal.openModal();
        }).catch(error => {
            console.error(error);
        });
    };

});