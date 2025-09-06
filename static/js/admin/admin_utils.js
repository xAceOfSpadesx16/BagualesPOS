import { Modal } from "../modal.js";

async function saveObject(e, fetcherFunct) {
    e.preventDefault();
    const form = e.target.closest('.modal-container').querySelector('form');
    if (!form) {
        console.error("No se encontró el formulario.");
        return Promise.resolve(false);
    }

    const formData = new FormData(form);
    const button = e.target.closest('#confirm_modal');
    const objectId = button.dataset.objectId;

    const responsePromise = objectId
        ? fetcherFunct(objectId, formData)
        : fetcherFunct(formData);

    return responsePromise.then(response => {
        if (response.status === 422) {
            return response.text().then(html => {
                Modal.updateContent(html);
                return false;
            });
        }
        if (response.redirected) {
            window.location.assign(response.url);
            return;
        }
        else {
            alert("Error inesperado: " + response.status);
            throw new Error("Error inesperado: " + response.status);
        }
    })
        .catch(error => {
            console.error("Error en fetch:", error);
            return false;
        });
}


async function deleteObject(e, fetcherFunct) {
    const target = e.target;
    const button = target.closest('.delete-btn');
    const objectId = button.dataset.objectId;
    if (!objectId) {
        console.error("ID de objeto no encontrado.");
        return;
    }
    if (!confirm('¿Eliminar este objeto?')) return;
    button.disabled = true;

    return fetcherFunct(objectId).then(response => response.json()).then(data => {
        const row = button.closest('tr');
        row.remove();
    }).catch(error => {
        console.error(error);
    }).finally(() => {
        button.disabled = false;
    });
}

export { saveObject, deleteObject };