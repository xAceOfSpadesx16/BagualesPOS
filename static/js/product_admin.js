// import { ProductsFetcher } from "./requests/fetchers";

import { Modal } from "./modal.js";

const modal = new Modal();


document.addEventListener('click', (e) => {
    const target = e.target;
    if (target.closest('#abrir_modal')) {
        modal.updateModal('Nuevo producto', 'Supuesto formulario', () => { }, () => { });
        modal.openModal();
    };

});