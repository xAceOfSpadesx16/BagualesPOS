


class Modal {
    static isOpen = false;

    /**
     * @param {string} [title='Titulo por defecto'] - Título del modal.
     * @param {string} [content='Contenido por defecto'] - Contenido del modal en formato HTML.
     * @param {Function} [onSubmitCallback=() => {}] - Callback al confirmar el modal.
     * @param {Function} [onCloseCallback=() => {}] - Callback al cerrar el modal.
     * @param {string} [modalSelector='#modal'] - Selector del modal en el DOM.
     * @param {string} [titleSelector='.modal-container-title'] - Selector del título del modal.
     * @param {string} [contentSelector='.modal-container-body'] - Selector del contenido del modal.
     * @param {string} [submitSelector='#confirm_modal'] - Selector del botón de confirmación.
     * @param {string} [closeSelector='#close_modal'] - Selector del botón de cierre.
     * @param {string} [modalXCloseSelector='#modal_x_close'] - Selector del botón "X" para cerrar.
     */

    constructor({
        title = '',
        content = '',
        onSubmitCallback = () => { },
        onCloseCallback = () => { },
        modalSelector = '#modal',
        titleSelector = '.modal-container-title',
        contentSelector = '.modal-container-body',
        submitSelector = '#confirm_modal',
        closeSelector = '#close_modal',
        modalXCloseSelector = '#modal_x_close',
    } = {}) {
        this.modalElement = document.querySelector(modalSelector);

        if (!this.modalElement) {
            throw new Error('No se encuentró el modal en el DOM');
        }

        this.titleElement = this.modalElement.querySelector(titleSelector);
        this.contentElement = this.modalElement.querySelector(contentSelector);

        this.submitButton = this.modalElement.querySelector(submitSelector);
        this.cancelButton = this.modalElement.querySelector(closeSelector);
        this.closeXButton = this.modalElement.querySelector(modalXCloseSelector);

        this.#validateElements();

        this.title = title;
        this.content = content;

        this.onSubmitCallback = onSubmitCallback;
        this.onCloseCallback = onCloseCallback;

        this.submitListener = this.closeModal.bind(this, this.onSubmitCallback);
        this.closeListener = this.closeModal.bind(this, this.onCloseCallback);
        this.boundBackdropListener = this.#backdropListener.bind(this);

        this.addOnSubmitClick();

        this.addOnCloseClick();
    };

    #validateElements() {
        const missingElements = [];

        if (!this.titleElement) missingElements.push('titleElement');
        if (!this.contentElement) missingElements.push('contentElement');
        if (!this.submitButton) missingElements.push('submitButton');
        if (!this.cancelButton) missingElements.push('cancelButton');
        if (!this.closeXButton) missingElements.push('closeXButton');

        if (missingElements.length > 0) {
            throw new Error(`No se encontraron los siguientes elementos dentro del modal: ${missingElements.join(', ')}`);
        }
    }

    openModal() {
        if (Modal.isOpen) return;
        Modal.isOpen = true;

        // se añade la clase show y lo que produce un transition de css
        this.modalElement.classList.add('show');

    };

    closeModal(callback = null) {
        if (!Modal.isOpen) return;

        // se ejecuta el callback si existe
        callback?.();

        // fadeout del modal
        this.modalElement.classList.remove('show');

        // se agrega un listener para cuando termine la transicion de fadeOut
        this.modalElement.addEventListener('transitionend', () => {

            // limpieza de eventos
            this.removeEvents();

            // limpieza de modal
            this.#clearModal();

        }, { once: true }); // once true para que se ejecute una sola vez y luego se elimine el listener

        Modal.isOpen = false;
    };


    addOnSubmitClick() {
        this.submitButton.addEventListener('click', this.submitListener);
    };


    addOnCloseClick() {
        this.cancelButton.addEventListener('click', this.closeListener);
        this.closeXButton.addEventListener('click', this.closeListener);
        this.modalElement.addEventListener('click', this.boundBackdropListener);
    };


    removeEvents() {
        this.submitButton.removeEventListener('click', this.submitListener);
        this.cancelButton.removeEventListener('click', this.closeListener);
        this.closeXButton.removeEventListener('click', this.closeListener);
        this.modalElement.removeEventListener('click', this.boundBackdropListener);
    };


    #clearModal() {
        // limpieza de modal
        this.titleElement.textContent = '';
        this.contentElement.innerHTML = '';
    };

    #backdropListener(event) {
        if (event.target === this.modalElement) {
            this.closeListener();
        }
    }

    /**
     * 
     * @param {string} title Titulo
     * @param {string} content Contenido en formato HTML
     * 
     */
    #updateContent(title, content) {
        this.title = title;
        this.content = content;

        // actualización de contenido del modal
        this.titleElement.textContent = this.title;
        this.contentElement.innerHTML = this.content;
    }

    /**
     * 
     * @param {Function} onSubmitCallback Callback al confirmar el modal
     * @param {Function} onCloseCallback Callback al cerrar el modal
     */
    #updateCallbacks(onSubmitCallback, onCloseCallback) {
        this.onSubmitCallback = onSubmitCallback;
        this.onCloseCallback = onCloseCallback;

        this.addOnSubmitClick();
        this.addOnCloseClick();
    }

    /**
     * 
     * @param {string} title Titulo
     * @param {string} content Contenido en formato HTML
     * @param {Function} onSubmitCallback Callback al confirmar el modal
     * @param {Function} onCloseCallback Callback al cerrar el modal
     */
    updateModal(title, content, onSubmitCallback, onCloseCallback) {
        this.#updateContent(title, content);
        this.#updateCallbacks(onSubmitCallback, onCloseCallback);
    }

};

export { Modal };