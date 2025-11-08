import { ClientFetcher } from "./requests/fetchers/client_fetchers.js";
import { saveObject } from "./admin/admin_utils.js";
import { Modal } from "./modal.js";


document.addEventListener('click', (e) => {

    const target = e.target;

    if (target.closest('#new-object-button')) {
        ClientFetcher.clientGetCreateForm()
            .then(data => data.text())
            .then(html => {
                const saveClient = (e) => saveObject(e, formData => ClientFetcher.clientCreate(formData));
                const modal = new Modal({
                    title: 'Crear Cliente',
                    content: html,
                    onSubmit: saveClient,
                    requireCloseConfirmation: true,
                });
                modal.openModal();
            }).catch(error => {
                console.error(error);
            });
    }


    else if (target.closest('.view-btn')) {
        const button = target.closest('.view-btn');
        const url = button.dataset.url;
        if (!url) return console.error('Falta data-url en .view-btn');

        window.location.href = url;
    }

    else if (target.closest('.edit-btn')) {
        const button = target.closest('.edit-btn');
        const clientId = button.dataset.objectId;

        ClientFetcher.clientUpdateForm(clientId)
            .then(data => data.text())
            .then(html => {
                const updateClient = (e) => saveObject(e, (id, formData) => ClientFetcher.clientUpdate(id, formData));
                const modal = new Modal({
                    title: 'Editar Cliente',
                    content: html,
                    onSubmit: updateClient,
                    requireCloseConfirmation: true,
                    confirmButtonDataAttr: { 'data-object-id': clientId }
                });
                modal.openModal();
            })
            .catch(error => {
                console.error(error);
            });
    }

    else if (target.closest('.client-action')) {
        const button = target.closest('.client-action');
        const clientId = button.dataset.objectId;
        const action = button.dataset.action;

        if (!clientId) return console.error('Falta data-object-id en .client-action');
        if (!action) return console.error('Falta data-action en .client-action');

        const ACTIONS = {
            delete: ClientFetcher.clientSoftDelete.bind(ClientFetcher),
            restore: ClientFetcher.clientRestore.bind(ClientFetcher),
        };
        const fetcherFunct = ACTIONS[action];
        if (!fetcherFunct) return console.error('Acción no soportada:', action);

        if (action === 'delete' && !confirm('¿Eliminar cliente?')) return;

        button.disabled = true;

        fetcherFunct(clientId).then(response => {
            if (response.redirected) {
                window.location.assign(response.url);
            }
            else {
                alert("Error inesperado: " + response.status);
                throw new Error("Error inesperado: " + response.status);
            }
        }).catch(error => {
            console.error("Error en fetch:", error);
        }).finally(() => {
            button.disabled = false;
        });
    }

});
