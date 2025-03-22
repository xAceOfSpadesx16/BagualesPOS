// import { ProductsFetcher } from "./requests/fetchers";

import { Modal } from "./modal.js";




document.addEventListener('click', (e) => {
    const target = e.target;
    if (target.closest('#abrir_modal')) {
        const modal = new Modal('Modal', 'Contenido del modal');
        modal.openModal();
    };

});