import { ProductsFetcher } from "./requests/fetchers.js";

import { Modal } from "./modal.js";

function saveProduct(e) {
    e.preventDefault();
    const form = e.target.closest('.modal-container').querySelector('form');
    if (!form) return;

    const formData = new FormData(form);
    console.log(Object.fromEntries(formData.entries()));
    // ProductsFetcher.productCreate(formData).then(data => {
    //     console.log(data);

    // })
}


document.addEventListener('click', (e) => {
    const target = e.target;
    if (target.closest('#new-product-button')) {
        ProductsFetcher.productFormGET().then(data => {
            let modal = new Modal({ title: 'Nuevo producto', content: data, onSubmit: saveProduct });
            modal.openModal();
        }).catch(error => {
            console.error(error);
        });
    };

});