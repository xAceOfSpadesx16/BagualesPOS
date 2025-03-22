class Modal {

    constructor({
        title = 'Titulo por defecto',
        content = 'Contenido por defecto',
        onSubmitCallback = () => console.log('submit de modal'),
        onCloseCallback = () => console.log('close de modal'),
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
        // actualización de contenido del modal
        this.titleElement.textContent = this.title;
        this.contentElement.innerHTML = this.content;

        // se añade la clase show y lo que produce un transition de css
        this.modalElement.classList.add('show');

    };

    closeModal(callback = null) {

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
    };


    addOnSubmitClick() {
        this.submitButton.addEventListener('click', this.submitListener);
    };


    addOnCloseClick() {
        this.cancelButton.addEventListener('click', this.closeListener);
        this.closeXButton.addEventListener('click', this.closeListener);
    };


    removeEvents() {
        this.submitButton.removeEventListener('click', this.submitListener);
        this.cancelButton.removeEventListener('click', this.closeListener);
        this.closeXButton.removeEventListener('click', this.closeListener);
    };


    #clearModal() {
        // limpieza de modal
        this.titleElement.textContent = '';
        this.contentElement.innerHTML = '';
    };

};

export { Modal };